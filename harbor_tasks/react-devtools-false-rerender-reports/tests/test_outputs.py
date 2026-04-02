"""
Task: React DevTools false re-render reports fix
Repo: facebook/react @ eab523e2a99583703b13536670dfdd8a3b1e26e0
PR:   35723

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """renderer.js must parse without syntax errors."""
    # AST-only because: JavaScript file cannot be imported in Python
    r = subprocess.run(
        ["node", "--check", RENDERER],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in renderer.js:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prevfiber_guard_profiling_loop():
    """Core fix: prevFiber !== fiber guard before didFiberRender in profiling data loop.

    Without this guard, when a fiber bails out and React reuses it (prevFiber === fiber),
    the profiler incorrectly reports didRender: true for components behind filtered parents.
    """
    # AST-only because: JavaScript file cannot be imported in Python
    content = Path(RENDERER).read_text()
    assert "prevFiber !== fiber && didFiberRender" in content, (
        "renderer.js is missing the 'prevFiber !== fiber && didFiberRender' guard "
        "in the profiling data loop. Components behind filtered fibers (host elements, "
        "keyless Fragments) will be falsely reported as re-rendered."
    )


# [pr_diff] fail_to_pass
def test_prevfiber_guard_trace_update():
    """Core fix: traceNearestHostComponentUpdate only set when prevFiber !== nextFiber.

    When prevFiber === nextFiber, the fiber bailed out and no render occurred.
    The trace flag must not be set in this case.
    """
    # AST-only because: JavaScript file cannot be imported in Python
    content = Path(RENDERER).read_text()
    lines = content.split("\n")

    # The fix wraps the traceNearestHostComponentUpdate assignment with if (prevFiber !== nextFiber)
    found = False
    for i, line in enumerate(lines):
        if "prevFiber !== nextFiber" in line:
            context = "\n".join(lines[i : i + 6])
            if "traceNearestHostComponentUpdate" in context:
                found = True
                break

    assert found, (
        "renderer.js is missing the 'if (prevFiber !== nextFiber)' guard around "
        "traceNearestHostComponentUpdate. This causes false render traces for "
        "components whose fiber was reused without re-rendering."
    )


# [pr_diff] fail_to_pass
def test_prevfiber_guard_inspect_update():
    """Core fix: hasElementUpdatedSinceLastInspected only set when prevFiber !== nextFiber.

    Setting this flag on a bailed-out fiber causes spurious cache invalidation
    and can indirectly contribute to false re-render reports.
    """
    # AST-only because: JavaScript file cannot be imported in Python
    content = Path(RENDERER).read_text()
    lines = content.split("\n")

    # The fix wraps the hasElementUpdatedSinceLastInspected assignment with if (prevFiber !== nextFiber)
    found = False
    for i, line in enumerate(lines):
        if "prevFiber !== nextFiber" in line:
            context = "\n".join(lines[i : i + 16])
            if "hasElementUpdatedSinceLastInspected" in context:
                found = True
                break

    assert found, (
        "renderer.js is missing the 'if (prevFiber !== nextFiber)' guard around "
        "hasElementUpdatedSinceLastInspected. This flag must not be set for "
        "bailed-out fibers where prevFiber === nextFiber."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_profiling_charts_pass():
    """Regression: the profilingCharts test suite passes after the fix."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-devtools-shared/src/__tests__/profilingCharts-test.js",
            "--ci",
            "--forceExit",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"profilingCharts tests failed:\n"
        f"{r.stdout.decode()[-3000:]}\n"
        f"{r.stderr.decode()[-500:]}"
    )


# [static] pass_to_pass
def test_didfiberrender_not_stubbed():
    """Anti-stub: didFiberRender retains its switch-based logic and was not deleted."""
    # AST-only because: JavaScript file cannot be imported in Python
    content = Path(RENDERER).read_text()
    assert "function didFiberRender" in content, (
        "didFiberRender function was removed from renderer.js"
    )
    # The function must retain its type-dispatch logic (not just return true/false)
    assert "ClassComponent" in content, (
        "didFiberRender appears to have been stubbed — ClassComponent case is missing"
    )
