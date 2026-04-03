"""
Task: react-fragmentinstance-dom-refactors
Repo: facebook/react @ 78f5c504b732aec0eb12514bc2cf3f27a8143dd2

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"


def _extract_js_function(src: str, func_pattern: str) -> str:
    """Extract a JS function body by tracking brace depth from a pattern match."""
    m = re.search(func_pattern, src)
    if not m:
        return ""
    start = m.start()
    # Find the opening brace
    brace_pos = src.find("{", start)
    if brace_pos == -1:
        return ""
    depth = 0
    for i in range(brace_pos, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start : i + 1]
    return src[start:]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """JS file must parse without errors (Flow-stripped)."""
    # AST-only because: Flow-typed JS, node --check fails on type syntax
    # Use a lightweight approach: check the file exists and has the expected functions
    src = Path(TARGET).read_text()
    assert len(src) > 1000, "Target file is unexpectedly small or empty"
    assert "function indexOfEventListener" in src, "indexOfEventListener function missing"
    assert "FragmentInstance.prototype.blur" in src, "FragmentInstance.prototype.blur missing"
    assert "FragmentInstance.prototype.compareDocumentPosition" in src, (
        "FragmentInstance.prototype.compareDocumentPosition missing"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral / structural checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_empty_array_early_return():
    """indexOfEventListener returns early (-1) when the listener array is empty."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    body = _extract_js_function(src, r"function indexOfEventListener\b")
    assert body, "indexOfEventListener function not found in file"
    # Must have an early-return guard for empty arrays before the loop
    assert re.search(r"\.length\s*===\s*0", body), (
        "indexOfEventListener must have an early return when eventListeners is empty"
    )
    # The early return must come before the for loop
    early_m = re.search(r"\.length\s*===\s*0", body)
    loop_m = re.search(r"\bfor\s*\(", body)
    assert early_m and loop_m and early_m.start() < loop_m.start(), (
        "Early-return check must appear before the for loop"
    )


# [pr_diff] fail_to_pass
def test_normalized_options_cached_before_loop():
    """normalizeListenerOptions(optionsOrUseCapture) is called once, before the loop."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    body = _extract_js_function(src, r"function indexOfEventListener\b")
    assert body, "indexOfEventListener function not found in file"

    # A cached assignment must exist before the loop
    cache_m = re.search(r"(?:const|let|var)\s+\w+\s*=\s*normalizeListenerOptions\s*\(\s*optionsOrUseCapture\s*\)", body)
    assert cache_m, (
        "normalizeListenerOptions(optionsOrUseCapture) must be called once before the loop "
        "and stored in a variable"
    )

    loop_m = re.search(r"\bfor\s*\(", body)
    assert loop_m, "for loop not found in indexOfEventListener"
    assert cache_m.start() < loop_m.start(), (
        "Cached normalizeListenerOptions call must appear before the for loop, not inside it"
    )

    # The loop body must NOT call normalizeListenerOptions(optionsOrUseCapture) directly
    loop_body = body[loop_m.start() :]
    assert not re.search(
        r"normalizeListenerOptions\s*\(\s*optionsOrUseCapture\s*\)", loop_body
    ), (
        "normalizeListenerOptions(optionsOrUseCapture) must not be called inside the loop; "
        "use the cached normalizedOptions instead"
    )


# [pr_diff] fail_to_pass
def test_blur_early_exit_when_active_not_in_parent():
    """blur() checks whether the active element is inside the fragment's parent before traversing."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    body = _extract_js_function(
        src, r"FragmentInstance\.prototype\.blur\s*=\s*function"
    )
    assert body, "FragmentInstance.prototype.blur not found in file"
    # Must call .contains() to guard the traversal
    assert ".contains(" in body, (
        "blur() must call .contains(activeElement) to skip traversal when the active element "
        "is not inside the fragment parent"
    )
    # The guard must return early (skip traversal) on negative condition
    assert "return" in body, (
        "blur() must have an early return when activeElement is not contained"
    )


# [pr_diff] fail_to_pass
def test_active_element_passed_to_traversal_callback():
    """blur() passes the pre-fetched activeElement to traverseFragmentInstance."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    body = _extract_js_function(
        src, r"FragmentInstance\.prototype\.blur\s*=\s*function"
    )
    assert body, "FragmentInstance.prototype.blur not found in file"
    # Find the traverseFragmentInstance call
    call_m = re.search(r"traverseFragmentInstance\s*\([^)]+\)", body)
    assert call_m, "traverseFragmentInstance call not found in blur()"
    call = call_m.group(0)
    assert "activeElement" in call, (
        "traverseFragmentInstance must receive activeElement as an argument "
        "(avoids re-querying DOM on every child)"
    )


# [pr_diff] fail_to_pass
def test_text_nodes_skipped_in_blur_traversal():
    """blurActiveElementWithinFragment skips HostText nodes (they can't be focused)."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    body = _extract_js_function(src, r"function blurActiveElementWithinFragment\b")
    assert body, "blurActiveElementWithinFragment function not found in file"
    assert "HostText" in body, (
        "blurActiveElementWithinFragment must skip text nodes by checking child.tag === HostText"
    )


# [pr_diff] fail_to_pass
def test_redundant_first_instance_removed():
    """compareDocumentPosition no longer declares a redundant firstInstance variable."""
    # AST-only because: Flow-typed JS in large React monorepo, not importable in isolation
    src = Path(TARGET).read_text()
    # The old code duplicated children[0] lookup: firstElement and then firstInstance
    assert "const firstInstance = getInstanceFromHostFiber" not in src, (
        "Redundant 'const firstInstance' variable must be removed from compareDocumentPosition; "
        "use the existing firstNode/firstElement reference instead"
    )
