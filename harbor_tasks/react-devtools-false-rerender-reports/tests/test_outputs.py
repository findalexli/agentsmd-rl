"""
Task: React DevTools false re-render reports fix
Repo: facebook/react @ eab523e2a99583703b13536670dfdd8a3b1e26e0
PR:   35723

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_renderer_file_valid():
    """renderer.js must exist with substantial content (not truncated or emptied)."""
    # AST-only because: JavaScript with Flow type annotations cannot be parsed by node --check
    content = Path(RENDERER).read_text()
    assert len(content) > 10000, (
        f"renderer.js appears truncated or emptied ({len(content)} bytes)"
    )
    # Verify core structure is intact
    assert "export function attach(" in content, (
        "renderer.js is missing the 'export function attach(' entry point"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prevfiber_guard_profiling_loop():
    """Core fix: prevFiber !== fiber guard before didFiberRender in profiling data loop.

    Without this guard, when a fiber bails out and React reuses it (prevFiber === fiber),
    the profiler incorrectly reports didRender: true for components behind filtered parents.
    The fix adds a reference-equality check so bailed-out fibers skip the didFiberRender call.
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()

    # The fix changes:
    #   if (prevFiber == null || didFiberRender(prevFiber, fiber))
    # to:
    #   if (prevFiber == null || (prevFiber !== fiber && didFiberRender(prevFiber, fiber)))
    #
    # Check for both possible formatting styles
    has_guard = (
        "prevFiber !== fiber && didFiberRender" in content
        or (
            "prevFiber !== fiber &&\n" in content
            and "didFiberRender(prevFiber, fiber)" in content
        )
    )
    assert has_guard, (
        "renderer.js is missing the 'prevFiber !== fiber && didFiberRender' guard "
        "in the profiling data loop. Components behind filtered fibers will be "
        "falsely reported as re-rendered."
    )


# [pr_diff] fail_to_pass
def test_prevfiber_guard_trace_update():
    """Core fix: traceNearestHostComponentUpdate only set when prevFiber !== nextFiber.

    When prevFiber === nextFiber, the fiber bailed out and no render occurred.
    Setting the trace flag in this case causes false render traces for
    components whose fiber was reused without re-rendering.
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()
    lines = content.split("\n")

    # The fix wraps the traceNearestHostComponentUpdate assignment:
    #   if (prevFiber !== nextFiber) {
    #     traceNearestHostComponentUpdate = didFiberRender(prevFiber, nextFiber);
    #   }
    found = False
    for i, line in enumerate(lines):
        if "prevFiber !== nextFiber" in line:
            # Look ahead up to 6 lines for the trace flag assignment
            context = "\n".join(lines[i : i + 6])
            if "traceNearestHostComponentUpdate" in context:
                found = True
                break

    assert found, (
        "renderer.js is missing the 'if (prevFiber !== nextFiber)' guard around "
        "traceNearestHostComponentUpdate assignment."
    )


# [pr_diff] fail_to_pass
def test_prevfiber_guard_inspect_update():
    """Core fix: hasElementUpdatedSinceLastInspected only set when prevFiber !== nextFiber.

    Setting this flag on a bailed-out fiber causes spurious cache invalidation
    and can indirectly contribute to false re-render reports in the inspector.
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()
    lines = content.split("\n")

    # The fix wraps the hasElementUpdatedSinceLastInspected block:
    #   if (prevFiber !== nextFiber) {
    #     if (mostRecentlyInspectedElement !== null && ... && didFiberRender(...)) {
    #       hasElementUpdatedSinceLastInspected = true;
    #     }
    #   }
    found = False
    for i, line in enumerate(lines):
        if "prevFiber !== nextFiber" in line:
            context = "\n".join(lines[i : i + 16])
            if "hasElementUpdatedSinceLastInspected" in context:
                found = True
                break

    assert found, (
        "renderer.js is missing the 'if (prevFiber !== nextFiber)' guard around "
        "hasElementUpdatedSinceLastInspected."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_profiling_data_logic_intact():
    """Regression: the profiling data recording logic in renderer.js is intact.

    The section that records profiling durations must still contain key operations:
    actualDuration processing, pushOperation calls, and treeBaseDuration handling.
    An agent must not gut this logic while adding the prevFiber guard.

    Note: upstream test suite (profilingCharts-test.js) cannot be run in isolation
    because React's Jest setup requires custom transforms (@reactVersion pragmas,
    Flow types, built artifacts via --project devtools).
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()

    # The profiling data loop must still process actual durations
    assert "actualDuration" in content, (
        "renderer.js is missing 'actualDuration' — profiling duration recording broken"
    )
    # Must still push profiling operations
    assert "pushOperation" in content, (
        "renderer.js is missing 'pushOperation' — profiling operation recording broken"
    )
    # Must still handle tree base durations
    assert "treeBaseDuration" in content, (
        "renderer.js is missing 'treeBaseDuration' — profiling tree data broken"
    )
    # The prevFiber == null check must still exist (the guard adds to it, not replaces it)
    assert "prevFiber == null" in content, (
        "renderer.js is missing 'prevFiber == null' check — profiling null guard removed"
    )


# [static] pass_to_pass
def test_didfiberrender_not_stubbed():
    """Anti-stub: didFiberRender retains its switch-based type dispatch logic.

    The function must not be removed or replaced with a trivial stub.
    It contains a switch statement over fiber tags (ClassComponent, etc.).
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()
    assert "function didFiberRender" in content, (
        "didFiberRender function was removed from renderer.js"
    )
    # Must retain the switch-case dispatch (not just return true/false)
    # Find the function and verify it has ClassComponent in its body
    idx = content.index("function didFiberRender")
    # Look at the next 500 chars for the switch cases
    snippet = content[idx : idx + 500]
    assert "ClassComponent" in snippet, (
        "didFiberRender appears stubbed — missing ClassComponent case in switch"
    )


# [static] pass_to_pass
def test_didfiber_render_uses_prevfiber_param():
    """Anti-cheat: didFiberRender must still use its prevFiber parameter.

    An agent might try to "fix" the false-render issue by making didFiberRender
    always return false or by ignoring prevFiber. The function must still compare
    prevFiber and nextFiber memoizedProps/memoizedState for ClassComponent/FunctionComponent.
    """
    # AST-only because: JavaScript with Flow types, deeply integrated with React internals
    content = Path(RENDERER).read_text()
    idx = content.index("function didFiberRender")
    # Get the function body (2000 chars covers the full switch including default case)
    snippet = content[idx : idx + 2000]

    # Must reference prevFiber's memoizedProps or memoizedState
    assert re.search(r"prevFiber\s*\.\s*memoized(Props|State)", snippet), (
        "didFiberRender does not compare prevFiber.memoizedProps/State — "
        "the function may have been stubbed to always return false"
    )
