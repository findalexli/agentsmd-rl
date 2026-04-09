""
Task: react-devtools-deprecation-warning
Repo: facebook/react @ 014138df87869b174956f90a33fd6cf66e160114
PR:   facebook/react#35994

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
BUILD_TYPE_FILE = (
    "packages/react-devtools-extensions/src/contentScripts/reactBuildType.js"
)


_flow_strip_installed = False
_yarn_installed = False


def _ensure_yarn():
    """Ensure yarn dependencies are installed."""
    global _yarn_installed
    if not _yarn_installed:
        subprocess.run(
            ["yarn", "install", "--frozen-lockfile"],
            capture_output=True, timeout=300, cwd=REPO, check=False,
        )
        _yarn_installed = True


def _strip_flow(filepath: str) -> str:
    """Strip Flow type annotations using flow-remove-types."""
    global _flow_strip_installed
    if not _flow_strip_installed:
        subprocess.run(
            ["npm", "install", "-g", "flow-remove-types"],
            capture_output=True, timeout=60, check=True,
        )
        _flow_strip_installed = True
    r = subprocess.run(
        ["flow-remove-types", filepath, "--pretty"],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"flow-remove-types failed: {r.stderr.decode()}"
    return r.stdout.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_repo_flow_typecheck():
    """Repo's Flow typecheck passes on dom-node renderer (pass_to_pass)."""
    _ensure_yarn()
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_repo_eslint_modified():
    """ESLint passes on modified devtools files (pass_to_pass)."""
    _ensure_yarn()
    files = [
        "packages/react-devtools-extensions/src/contentScripts/installHook.js",
        "packages/react-devtools-shared/src/backend/types.js",
        "packages/react-devtools-shared/src/hook.js",
    ]
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"] + files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """Pre-existing modified JS files must exist and contain valid structure."""
    files = [
        "packages/react-devtools-extensions/src/contentScripts/installHook.js",
        "packages/react-devtools-shared/src/backend/types.js",
        "packages/react-devtools-shared/src/hook.js",
    ]
    for f in files:
        path = Path(f"{REPO}/{f}")
        assert path.exists(), f"Missing file: {f}"
        content = path.read_text()
        assert len(content) > 100, f"File suspiciously small: {f}"
        # Check balanced braces (basic structural validity)
        assert content.count("{") == content.count("}"), (
            f"Unbalanced braces in {f}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_new_reactbuildtype_file_exists():
    """reactBuildType.js must be created with both required exports."""
    p = Path(f"{REPO}/{BUILD_TYPE_FILE}")
    assert p.exists(), "reactBuildType.js must be created"
    src = p.read_text()
    assert "reduceReactBuild" in src, "Must define reduceReactBuild"
    assert "createReactRendererListener" in src, "Must define createReactRendererListener"


# [pr_diff] fail_to_pass
def test_reduce_react_build_worst_build_wins():
    """reduceReactBuild must implement worst build logic: non-production beats production."""
    p = Path(f"{REPO}/{BUILD_TYPE_FILE}")
    assert p.exists(), "reactBuildType.js must exist"
    src = _strip_flow(str(p))

    test_code = (
        src
        + """
function assertEq(actual, expected, label) {
  if (actual !== expected)
    throw new Error(label + ": expected " + JSON.stringify(expected) + " got " + JSON.stringify(actual));
}
// null always accepts the first value
assertEq(reduceReactBuild(null, "production"),   "production",   "null+production");
assertEq(reduceReactBuild(null, "development"),  "development",  "null+development");
assertEq(reduceReactBuild(null, "outdated"),     "outdated",     "null+outdated");
assertEq(reduceReactBuild(null, "unminified"),   "unminified",   "null+unminified");
assertEq(reduceReactBuild(null, "deadcode"),     "deadcode",     "null+deadcode");
// production is overridden by any non-production value
assertEq(reduceReactBuild("production", "development"), "development", "prod+dev");
assertEq(reduceReactBuild("production", "outdated"),    "outdated",    "prod+outdated");
assertEq(reduceReactBuild("production", "deadcode"),    "deadcode",    "prod+deadcode");
assertEq(reduceReactBuild("production", "unminified"),  "unminified",  "prod+unminified");
// non-production is NOT overridden by production
assertEq(reduceReactBuild("development", "production"), "development", "dev+prod");
assertEq(reduceReactBuild("outdated",    "production"), "outdated",    "outdated+prod");
assertEq(reduceReactBuild("deadcode",    "production"), "deadcode",    "deadcode+prod");
assertEq(reduceReactBuild("unminified",  "production"), "unminified",  "unminified+prod");
// non-production can still be updated by another non-production value
assertEq(reduceReactBuild("development", "outdated"),   "outdated",    "dev+outdated");
assertEq(reduceReactBuild("outdated",    "deadcode"),   "deadcode",    "outdated+deadcode");
console.log("OK");
"""
    )
    r = subprocess.run(["node", "-e", test_code], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"reduceReactBuild logic incorrect:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
    assert "OK" in r.stdout.decode()


# [pr_diff] fail_to_pass
def test_listener_maintains_state_across_renderers():
    """createReactRendererListener must preserve worst build across multiple renderer attachments."""
    p = Path(f"{REPO}/{BUILD_TYPE_FILE}")
    assert p.exists(), "reactBuildType.js must exist"
    src = _strip_flow(str(p))

    test_code = (
        src
        + """
function makeWindow() {
  const msgs = [];
  return { msgs, postMessage(m) { msgs.push(m.payload.reactBuildType); } };
}

// Scenario 1: dev first, then two production renderers -- must keep "development"
const w1 = makeWindow();
const l1 = createReactRendererListener(w1);
l1({ reactBuildType: "development" });
l1({ reactBuildType: "production" });
l1({ reactBuildType: "production" });
if (w1.msgs[0] !== "development") throw new Error("S1 msg[0]: expected development got " + w1.msgs[0]);
if (w1.msgs[1] !== "development") throw new Error("S1 msg[1]: expected development got " + w1.msgs[1]);
if (w1.msgs[2] !== "development") throw new Error("S1 msg[2]: expected development got " + w1.msgs[2]);

// Scenario 2: production first, then dev -- must switch to "development"
const w2 = makeWindow();
const l2 = createReactRendererListener(w2);
l2({ reactBuildType: "production" });
l2({ reactBuildType: "development" });
if (w2.msgs[0] !== "production")   throw new Error("S2 msg[0]: expected production got "   + w2.msgs[0]);
if (w2.msgs[1] !== "development")  throw new Error("S2 msg[1]: expected development got "  + w2.msgs[1]);

// Scenario 3: listeners are independent (closure state not shared)
const w3a = makeWindow();
const w3b = makeWindow();
const la = createReactRendererListener(w3a);
const lb = createReactRendererListener(w3b);
la({ reactBuildType: "development" });
lb({ reactBuildType: "production" });
if (w3a.msgs[0] !== "development") throw new Error("S3a: expected development got " + w3a.msgs[0]);
if (w3b.msgs[0] !== "production")  throw new Error("S3b: expected production got "  + w3b.msgs[0]);

// Scenario 4: outdated then production -- keeps outdated
const w4 = makeWindow();
const l4 = createReactRendererListener(w4);
l4({ reactBuildType: "outdated" });
l4({ reactBuildType: "production" });
if (w4.msgs[1] !== "outdated") throw new Error("S4: expected outdated got " + w4.msgs[1]);

// Scenario 5: deadcode then production -- keeps deadcode
const w5 = makeWindow();
const l5 = createReactRendererListener(w5);
l5({ reactBuildType: "deadcode" });
l5({ reactBuildType: "production" });
l5({ reactBuildType: "development" });
if (w5.msgs[1] !== "deadcode") throw new Error("S5 msg[1]: expected deadcode got " + w5.msgs[1]);
if (w5.msgs[2] !== "development") throw new Error("S5 msg[2]: expected development got " + w5.msgs[2]);

console.log("OK");
"""
    )
    r = subprocess.run(["node", "-e", test_code], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"Listener state management incorrect:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )
    assert "OK" in r.stdout.decode()


# [pr_diff] fail_to_pass
def test_installhook_uses_factory_not_inline():
    """installHook.js must use createReactRendererListener factory; inline listener must be gone."""
    src = Path(
        f"{REPO}/packages/react-devtools-extensions/src/contentScripts/installHook.js"
    ).read_text()
    assert "createReactRendererListener" in src, (
        "installHook.js must import and use createReactRendererListener"
    )
    # Old inline pattern sent "react-renderer-attached" directly inside the listener
    assert "react-renderer-attached" not in src, (
        "Old inline react-renderer-attached listener must be removed from installHook.js"
    )


# [pr_diff] fail_to_pass
def test_react_build_type_union_exported():
    """ReactBuildType must be exported from types.js with all five required literal values."""
    src = Path(
        f"{REPO}/packages/react-devtools-shared/src/backend/types.js"
    ).read_text()
    assert "ReactBuildType" in src, "types.js must define ReactBuildType"
    for value in ("deadcode", "development", "outdated", "production", "unminified"):
        # Accept either single or double quoted literals
        assert (f'"{value}"' in src) or (f"'{value}'" in src), f"ReactBuildType must include literal \{value}"


# ---------------------------------------------------------------------------
# Anti-stub (static, fail_to_pass)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """New reactBuildType.js must contain real implementation logic, not stubs."""
    p = Path(f"{REPO}/{BUILD_TYPE_FILE}")
    assert p.exists(), "reactBuildType.js must exist"
    src = p.read_text()
    assert len(src) > 200, "File seems too short to contain real logic"
    assert "return" in src, "reduceReactBuild must have return statements"
    assert (
        "currentReactBuildType" in src or "displayedReactBuild" in src
    ), "Must reference internal state variable"