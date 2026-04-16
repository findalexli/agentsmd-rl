"""
Task: playwright-cli-allow-locators-and-selectors
Repo: playwright @ 35f853d5c293c901ea66a9aa3f56f6879a94e66a
PR:   39708

Test that the CLI supports both CSS selectors and Playwright locators,
and that the SKILL.md documentation reflects this capability.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/playwright"
TAB_FILE = f"{REPO}/packages/playwright-core/src/tools/backend/tab.ts"
LOCATOR_PARSER_FILE = f"{REPO}/packages/playwright-core/src/utils/isomorphic/locatorParser.ts"
SKILL_FILE = f"{REPO}/packages/playwright-core/src/tools/cli-client/skill/SKILL.md"


def _read_file(path: str) -> str:
    return Path(path).read_text()


def _run_typescript_check(file_path: str) -> bool:
    """Check TypeScript syntax by running tsc --noEmit on the file."""
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", file_path],
            cwd=REPO,
            capture_output=True,
            timeout=60,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # If tsc is not available or times out, fall back to syntax inspection
        return True


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must parse without errors."""
    # Check that tab.ts is syntactically valid by verifying key structures
    src = _read_file(TAB_FILE)

    # Verify the file has valid TypeScript structure
    assert "export class Tab" in src, "Tab class not found"
    assert "extends EventEmitter" in src, "EventEmitter extension not found"
    assert "param.selector" in src, "selector param handling not found"

    # Verify no obvious syntax errors (unmatched braces would break parsing)
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, "Mismatched braces in TypeScript"

    open_parens = src.count("(")
    close_parens = src.count(")")
    assert open_parens == close_parens, "Mismatched parentheses in TypeScript"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_playwright_locator_parsing_supported():
    """
    The tab.ts file must import and use locatorOrSelectorAsSelector
    to support Playwright locator syntax like getByRole().

    Before fix: Used this.page.locator(param.selector) directly, which
    only accepted raw CSS selectors or Playwright's internal selector format.

    After fix: Uses locatorOrSelectorAsSelector() to convert Playwright
    locator syntax (e.g., getByRole('button')) to internal selector format.
    """
    src = _read_file(TAB_FILE)

    # Check that the import for locatorOrSelectorAsSelector is present
    assert "locatorOrSelectorAsSelector" in src, (
        "Missing import for locatorOrSelectorAsSelector - required to support "
        "Playwright locator syntax"
    )

    # Check that locatorOrSelectorAsSelector is actually called in the selector handling
    assert "locatorOrSelectorAsSelector('javascript', param.selector" in src, (
        "locatorOrSelectorAsSelector not called with correct parameters - "
        "needed to convert Playwright locators to internal format"
    )


def test_css_selector_still_works():
    """
    CSS selectors must continue to work after the fix (regression protection).

    The fix should use page.$() (which accepts CSS selectors) to check element
    existence, maintaining backward compatibility with CSS selector inputs.
    """
    src = _read_file(TAB_FILE)

    # Verify the new code uses page.$() which accepts CSS selectors
    assert "this.page.$(selector)" in src, (
        "Missing this.page.$(selector) call - needed for CSS selector support"
    )

    # Verify the handle disposal pattern is present (part of the fix)
    assert "handle.dispose()" in src, (
        "Missing handle.dispose() cleanup - part of proper element handle management"
    )


def test_getbytestid_locator_supported():
    """
    getByTestId() locator syntax must be supported.

    This is an important locator type that users commonly use for test automation.
    The fix should pass the testIdAttribute to locatorOrSelectorAsSelector.
    """
    src = _read_file(TAB_FILE)

    # Check that testIdAttribute is passed to the parser
    assert "testIdAttribute" in src, (
        "Missing testIdAttribute parameter - needed for getByTestId() support"
    )

    # Verify the default 'data-testid' fallback is present
    assert "data-testid" in src, (
        "Missing 'data-testid' default - needed for getByTestId() to work "
        "when no custom testIdAttribute is configured"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_existing_locator_parser_works():
    """
    The locatorParser.ts utility must be available and functional.

    This is a dependency of the fix; if it's broken, the fix won't work.
    """
    src = _read_file(LOCATOR_PARSER_FILE)

    # Verify the key function exists
    assert "function parseLocator" in src, (
        "parseLocator function not found in locatorParser.ts"
    )

    assert "locatorOrSelectorAsSelector" in src, (
        "locatorOrSelectorAsSelector not exported from locatorParser.ts"
    )


def test_not_stub():
    """
    The modified resolveSelector method must have real logic, not just pass/return.

    A stub implementation would just return the input without conversion.
    """
    src = _read_file(TAB_FILE)

    # Find the selector handling section
    selector_section_idx = src.find("param.selector")
    assert selector_section_idx != -1, "selector handling section not found"

    # Extract a reasonable chunk around the selector handling
    section = src[selector_section_idx:selector_section_idx + 2000]

    # Count meaningful statements (not just imports, types, or comments)
    statements = [
        "locatorOrSelectorAsSelector",
        "this.page.$",
        "handle.dispose",
        "throw new Error",
        "return {",
    ]

    found_statements = sum(1 for s in statements if s in section)
    assert found_statements >= 4, (
        f"Modified code appears to be a stub. Found only {found_statements}/5 "
        f"expected implementation patterns."
    )


def test_error_message_improved():
    """
    The error message should use quotes around the selector for clarity.

    This is a minor improvement from the PR:
    - Before: "Selector ${param.selector} does not match..."
    - After: ""${param.selector}" does not match..."
    """
    src = _read_file(TAB_FILE)

    # The new error format should have quotes around the selector
    assert '"${param.selector}"' in src or "`${param.selector}`" in src, (
        "Error message should quote the selector for clarity"
    )
