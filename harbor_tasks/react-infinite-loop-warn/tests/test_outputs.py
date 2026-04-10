"""
Task: react-infinite-loop-warn
Repo: react @ 3f0b9e61c467cd6e09cac6fb69f6e8f68cd3c5d7
PR:   35999

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/react"
WORKLOOP = f"{REPO}/packages/react-reconciler/src/ReactFiberWorkLoop.js"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workloop_has_core_functions():
    """Core functions in ReactFiberWorkLoop.js must still exist."""
    src = Path(WORKLOOP).read_text()
    assert "function throwIfInfiniteUpdateLoopDetected" in src, \
        "throwIfInfiniteUpdateLoopDetected function not found"
    assert "function flushSpawnedWork" in src, \
        "flushSpawnedWork function not found"
    assert "nestedUpdateCount" in src, \
        "nestedUpdateCount variable not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks that must pass on both base and fix
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint checks must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        # Install errors are acceptable, skip lint test if deps can't install
        return
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_flow():
    """Repo's Flow type checks must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        return
    r = subprocess.run(
        ["node", "./scripts/tasks/flow.js", "dom-browser"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_tests_relevant():
    """Tests for modified module must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        return
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactUpdates", "--testNamePattern=infinite"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ReactUpdates tests failed:\n{r.stderr[-500:]}"


def test_repo_reconciler_infinite():
    """Reconciler tests for infinite loop handling must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        return
    r = subprocess.run(
        ["yarn", "test", "--testPathPattern=ReactIncrementalErrorHandling", "--testNamePattern=infinite"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Reconciler infinite loop tests failed:\n{r.stderr[-500:]}"


def test_repo_flags():
    """Feature flags check must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        return
    r = subprocess.run(
        ["yarn", "flags"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Flags check failed:\n{r.stderr[-500:]}"


def test_repo_version():
    """Version check must pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile", "--silent"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    if r.returncode != 0:
        return
    r = subprocess.run(
        ["yarn", "version-check"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_update_kind_constants():
    """Three distinct constants for nested update kind tracking must be defined."""
    src = Path(WORKLOOP).read_text()
    assert re.search(r"const\s+NO_NESTED_UPDATE\s*=\s*\d", src), \
        "NO_NESTED_UPDATE constant not found"
    assert re.search(r"const\s+NESTED_UPDATE_SYNC_LANE\s*=\s*\d", src), \
        "NESTED_UPDATE_SYNC_LANE constant not found"
    assert re.search(r"const\s+NESTED_UPDATE_PHASE_SPAWN\s*=\s*\d", src), \
        "NESTED_UPDATE_PHASE_SPAWN constant not found"
    # Verify distinct values
    vals = []
    for name in ["NO_NESTED_UPDATE", "NESTED_UPDATE_SYNC_LANE", "NESTED_UPDATE_PHASE_SPAWN"]:
        m = re.search(rf"const\s+{name}\s*=\s*(\d+)", src)
        assert m, f"Could not extract value for {name}"
        vals.append(int(m.group(1)))
    assert len(set(vals)) == 3, f"Constants must have distinct values, got {vals}"


# [pr_diff] fail_to_pass
def test_nested_update_kind_tracking():
    """nestedUpdateKind variable must track different update kinds in flushSpawnedWork."""
    src = Path(WORKLOOP).read_text()
    assert re.search(r"let\s+nestedUpdateKind", src), \
        "nestedUpdateKind variable not declared"
    assert "nestedUpdateKind = NESTED_UPDATE_SYNC_LANE" in src, \
        "nestedUpdateKind never assigned NESTED_UPDATE_SYNC_LANE"
    assert "nestedUpdateKind = NESTED_UPDATE_PHASE_SPAWN" in src, \
        "nestedUpdateKind never assigned NESTED_UPDATE_PHASE_SPAWN"
    assert "nestedUpdateKind = NO_NESTED_UPDATE" in src, \
        "nestedUpdateKind never reset to NO_NESTED_UPDATE"


# [pr_diff] fail_to_pass
def test_phase_spawn_uses_console_error():
    """NESTED_UPDATE_PHASE_SPAWN path must warn via console.error instead of throwing."""
    src = Path(WORKLOOP).read_text()
    func_start = src.find("function throwIfInfiniteUpdateLoopDetected")
    assert func_start != -1, "throwIfInfiniteUpdateLoopDetected function not found"
    func_body = src[func_start:func_start + 4000]
    assert "NESTED_UPDATE_PHASE_SPAWN" in func_body, \
        "NESTED_UPDATE_PHASE_SPAWN not referenced in throwIfInfiniteUpdateLoopDetected"
    assert re.search(
        r"console\.error\(\s*['\"]Maximum update depth exceeded\. This could be an infinite loop",
        func_body,
    ), "Expected console.error warning about potential infinite loop"


# [pr_diff] fail_to_pass
def test_sync_lane_branches_on_render_context():
    """NESTED_UPDATE_SYNC_LANE path must check render context: warn in render, throw outside."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('packages/react-reconciler/src/ReactFiberWorkLoop.js', 'utf8');

// Find throwIfInfiniteUpdateLoopDetected function
const funcStart = src.indexOf('function throwIfInfiniteUpdateLoopDetected');
if (funcStart === -1) { console.error('function not found'); process.exit(1); }
const funcBody = src.slice(funcStart, funcStart + 4000);

// Must reference NESTED_UPDATE_SYNC_LANE in the function
if (!funcBody.includes('NESTED_UPDATE_SYNC_LANE')) {
    console.error('NESTED_UPDATE_SYNC_LANE not found in throwIfInfiniteUpdateLoopDetected');
    process.exit(1);
}

// Must check RenderContext to decide warn vs throw for sync lane updates
if (!funcBody.includes('RenderContext')) {
    console.error('No RenderContext check in throwIfInfiniteUpdateLoopDetected');
    process.exit(1);
}

// Must have both console.error (warn path) and throw new Error (throw path)
if (!funcBody.includes('console.error')) {
    console.error('No console.error warn path in throwIfInfiniteUpdateLoopDetected');
    process.exit(1);
}
if (!funcBody.includes('throw new Error')) {
    console.error('No throw new Error in throwIfInfiniteUpdateLoopDetected');
    process.exit(1);
}

console.log('OK');
"""],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, \
        f"Sync lane context branching check failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_else_resets_nested_update_state():
    """Else branch in flushSpawnedWork must reset rootWithNestedUpdates and nestedUpdateKind."""
    src = Path(WORKLOOP).read_text()
    func_start = src.find("function flushSpawnedWork")
    assert func_start != -1, "flushSpawnedWork function not found"
    func_body = src[func_start:func_start + 15000]
    assert "rootWithNestedUpdates = null" in func_body, \
        "flushSpawnedWork does not reset rootWithNestedUpdates to null"
    assert "nestedUpdateKind = NO_NESTED_UPDATE" in func_body, \
        "flushSpawnedWork does not reset nestedUpdateKind to NO_NESTED_UPDATE"
