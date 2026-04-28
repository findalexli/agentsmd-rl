"""
Task: opencode-variant-menu-subagent-info
Repo: anomalyco/opencode @ 860531c275cf845f80ccf26bba5bad745fe98398
PR:   19537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
SESSION = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
FOOTER = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - CI typecheck (scoped to affected package)
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun run typecheck
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - TUI unit tests
def test_repo_tui_prompt_part_tests():
    """TUI prompt-part unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/cli/cmd/tui/prompt-part.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"TUI prompt-part tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Session module unit tests
def test_repo_session_unit_tests():
    """Session module unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/session/session.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Session unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - TUI thread tests
def test_repo_tui_thread_tests():
    """TUI thread unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/cli/tui/thread.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"TUI thread tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Server session-list tests
def test_repo_server_session_list_tests():
    """Server session-list unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/server/session-list.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Server session-list tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Server session-messages tests
def test_repo_server_session_messages_tests():
    """Server session-messages unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/server/session-messages.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Server session-messages tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - CLI keybind-plugin tests
def test_repo_cli_keybind_plugin_tests():
    """CLI keybind-plugin unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/cli/tui/keybind-plugin.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"CLI keybind-plugin tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Session compaction tests
def test_repo_session_compaction_tests():
    """Session compaction unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/session/compaction.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Session compaction tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - TUI transcript tests
def test_repo_tui_transcript_tests():
    """TUI transcript unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/cli/tui/transcript.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"TUI transcript tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - TUI theme-store tests
def test_repo_tui_theme_store_tests():
    """TUI theme-store unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/cli/tui/theme-store.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"TUI theme-store tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Server session-select tests
def test_repo_server_session_select_tests():
    """Server session-select unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/server/session-select.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Server session-select tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass - Server global-session-list tests
def test_repo_server_global_session_list_tests():
    """Server global-session-list unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/opencode/packages/opencode
bun test test/server/global-session-list.test.ts
"""],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Server global-session-list tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [static] pass_to_pass
def test_files_exist_and_not_truncated():
    """Modified files must exist and have meaningful content."""
    for f in [SESSION, FOOTER]:
        p = Path(f)
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 200, f"{f} is truncated (< 200 bytes)"


# [static] pass_to_pass
def test_core_exports_intact():
    """Key exports and components must still exist after changes."""
    session_src = Path(SESSION).read_text()
    footer_src = Path(FOOTER).read_text()

    assert "export function Session" in session_src, "Session export missing"
    assert "export function SubagentFooter" in footer_src, "SubagentFooter export missing"
    assert "function InlineTool(" in session_src, "InlineTool function missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cycle_direction_fixed():
    """cycleSession must subtract direction from index, not add it.

    Extracts the cycling arithmetic and evaluates it with multiple inputs
    to verify the direction is inverted.
    """
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

const lines = src.split('\n');
let opLine = null;
for (const line of lines) {
    if (/findIndex/.test(line) && /direction/.test(line)) {
        opLine = line;
        break;
    }
}
if (!opLine) { console.log(JSON.stringify({ok: false, reason: "no findIndex+direction line"})); process.exit(0); }

const m = opLine.match(/\)\s*([+\-])\s*direction/);
if (!m) { console.log(JSON.stringify({ok: false, reason: "can't parse operator from: " + opLine.trim()})); process.exit(0); }

const op = m[1];
const cycle = new Function('idx', 'len', 'dir', `
    let next = idx ${op} dir;
    if (next >= len) next = 0;
    if (next < 0) next = len - 1;
    return next;
`);

// After fix (- direction): dir=1 means go to lower index
const tests = [
    [2, 5, 1, 1],
    [0, 5, 1, 4],
    [4, 5, -1, 0],
    [3, 5, 1, 2],
    [1, 5, -1, 2],
    [0, 3, 1, 2],
    [1, 4, 1, 0],
    [3, 4, -1, 0],
];

let passed = 0;
for (const [ci, total, dir, expected] of tests) {
    if (cycle(ci, total, dir) === expected) passed++;
}
console.log(JSON.stringify({ok: passed === tests.length, passed, total: tests.length, op}));
""", SESSION],
        capture_output=True, text=True, timeout=10,
    )
    assert result.stdout.strip(), f"node produced no output; stderr: {result.stderr[:300]}"
    data = json.loads(result.stdout.strip())
    assert data["ok"], (
        f"Cycling direction wrong: operator='{data.get('op')}', "
        f"passed {data.get('passed')}/{data.get('total')}"
    )


# [pr_diff] fail_to_pass
def test_subagent_footer_shows_type():
    """Footer must extract agent type from session title via regex and display it."""
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

// Must have a regex to extract agent type from title
const regexMatch = src.match(/\.match\(\s*(\/[^/]+\/[gimsuy]*)\s*\)/);
if (!regexMatch) { console.log(JSON.stringify({ok: false, reason: "no regex found"})); process.exit(0); }

try {
    const re = eval(regexMatch[1]);

    const tests = [
        ['@coder subagent session #3', 'coder'],
        ['@explorer subagent', 'explorer'],
        ['@writer subagent task', 'writer'],
        ['plain session title', null],
        ['@planner subagent review', 'planner'],
    ];

    let passed = 0;
    for (const [title, expected] of tests) {
        const m = title.match(re);
        if (expected === null) {
            if (!m || !m[1]) passed++;
        } else {
            if (m && m[1] && m[1].toLowerCase() === expected) passed++;
        }
    }

    const noStatic = !src.includes('<b>Subagent session</b>');
    console.log(JSON.stringify({ok: passed >= 4 && noStatic, passed, total: tests.length, noStatic}));
} catch(e) {
    console.log(JSON.stringify({ok: false, reason: e.message}));
}
""", FOOTER],
        capture_output=True, text=True, timeout=10,
    )
    assert result.stdout.strip(), f"node produced no output; stderr: {result.stderr[:300]}"
    data = json.loads(result.stdout.strip())
    assert data["ok"], f"Subagent type extraction failed: {data}"


# [pr_diff] fail_to_pass
def test_subagent_footer_shows_index():
    """Footer must compute sibling index from parentID and display 'X of Y'."""
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');

const checks = {
    parentID: /parentID/.test(src),
    filter: /\.filter\(/.test(src),
    findIndex: /\.findIndex\(/.test(src) || /\.indexOf\(/.test(src),
    ofPattern: / of /.test(src) || /"of"/.test(src) || /'of'/.test(src),
    oneBased: /index\s*[\+]\s*1|idx\s*[\+]\s*1|\+\s*1/.test(src),
    lengthRef: /\.length/.test(src),
    filterParent: /\.filter\(\s*\(?(\w+)\)?\s*=>\s*\1\.parentID\s*===/.test(src),
};

const ok = checks.parentID && checks.filter && checks.findIndex
    && checks.ofPattern && checks.oneBased && checks.filterParent;

console.log(JSON.stringify({ok, checks}));
""", FOOTER],
        capture_output=True, text=True, timeout=10,
    )
    assert result.stdout.strip(), f"node produced no output; stderr: {result.stderr[:300]}"
    data = json.loads(result.stdout.strip())
    assert data["ok"], f"Sibling index computation missing or incorrect: {data}"


# [pr_diff] fail_to_pass
def test_task_content_includes_subagent_type():
    """Task component must include subagent_type in content with capitalization and fallback."""
    src = Path(SESSION).read_text()

    # Must reference subagent_type (only used in Task's content memo)
    assert "subagent_type" in src, "subagent_type not referenced in session/index.tsx"

    # Must have a fallback for missing subagent_type (nullish coalescing or logical OR)
    assert re.search(r'subagent_type\s*\?\?|subagent_type\s*\|\|', src), \
        "No fallback when subagent_type is missing (expected ?? or ||)"

    # Must apply capitalization (titlecase, toUpperCase, capitalize, etc.)
    assert re.search(r'titlecase|capitalize|toUpperCase|charAt\(0\)', src), \
        "No capitalization applied to subagent_type"

    # Must combine subagent_type with description in the same expression
    assert re.search(
        r'subagent_type[\s\S]{0,150}description|description[\s\S]{0,150}subagent_type',
        src
    ), "subagent_type and description not combined in Task content"

    # Must no longer show plain 'Task ${description}' without a type prefix
    assert not re.search(r'`Task\s+\$\{', src), \
        "Still uses plain 'Task ${...}' without subagent type prefix"


# [pr_diff] fail_to_pass
def test_dead_code_removed():
    """Unused ToolTitle function should be removed from session/index.tsx."""
    src = Path(SESSION).read_text()
    assert "function ToolTitle(" not in src, "Unused ToolTitle function still present"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:12 @ 860531c275cf845f80ccf26bba5bad745fe98398
def test_no_try_catch_in_footer():
    """subagent-footer.tsx must not contain try/catch blocks. Per AGENTS.md:12."""
    src = Path(FOOTER).read_text()
    assert "try {" not in src and "try{" not in src, \
        "try/catch block found in subagent-footer.tsx (AGENTS.md:12: avoid try/catch where possible)"


# [agent_config] fail_to_pass — AGENTS.md:17 @ 860531c275cf845f80ccf26bba5bad745fe98398
def test_functional_array_methods():
    """New sibling computation in footer must use functional array methods
    (filter/map/flatMap), not C-style for loops. Per AGENTS.md:17."""
    src = Path(FOOTER).read_text()

    has_functional = ".filter(" in src or ".reduce(" in src or ".flatMap(" in src
    has_index = ".findIndex(" in src or ".indexOf(" in src

    # Must NOT use imperative for loops for sibling computation
    has_imperative = bool(re.search(r"for\s*\(\s*(let|var)\s+\w+[\s\S]{0,100}parentID", src))

    assert has_functional, "No functional array methods (filter/reduce/flatMap) found in footer"
    assert has_index, "No index computation method (findIndex/indexOf) found in footer"
    assert not has_imperative, "Imperative for loop used near parentID logic"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")