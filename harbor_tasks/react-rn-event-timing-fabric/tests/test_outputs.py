"""
Task: react-rn-event-timing-fabric
Repo: facebook/react @ aac12ce597b49093a5add54b00deee3d8980f874
PR:   35947

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = REPO + "/packages/react-native-renderer/src/ReactFiberConfigFabric.js"

# ---------------------------------------------------------------------------
# JS helper: extracts event-timing functions from the file, strips Flow types,
# and makes them callable.  Every behavioral test reuses this preamble.
# ---------------------------------------------------------------------------
_JS_PREAMBLE = r"""
const fs = require("fs");
const code = fs.readFileSync("TARGET_PATH", "utf8");
const lines = code.split("\n");

// Locate section: from trackSchedulerEvent to shouldAttemptEagerTransition
let start = -1, end = lines.length;
for (let i = 0; i < lines.length; i++) {
    if (start === -1 && /function\s+trackSchedulerEvent/.test(lines[i])) {
        start = i;
        // Include preceding variable declarations (up to 5 lines back)
        for (let j = i - 1; j >= Math.max(0, i - 5); j--) {
            const t = lines[j].trim();
            if (t === "" || t.startsWith("//")) continue;
            if (/^(let|const|var)\s/.test(t)) { start = j; break; }
            break;
        }
    }
    if (start !== -1 && /function\s+shouldAttemptEagerTransition/.test(lines[i])) {
        end = i; break;
    }
}
if (start === -1) { console.error("trackSchedulerEvent not found"); process.exit(1); }

let section = lines.slice(start, end).join("\n");

// Strip Flow type annotations
section = section
    .replace(/export\s+/g, "")
    .replace(/(let|const|var)\s+(\w+)\s*:[^=;]+=/g, "$1 $2 =")
    .replace(/function\s+(\w+)\s*\(([^)]*)\)\s*:[^{]+\{/g, (m, name, params) => {
        const clean = params.replace(/:\s*[^,)]+/g, "");
        return "function " + name + "(" + clean + ") {";
    })
    .replace(/\/\/\s*\$Flow[^\n]*/g, "");

let fns;
try {
    fns = new Function(
        section + "\nreturn { trackSchedulerEvent, resolveEventType, resolveEventTimeStamp };"
    )();
} catch(e) {
    console.error("Eval failed:", e.message, "\n", section.substring(0, 500));
    process.exit(1);
}

// Reset: clear any tracked event
global.event = undefined;
fns.trackSchedulerEvent();
""".replace("TARGET_PATH", TARGET)


def _run_js(test_code: str) -> subprocess.CompletedProcess:
    """Run JS test_code after the extraction preamble."""
    return subprocess.run(
        ["node", "-e", _JS_PREAMBLE + test_code],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- file must exist with correct exports
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_and_has_exports():
    """Target file exists and exports the three required functions."""
    content = Path(TARGET).read_text()
    assert "export function trackSchedulerEvent" in content
    assert "export function resolveEventType" in content
    assert "export function resolveEventTimeStamp" in content


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resolve_event_type_modern():
    """resolveEventType returns event.type for modern events."""
    r = _run_js(r"""
const types = ["click", "keydown", "touchstart", "scroll", "pointerup"];
for (const t of types) {
    global.event = { type: t, timeStamp: 1 };
    const result = fns.resolveEventType();
    if (result !== t) {
        console.error("Expected " + t + ", got " + result);
        process.exit(1);
    }
}
console.log("PASS");
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_resolve_event_type_legacy():
    """resolveEventType handles legacy RN dispatchConfig.phasedRegistrationNames."""
    r = _run_js(r"""
const cases = [
    // bubbled with "on" prefix -> strip and lowercase
    [{ dispatchConfig: { phasedRegistrationNames: { bubbled: "onClick" } }, timeStamp: 1 }, "click"],
    [{ dispatchConfig: { phasedRegistrationNames: { bubbled: "onTouchStart" } }, timeStamp: 2 }, "touchstart"],
    // captured with "on" prefix
    [{ dispatchConfig: { phasedRegistrationNames: { captured: "onKeyDown" } }, timeStamp: 3 }, "keydown"],
    // no "on" prefix -> just lowercase
    [{ dispatchConfig: { phasedRegistrationNames: { bubbled: "press" } }, timeStamp: 4 }, "press"],
    // null dispatchConfig -> null
    [{ dispatchConfig: null, timeStamp: 5 }, null],
    // null phasedRegistrationNames -> null
    [{ dispatchConfig: { phasedRegistrationNames: null }, timeStamp: 6 }, null],
];
for (const [evt, expected] of cases) {
    global.event = evt;
    const result = fns.resolveEventType();
    if (result !== expected) {
        console.error("Expected " + expected + ", got " + result + " for " + JSON.stringify(evt));
        process.exit(1);
    }
}
console.log("PASS");
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_resolve_event_timestamp():
    """resolveEventTimeStamp returns event.timeStamp from global.event."""
    r = _run_js(r"""
const timestamps = [0, 42, 999.5, 1234567890.123];
for (const ts of timestamps) {
    global.event = { type: "test", timeStamp: ts };
    const result = fns.resolveEventTimeStamp();
    if (result !== ts) {
        console.error("Expected " + ts + ", got " + result);
        process.exit(1);
    }
}
console.log("PASS");
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_scheduler_event_filtering():
    """Tracked scheduler event is filtered out; new events are not."""
    r = _run_js(r"""
// Track an event
const tracked = { type: "click", timeStamp: 42 };
global.event = tracked;
fns.trackSchedulerEvent();

// Same event still in global.event -> should be filtered
if (fns.resolveEventType() !== null) {
    console.error("Type should be null for tracked event");
    process.exit(1);
}
if (fns.resolveEventTimeStamp() !== -1.1) {
    console.error("Timestamp should be -1.1 for tracked event");
    process.exit(1);
}

// Different event -> should NOT be filtered
const fresh = { type: "mousemove", timeStamp: 99 };
global.event = fresh;
if (fns.resolveEventType() !== "mousemove") {
    console.error("New event type should resolve");
    process.exit(1);
}
if (fns.resolveEventTimeStamp() !== 99) {
    console.error("New event timestamp should resolve");
    process.exit(1);
}

// Re-track the new event -> now it should be filtered
fns.trackSchedulerEvent();
if (fns.resolveEventType() !== null) {
    console.error("Re-tracked event type should be null");
    process.exit(1);
}
if (fns.resolveEventTimeStamp() !== -1.1) {
    console.error("Re-tracked event timestamp should be -1.1");
    process.exit(1);
}

console.log("PASS");
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_event_returns_defaults():
    """With no global.event, resolveEventType returns null, resolveEventTimeStamp returns -1.1."""
    r = _run_js(r"""
global.event = undefined;
if (fns.resolveEventType() !== null) {
    console.error("Expected null when no event");
    process.exit(1);
}
if (fns.resolveEventTimeStamp() !== -1.1) {
    console.error("Expected -1.1 when no event");
    process.exit(1);
}
console.log("PASS");
""")
    assert r.returncode == 0, f"Failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_function_signatures_preserved():
    """Exported functions keep their original Flow type signatures."""
    content = Path(TARGET).read_text()
    assert "export function trackSchedulerEvent(): void" in content, \
        "trackSchedulerEvent signature changed"
    assert "export function resolveEventType(): null | string" in content, \
        "resolveEventType signature changed"
    assert "export function resolveEventTimeStamp(): number" in content, \
        "resolveEventTimeStamp signature changed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- CLAUDE.md + .claude/skills/flow/SKILL.md
def test_no_wildcard_imports():
    """No wildcard imports in the modified file."""
    content = Path(TARGET).read_text()
    wildcards = re.findall(r"import\s+\*", content)
    assert len(wildcards) == 0, f"Found wildcard imports: {wildcards}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates -- ensure fix does not break existing tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_flow_typecheck():
    """Repos Flow typecheck passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "check", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stderr[-1000:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repos ESLint passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_native_renderer_tests():
    """React Native renderer tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test", "--releaseChannel=xplat", "--testPathPattern=react-native-renderer", "--ci"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"React Native renderer tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
