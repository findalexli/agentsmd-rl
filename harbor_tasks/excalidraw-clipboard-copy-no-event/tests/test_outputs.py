"""Tests for excalidraw clipboard fix.

The bug: copyTextToSystemClipboard had a return statement outside the
if (clipboardEvent) block, causing it to return early even when no clipboardEvent
was provided, thus never attempting the navigator.clipboard.writeText() fallback.

The fix:
1. Move return inside the if (clipboardEvent) block
2. Add return after successful navigator.clipboard.writeText()
3. Change let to const for plainTextEntry
4. Remove redundant plainTextEntry = undefined assignment
"""

import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/excalidraw")
CLIPBOARD_TS = REPO / "packages" / "excalidraw" / "clipboard.ts"
BUTTON_SCSS = REPO / "packages" / "excalidraw" / "components" / "FilledButton.scss"


def _extract_copyTextToSystemClipboard_function(content: str) -> str:
    """Extract the copyTextToSystemClipboard function body using brace balancing."""
    # Find the start of the function
    start_match = re.search(r'export const copyTextToSystemClipboard = async', content)
    if not start_match:
        return ""

    start_idx = start_match.start()

    # Find the opening brace of the function body (after the =>)
    # The function signature is multi-line, so we need to find the => { pattern
    arrow_match = re.search(r'\) => \{', content[start_idx:])
    if not arrow_match:
        return ""

    brace_start = start_idx + arrow_match.start() + len(") => ")  # Position at the {

    # Now balance braces to find the end of the function
    brace_count = 0
    end_idx = brace_start
    for i in range(brace_start, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break

    return content[start_idx:end_idx]


def test_clipboard_flow_control():
    """Test that return statements are in correct scopes.

    The function should:
    - Return inside if (clipboardEvent) block (when event is used)
    - Return after navigator.clipboard.writeText succeeds
    - Continue to execCommand fallback if clipboard.writeText fails
    """
    content = CLIPBOARD_TS.read_text()

    # Find the copyTextToSystemClipboard function
    func_body = _extract_copyTextToSystemClipboard_function(content)
    assert func_body, "copyTextToSystemClipboard function not found"

    # Check that there's a return inside the if (clipboardEvent) block
    # After the fix, the structure should be:
    # if (clipboardEvent) {
    #   ...
    #   return;
    # }
    # Use non-greedy match to handle nested braces properly
    clipboard_event_pattern = r'if \(clipboardEvent\) \{.*?return;.*?\}\s*\} catch'
    assert re.search(clipboard_event_pattern, func_body, re.DOTALL), \
        "Missing return inside if (clipboardEvent) block"

    # Check that there's a return after successful navigator.clipboard.writeText
    write_text_pattern = r'await navigator\.clipboard\.writeText\([^)]*\);\s*return;'
    assert re.search(write_text_pattern, func_body, re.DOTALL), \
        "Missing return after navigator.clipboard.writeText"


def test_plain_text_const():
    """Test that plainTextEntry is declared as const, not let."""
    content = CLIPBOARD_TS.read_text()

    # Find the copyTextToSystemClipboard function
    func_body = _extract_copyTextToSystemClipboard_function(content)
    assert func_body, "copyTextToSystemClipboard function not found"

    # plainTextEntry should be const, not let
    assert "const plainTextEntry" in func_body, \
        "plainTextEntry should be declared as const, not let"
    assert "let plainTextEntry" not in func_body, \
        "plainTextEntry should not be declared as let"


def test_no_redundant_undefined():
    """Test that plainTextEntry is not set to undefined after writeText."""
    content = CLIPBOARD_TS.read_text()

    # Find the copyTextToSystemClipboard function
    func_body = _extract_copyTextToSystemClipboard_function(content)
    assert func_body, "copyTextToSystemClipboard function not found"

    # Should NOT have plainTextEntry = undefined
    # (This was the old pattern that should be removed)
    assert "plainTextEntry = undefined" not in func_body, \
        "plainTextEntry should not be set to undefined - use return instead"


def test_scss_success_color():
    """Test that FilledButton.scss includes background-color for success state."""
    content = BUTTON_SCSS.read_text()

    # Find the loading/success state block
    # Should contain background-color: var(--color-success)
    # Use non-greedy match to handle nested braces properly
    pattern = r'\&\.ExcButton--status-loading,\s*\&\.ExcButton--status-success \{.*?background-color:\s*var\(--color-success\)'
    assert re.search(pattern, content, re.DOTALL), \
        "FilledButton.scss should have background-color: var(--color-success) for loading/success states"


# =============================================================================
# Pass-to-Pass Tests - Repo CI/CD Checks
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_repo_clipboard_ts_syntax():
    """Repo's clipboard.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate the file can be parsed.
    This catches syntax errors without requiring full type checking.
    """
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(CLIPBOARD_TS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"clipboard.ts has TypeScript syntax errors"


def test_repo_clipboard_test_ts_syntax():
    """Repo's clipboard.test.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate test file syntax.
    This is a repo CI gate - the test file must be syntactically valid.
    """
    test_file = REPO / "packages" / "excalidraw" / "clipboard.test.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"clipboard.test.ts has TypeScript syntax errors"


def test_repo_filledbutton_scss_syntax():
    """Repo's FilledButton.scss has valid SCSS syntax (pass_to_pass).

    Uses prettier --parser scss to validate the file can be parsed.
    This catches syntax errors without requiring full SCSS compilation.
    """
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "scss", str(BUTTON_SCSS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FilledButton.scss has SCSS syntax errors"


def test_repo_clipboard_test_syntax():
    """Repo's clipboard.test.ts has valid TypeScript syntax (pass_to_pass).

    Uses prettier --parser typescript to validate the file can be parsed.
    This catches syntax errors without requiring full type checking.
    """
    test_file = REPO / "packages" / "excalidraw" / "clipboard.test.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(test_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"clipboard.test.ts has TypeScript syntax errors"


def test_repo_constants_ts_syntax():
    """Repo's constants.ts has valid TypeScript syntax (pass_to_pass).

    The constants.ts file must be syntactically valid TypeScript.
    Uses prettier to validate without requiring full type check.
    """
    constants_file = REPO / "packages" / "common" / "src" / "constants.ts"
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", str(constants_file)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"constants.ts has TypeScript syntax errors"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
