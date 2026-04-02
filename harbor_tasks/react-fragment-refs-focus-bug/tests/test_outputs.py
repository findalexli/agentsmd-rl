"""
Task: react-fragment-refs-focus-bug
Repo: facebook/react @ 8f4150605449efe909822d8b20fe529d85851afe
PR:   36010

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only because: target is JavaScript DOM code; cannot be imported or
# executed from Python without a browser/JSDOM environment. Checks use
# text/regex pattern matching on the source file.

import re
from pathlib import Path

REPO = "/workspace/react"
TARGET = REPO + "/packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js"


def _src() -> str:
    return Path(TARGET).read_text()


def _fn_body() -> str:
    """Extract the body of setFocusIfFocusable from the source file."""
    src = _src()
    # Match from the function export to the closing brace that balances it.
    # We find the function start, then walk braces.
    m = re.search(r'export function setFocusIfFocusable\b[^{]*\{', src)
    assert m, "setFocusIfFocusable not found in source"
    start = m.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    return src[start:i - 1]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists():
    """ReactFiberConfigDOM.js must exist and export setFocusIfFocusable."""
    p = Path(TARGET)
    assert p.exists(), f"File not found: {TARGET}"
    assert "setFocusIfFocusable" in p.read_text(), (
        "setFocusIfFocusable not found in ReactFiberConfigDOM.js"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_already_focused_early_return():
    """setFocusIfFocusable must return true immediately when element is already activeElement."""
    # AST-only because: JavaScript DOM code; can't execute without browser env.
    src = _src()
    # The fix adds: if (element.ownerDocument.activeElement === element) { return true; }
    assert re.search(
        r'ownerDocument\.activeElement\s*===\s*element',
        src,
    ), (
        "Missing early-return check: "
        "`element.ownerDocument.activeElement === element` not found"
    )


# [pr_diff] fail_to_pass
def test_early_return_before_try():
    """The already-focused check must appear before the try block, not inside it."""
    # AST-only because: JavaScript DOM code; can't execute without browser env.
    fn = _fn_body()
    active_m = re.search(r'ownerDocument\.activeElement\s*===\s*element', fn)
    try_m = re.search(r'\btry\s*\{', fn)
    assert active_m, "activeElement check not found in setFocusIfFocusable body"
    assert try_m, "try block not found in setFocusIfFocusable body"
    assert active_m.start() < try_m.start(), (
        "already-focused check must come before the try block; "
        f"found at offset {active_m.start()} but try at {try_m.start()}"
    )


# [pr_diff] fail_to_pass
def test_document_level_capture_listener():
    """Focus listener must use ownerDocument (capture phase), not element directly."""
    # AST-only because: JavaScript DOM code; can't execute without browser env.
    src = _src()
    # New: ownerDocument.addEventListener('focus', handleFocus, true)
    assert re.search(
        r'ownerDocument\.addEventListener\(\s*[\'"]focus[\'"]\s*,\s*handleFocus\s*,\s*true\s*\)',
        src,
    ), (
        "Missing document-level capture listener: "
        "`ownerDocument.addEventListener('focus', handleFocus, true)` not found"
    )
    # Old element-level listener must be gone
    old = re.search(
        r'element\.addEventListener\(\s*[\'"]focus[\'"]\s*,\s*handleFocus\s*\)',
        src,
    )
    assert not old, (
        "Old element-level focus listener still present; "
        "must use ownerDocument with capture=true instead"
    )


# [pr_diff] fail_to_pass
def test_capture_cleanup():
    """Listener removal must also use ownerDocument with the capture flag."""
    # AST-only because: JavaScript DOM code; can't execute without browser env.
    src = _src()
    assert re.search(
        r'ownerDocument\.removeEventListener\(\s*[\'"]focus[\'"]\s*,\s*handleFocus\s*,\s*true\s*\)',
        src,
    ), (
        "Missing: `ownerDocument.removeEventListener('focus', handleFocus, true)` not found; "
        "cleanup must match the capture flag used when adding the listener"
    )
    # Old element-level removal must be gone
    old = re.search(
        r'element\.removeEventListener\(\s*[\'"]focus[\'"]\s*,\s*handleFocus\s*\)',
        src,
    )
    assert not old, (
        "Old element.removeEventListener still present; "
        "must use ownerDocument.removeEventListener with capture=true"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_not_stub():
    """setFocusIfFocusable must have a non-trivial implementation."""
    # AST-only because: JavaScript DOM code; can't execute without browser env.
    fn = _fn_body()
    assert 'didFocus' in fn, "Function must use didFocus variable"
    assert 'try' in fn, "Function must have try block"
    assert re.search(r'\breturn\s+(didFocus|true|false)', fn), (
        "Function must return a meaningful value (didFocus or true/false)"
    )
    # Not just return false or return null
    meaningful_lines = [
        l.strip() for l in fn.splitlines()
        if l.strip() and not l.strip().startswith('//')
    ]
    assert len(meaningful_lines) >= 8, (
        f"Function body suspiciously short ({len(meaningful_lines)} lines); likely a stub"
    )
