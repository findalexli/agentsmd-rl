"""
Tests for superset-playwright-timeout-propagate task.

These tests verify that PlaywrightTimeout exceptions are properly propagated
from WebDriverPlaywright.get_screenshot() instead of being swallowed.

The key bug is that the except PlaywrightTimeout block used 'pass' (swallowing
the exception) instead of 'raise' (propagating it to the caller).
"""
import re
import ast
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
WEBDRIVER_PATH = REPO / "superset" / "utils" / "webdriver.py"


def test_syntax_valid():
    """
    Pass-to-pass: webdriver.py must have valid Python syntax.
    """
    content = WEBDRIVER_PATH.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        assert False, f"Syntax error in webdriver.py: {e}"


def test_outer_playwright_timeout_not_swallowed():
    """
    Fail-to-pass: Verify there is no 'pass' immediately after except PlaywrightTimeout.

    This is a secondary check using regex to ensure the buggy pattern is fixed.
    """
    content = WEBDRIVER_PATH.read_text()

    # Pattern matches: except PlaywrightTimeout: followed by pass (with optional comment)
    buggy_pattern = r'except\s+PlaywrightTimeout\s*:\s*\n\s*#[^\n]*\n\s*pass'

    match = re.search(buggy_pattern, content)
    if match:
        assert False, (
            "Found buggy pattern: 'except PlaywrightTimeout:' followed by 'pass'.\n"
            f"Match: {match.group()}\n"
            "This swallows the exception. It should use 'raise' instead."
        )


def test_playwright_timeout_raises_exception():
    """
    Fail-to-pass: The except block should re-raise the PlaywrightTimeout.

    This test verifies the fix is present by checking for 'raise' after
    the except PlaywrightTimeout clause.
    """
    content = WEBDRIVER_PATH.read_text()

    # Pattern matches: except PlaywrightTimeout: followed by raise
    fixed_pattern = r'except\s+PlaywrightTimeout\s*:\s*\n\s*raise\b'

    match = re.search(fixed_pattern, content)
    assert match, (
        "Could not find the fixed pattern: 'except PlaywrightTimeout:' followed by 'raise'.\n"
        "The PlaywrightTimeout exception must be re-raised to propagate to the caller."
    )


def test_get_screenshot_method_exists():
    """
    Pass-to-pass: The get_screenshot method must exist in WebDriverPlaywright class.
    """
    content = WEBDRIVER_PATH.read_text()

    # Parse AST to find the method
    tree = ast.parse(content)

    found_class = False
    found_method = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'WebDriverPlaywright':
            found_class = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == 'get_screenshot':
                    found_method = True
                    break

    assert found_class, "WebDriverPlaywright class not found in webdriver.py"
    assert found_method, "get_screenshot method not found in WebDriverPlaywright class"


def test_playwright_error_handling_preserved():
    """
    Pass-to-pass: The except PlaywrightError block should still be present.

    The fix only changes PlaywrightTimeout handling. The general PlaywrightError
    handling should remain intact for other errors.
    """
    content = WEBDRIVER_PATH.read_text()

    # Check that PlaywrightError handling is still present
    assert 'except PlaywrightError:' in content, (
        "except PlaywrightError: block not found. "
        "This block should be preserved for handling non-timeout Playwright errors."
    )

    # Verify the error is logged (not silently swallowed like the old timeout was)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'except PlaywrightError:' in line:
            # Check the next few lines for logger call
            for j in range(i + 1, min(i + 5, len(lines))):
                if 'logger.exception' in lines[j]:
                    return  # Found the logging call
            break

    assert False, "PlaywrightError handler should log the exception with logger.exception"


def test_finally_block_closes_browser():
    """
    Pass-to-pass: The finally block should still close the browser.

    The buggy comment said "raise again for the finally block" but this was
    incorrect - finally blocks run regardless of whether an exception is raised.
    The fix removes this misleading comment and the browser cleanup should still work.
    """
    content = WEBDRIVER_PATH.read_text()

    # Check for browser.close() in finally block
    # The pattern should be: finally: ... browser.close()
    if 'finally:' in content and 'browser.close()' in content:
        # Verify browser.close() comes after finally
        finally_idx = content.find('finally:')
        close_idx = content.find('browser.close()', finally_idx)
        assert close_idx > finally_idx, (
            "browser.close() should be in the finally block after 'finally:'"
        )
    else:
        # If there's no explicit finally block, check for context manager usage
        assert 'with sync_playwright()' in content or 'browser.close()' in content, (
            "Browser cleanup mechanism not found"
        )


def test_no_misleading_comment():
    """
    Fail-to-pass: The misleading comment should be removed.

    The buggy code had a comment: "raise again for the finally block, but handled above"
    This comment was incorrect (finally runs regardless) and misleading.
    """
    content = WEBDRIVER_PATH.read_text()

    misleading_phrases = [
        "raise again for the finally block",
        "but handled above",
    ]

    for phrase in misleading_phrases:
        assert phrase not in content, (
            f"Found misleading comment phrase: '{phrase}'\n"
            "This comment is incorrect - finally blocks run regardless of exception handling. "
            "It should be removed as part of the fix."
        )


def test_webdriver_imports_valid():
    """
    Pass-to-pass: The webdriver module should have valid import structure.
    """
    content = WEBDRIVER_PATH.read_text()
    tree = ast.parse(content)

    # Check that required imports are present
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # The webdriver module should import from these modules
    assert any('logging' in imp for imp in imports), "logging import missing"
    assert any('abc' in imp for imp in imports), "abc import missing"


def test_ruff_check_webdriver():
    """
    Pass-to-pass: ruff lint check passes on webdriver.py.

    This runs the repo's actual linter (ruff) on the modified file.
    """
    r = subprocess.run(
        ["ruff", "check", "superset/utils/webdriver.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr[-500:]}"


def test_ruff_format_webdriver():
    """
    Pass-to-pass: ruff format check passes on webdriver.py.

    This verifies the file is properly formatted according to repo standards.
    """
    r = subprocess.run(
        ["ruff", "format", "--check", "superset/utils/webdriver.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr[-500:]}"


def test_python_compile_webdriver():
    """
    Pass-to-pass: Python byte-compilation succeeds for webdriver.py.

    This runs the Python compiler to verify syntax validity beyond AST parsing.
    """
    r = subprocess.run(
        ["python", "-m", "py_compile", "superset/utils/webdriver.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"
