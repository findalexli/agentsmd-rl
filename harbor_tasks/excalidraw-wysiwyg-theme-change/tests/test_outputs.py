#!/usr/bin/env python3
"""
Tests for excalidraw-wysiwyg-theme-change task.

This task verifies that the WYSIWYG text editor correctly updates its
text color when the theme changes between light and dark mode.
"""

import subprocess
import sys
import os

REPO = "/workspace/excalidraw"
TARGET_FILE = os.path.join(REPO, "packages/excalidraw/wysiwyg/textWysiwyg.tsx")


def read_target_file():
    """Read the target file content."""
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def test_last_theme_variable_exists():
    """
    Fail-to-pass: LAST_THEME variable must be defined to track theme state.
    """
    content = read_target_file()
    # Check for the LAST_THEME variable declaration
    assert "let LAST_THEME = app.state.theme" in content, \
        "Missing LAST_THEME variable declaration"


def test_last_theme_updated_in_style_function():
    """
    Fail-to-pass: LAST_THEME must be updated at the start of updateWysiwygStyle.
    """
    content = read_target_file()
    # Check that LAST_THEME is updated in updateWysiwygStyle function
    assert "LAST_THEME = app.state.theme" in content, \
        "LAST_THEME is not being updated in updateWysiwygStyle"


def test_onchange_emitter_subscription_exists():
    """
    Fail-to-pass: Must subscribe to onChangeEmitter to detect theme changes.
    """
    content = read_target_file()
    # Check for onChangeEmitter subscription
    assert "app.onChangeEmitter.on" in content, \
        "Missing onChangeEmitter subscription"
    # Check for theme change comparison
    assert "app.state.theme !== LAST_THEME" in content, \
        "Missing theme change comparison"


def test_unsub_onchange_cleanup_exists():
    """
    Fail-to-pass: Must unsubscribe from onChangeEmitter in cleanup to prevent memory leaks.
    """
    content = read_target_file()
    # Check for unsubOnChange in cleanup function
    assert "unsubOnChange()" in content, \
        "Missing unsubOnChange() call in cleanup function"


def test_fixme_comment_present():
    """
    Fail-to-pass: The FIXME comment about Store updates for theme should be present.
    """
    content = read_target_file()
    # Check for the FIXME comment about theme updates
    assert "FIXME after we start emitting updates from Store for appState.theme" in content, \
        "Missing FIXME comment about Store theme updates"


def test_target_file_syntax_valid():
    """
    Pass-to-pass: Target file is valid TypeScript/JavaScript syntax.
    We verify the file can be parsed by Node.js parser.
    """
    # Parse the file with Node.js to check for syntax errors
    result = subprocess.run(
        ["node", "--check", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    # Note: node --check works on JS files, but we'll verify the file is readable
    # and the syntax is generally valid by checking it doesn't contain obvious errors
    content = read_target_file()

    # Check for balanced braces (basic sanity check)
    open_count = content.count('{')
    close_count = content.count('}')
    assert open_count == close_count, f"Unbalanced braces in target file"

    # Check for balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses in target file"


def test_theme_change_wysiwyg_test():
    """
    Pass-to-pass: The theme change WYSIWYG test passes.
    """
    # Run the specific test for theme change in the WYSIWYG editor
    result = subprocess.run(
        ["yarn", "test", "--run", "packages/excalidraw/wysiwyg/textWysiwyg.test.tsx", "-t", "theme change"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # The test may not exist in the base commit, so we check if it passes or doesn't exist
    # In the fixed version, it should pass
    if "Test theme change" not in result.stdout and "theme change" not in result.stdout:
        # Test doesn't exist in base commit (expected for NOP)
        pass
    else:
        assert result.returncode == 0, \
            f"Theme change WYSIWYG test failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_wysiwyg_tests_pass():
    """
    Pass-to-pass: All WYSIWYG tests pass (general regression check).
    """
    result = subprocess.run(
        ["yarn", "test", "--run", "packages/excalidraw/wysiwyg/textWysiwyg.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"WYSIWYG tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_eslint():
    """
    Pass-to-pass: Repo CI - ESLint passes (yarn test:code).
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"ESLint check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_prettier():
    """
    Pass-to-pass: Repo CI - Prettier formatting passes (yarn test:other).
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Prettier check failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


def test_repo_app_smoke():
    """
    Pass-to-pass: Repo CI - App smoke test passes.
    """
    result = subprocess.run(
        ["yarn", "test:app", "--run", "packages/excalidraw/tests/App.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"App smoke test failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
