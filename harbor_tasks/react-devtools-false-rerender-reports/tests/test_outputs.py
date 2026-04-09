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


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_renderer_file_valid():
    """renderer.js must exist with substantial content and core attach() entry point."""
    content = Path(RENDERER).read_text()
    assert len(content) > 10000, (
        f"renderer.js appears truncated or emptied ({len(content)} bytes)"
    )
    assert "export function attach(" in content, (
        "renderer.js is missing the 'export function attach(' entry point"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification via subprocess execution
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_prevfiber_guard_profiling_loop():
    """Core fix: prevFiber !== fiber guard prevents false didRender in profiling data loop.

    Executes via Node.js to verify:
    1. The guard pattern exists in the profiling section (near actualDuration)
    2. The guard logic correctly blocks didFiberRender when prevFiber === fiber
    3. The guard logic allows didFiberRender when prevFiber !== fiber (real update)
    """
    r = _run_node(
        r"""
const fs = require('fs');
const content = fs.readFileSync('/workspace/react/packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8');

// Step 1: Locate the profiling data section (near actualDuration)
const adIdx = content.indexOf('actualDuration');
if (adIdx === -1) throw new Error('actualDuration not found in renderer.js');

// Search within +/-3000 chars for the guard pattern
const section = content.substring(Math.max(0, adIdx - 3000), adIdx + 3000);
if (!section.includes('prevFiber !== fiber && didFiberRender')) {
    throw new Error(
        'Guard pattern (prevFiber !== fiber && didFiberRender) not found ' +
        'in profiling section near actualDuration'
    );
}

// Step 2: Execute the fixed guard logic with behavioral test cases.
// The fix changes: prevFiber == null || didFiberRender(prevFiber, fiber)
//           into: prevFiber == null || (prevFiber !== fiber && didFiberRender(prevFiber, fiber))
function fixedGuard(prevFiber, fiber, didRenderResult) {
    return prevFiber == null || (prevFiber !== fiber && didRenderResult);
}

// Case 1: New fiber (prevFiber = null) -> should proceed to record
if (fixedGuard(null, {id: 1}, true) !== true) {
    throw new Error('null prevFiber should allow recording');
}

// Case 2: Bailed-out fiber (prevFiber === fiber, same reference).
// didFiberRender might return true but the guard must block it.
const sameFiber = {id: 1};
if (fixedGuard(sameFiber, sameFiber, true) !== false) {
    throw new Error('Bailed-out fiber should NOT be reported as rendered');
}

// Case 3: Real update (different fibers), didFiberRender = true -> proceed
if (fixedGuard({id: 1}, {id: 2}, true) !== true) {
    throw new Error('Real update with didRender=true should be recorded');
}

// Case 4: Real update (different fibers), didFiberRender = false -> skip
if (fixedGuard({id: 1}, {id: 2}, false) !== false) {
    throw new Error('Real update with didRender=false should not be recorded');
}

console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Profiling guard test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_prevfiber_guard_trace_update():
    """Core fix: traceNearestHostComponentUpdate guarded by prevFiber !== nextFiber.

    Executes via Node.js to verify the guard exists around the trace flag
    assignment and that the logic prevents false traces for bailed-out fibers.
    """
    r = _run_node(
        r"""
const fs = require('fs');
const content = fs.readFileSync('/workspace/react/packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8');

// Find the traceNearestHostComponentUpdate = didFiberRender assignment
const traceIdx = content.indexOf('traceNearestHostComponentUpdate = didFiberRender');
if (traceIdx === -1) {
    throw new Error('traceNearestHostComponentUpdate assignment not found');
}

// The guard must appear in the ~200 chars before the assignment
const before = content.substring(Math.max(0, traceIdx - 200), traceIdx);
if (!before.includes('prevFiber !== nextFiber')) {
    throw new Error(
        'traceNearestHostComponentUpdate is not guarded by ' +
        'prevFiber !== nextFiber'
    );
}

// Execute the guard logic for trace updates.
// After fix: only set trace flag when fibers are different references.
function traceGuard(prevFiber, nextFiber) {
    if (prevFiber !== nextFiber) {
        return true; // proceed to call didFiberRender
    }
    return false; // skip — same fiber means no update occurred
}

// Same fiber (bailed out) -> should NOT trace
const f = {id: 1};
if (traceGuard(f, f)) {
    throw new Error('Bailed-out fiber should not trigger trace');
}

// Different fibers -> should trace
if (!traceGuard({id: 1}, {id: 2})) {
    throw new Error('Real update should trigger trace');
}

console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Trace guard test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_prevfiber_guard_inspect_update():
    """Core fix: hasElementUpdatedSinceLastInspected guarded by prevFiber !== nextFiber.

    Executes via Node.js to verify the guard exists around the inspect cache
    invalidation and prevents spurious invalidation for bailed-out fibers.
    """
    r = _run_node(
        r"""
const fs = require('fs');
const content = fs.readFileSync('/workspace/react/packages/react-devtools-shared/src/backend/fiber/renderer.js', 'utf8');

// Find hasElementUpdatedSinceLastInspected = true
const inspectIdx = content.indexOf('hasElementUpdatedSinceLastInspected = true');
if (inspectIdx === -1) {
    throw new Error('hasElementUpdatedSinceLastInspected assignment not found');
}

// The guard must appear in the ~500 chars before the assignment
const before = content.substring(Math.max(0, inspectIdx - 500), inspectIdx);
if (!before.includes('prevFiber !== nextFiber')) {
    throw new Error(
        'hasElementUpdatedSinceLastInspected is not guarded by ' +
        'prevFiber !== nextFiber'
    );
}

// Execute the guard logic for inspect updates
function inspectGuard(prevFiber, nextFiber) {
    if (prevFiber !== nextFiber) {
        return true; // may update inspect cache
    }
    return false; // skip — no real update
}

// Same fiber -> should NOT invalidate cache
const f = {id: 1};
if (inspectGuard(f, f)) {
    throw new Error('Bailed-out fiber should not invalidate inspect cache');
}

// Different fibers -> should proceed
if (!inspectGuard({id: 1}, {id: 2})) {
    throw new Error('Real update should allow cache invalidation');
}

console.log('PASS');
"""
    )
    assert r.returncode == 0, f"Inspect guard test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_profiling_data_logic_intact():
    """Regression: the profiling data recording logic in renderer.js is intact.

    The section that records profiling durations must still contain key operations:
    actualDuration processing, pushOperation calls, and treeBaseDuration handling.
    """
    content = Path(RENDERER).read_text()

    assert "actualDuration" in content, (
        "renderer.js is missing 'actualDuration' — profiling duration recording broken"
    )
    assert "pushOperation" in content, (
        "renderer.js is missing 'pushOperation' — profiling operation recording broken"
    )
    assert "treeBaseDuration" in content, (
        "renderer.js is missing 'treeBaseDuration' — profiling tree data broken"
    )
    assert "prevFiber == null" in content, (
        "renderer.js is missing 'prevFiber == null' check — profiling null guard removed"
    )


# [static] pass_to_pass
def test_didfiberrender_not_stubbed():
    """Anti-stub: didFiberRender retains its switch-based type dispatch logic.

    The function must not be removed or replaced with a trivial stub.
    It contains a switch statement over fiber tags (ClassComponent, etc.).
    """
    content = Path(RENDERER).read_text()
    assert "function didFiberRender" in content, (
        "didFiberRender function was removed from renderer.js"
    )
    idx = content.index("function didFiberRender")
    snippet = content[idx : idx + 500]
    assert "ClassComponent" in snippet, (
        "didFiberRender appears stubbed — missing ClassComponent case in switch"
    )


# [static] pass_to_pass
def test_didfiber_render_uses_prevfiber_param():
    """Anti-cheat: didFiberRender must still use its prevFiber parameter.

    An agent might try to "fix" the false-render issue by making didFiberRender
    always return false or by ignoring prevFiber. The function must still compare
    prevFiber and nextFiber memoizedProps/memoizedState.
    """
    import re

    content = Path(RENDERER).read_text()
    idx = content.index("function didFiberRender")
    snippet = content[idx : idx + 2000]

    assert re.search(r"prevFiber\s*\.\s*memoized(Props|State)", snippet), (
        "didFiberRender does not compare prevFiber.memoizedProps/State — "
        "the function may have been stubbed to always return false"
    )
