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


def test_clipboard_flow_control():
    """Test that return statements are in correct scopes.

    The function should:
    - Return inside if (clipboardEvent) block (when event is used)
    - Return after navigator.clipboard.writeText succeeds
    - Continue to execCommand fallback if clipboard.writeText fails
    """
    content = CLIPBOARD_TS.read_text()

    # Find the copyTextToSystemClipboard function
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async.*?\n\}(?=\n|$)',
        content,
        re.DOTALL
    )
    assert func_match, "copyTextToSystemClipboard function not found"
    func_body = func_match.group(0)

    # Check that there's a return inside the if (clipboardEvent) block
    # After the fix, the structure should be:
    # if (clipboardEvent) {
    #   ...
    #   return;
    # }
    clipboard_event_pattern = r'if \(clipboardEvent\) \{[^}]*return;[^}]*\}'
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
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async.*?\n\}(?=\n|$)',
        content,
        re.DOTALL
    )
    assert func_match, "copyTextToSystemClipboard function not found"
    func_body = func_match.group(0)

    # plainTextEntry should be const, not let
    assert "const plainTextEntry" in func_body, \
        "plainTextEntry should be declared as const, not let"
    assert "let plainTextEntry" not in func_body, \
        "plainTextEntry should not be declared as let"


def test_no_redundant_undefined():
    """Test that plainTextEntry is not set to undefined after writeText."""
    content = CLIPBOARD_TS.read_text()

    # Find the copyTextToSystemClipboard function
    func_match = re.search(
        r'export const copyTextToSystemClipboard = async.*?\n\}(?=\n|$)',
        content,
        re.DOTALL
    )
    assert func_match, "copyTextToSystemClipboard function not found"
    func_body = func_match.group(0)

    # Should NOT have plainTextEntry = undefined
    # (This was the old pattern that should be removed)
    assert "plainTextEntry = undefined" not in func_body, \
        "plainTextEntry should not be set to undefined - use return instead"


def test_scss_success_color():
    """Test that FilledButton.scss includes background-color for success state."""
    content = BUTTON_SCSS.read_text()

    # Find the loading/success state block
    # Should contain background-color: var(--color-success)
    pattern = r'\&\.ExcButton--status-loading,\s*\&\.ExcButton--status-success \{[^}]*background-color:\s*var\(--color-success\)'
    assert re.search(pattern, content, re.DOTALL), \
        "FilledButton.scss should have background-color: var(--color-success) for loading/success states"


# =============================================================================
# Pass-to-Pass Tests - Repo CI/CD Checks
# These ensure the fix doesn't break existing functionality
# =============================================================================


def test_repo_clipboard_ts_syntax():
    """Repo's clipboard.ts has valid TypeScript syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "typescript", "--check", str(CLIPBOARD_TS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"clipboard.ts has invalid TypeScript syntax:\n{r.stderr[-500:]}"


def test_repo_filledbutton_scss_syntax():
    """Repo's FilledButton.scss has valid SCSS syntax (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--no-config", "--parser", "scss", "--check", str(BUTTON_SCSS)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FilledButton.scss has invalid SCSS syntax:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
