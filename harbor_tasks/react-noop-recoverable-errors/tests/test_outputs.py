"""
Task: react-noop-recoverable-errors
Repo: facebook/react @ 23b2d8514f13f109b980b0a1f4f3aab906ad51d0

Fix: Enable console.error for recoverable errors in the noop renderer
instead of leaving it as a commented-out TODO.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/react"
TARGET = f"{REPO}/packages/react-noop-renderer/src/createReactNoop.js"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_console_error_enabled():
    """onRecoverableError should call console.error(error)."""
    src = Path(TARGET).read_text()
    # Find the onRecoverableError function and check it calls console.error
    in_func = False
    found_console_error = False
    for line in src.split('\n'):
        if 'function onRecoverableError' in line:
            in_func = True
        if in_func and 'console.error(error)' in line and not line.strip().startswith('//'):
            found_console_error = True
            break
        if in_func and line.strip().startswith('}') and not 'error' in line:
            break
    assert found_console_error, \
        "onRecoverableError should have uncommented console.error(error)"


def test_todo_comment_removed():
    """The TODO comment about enabling console.error should be removed."""
    src = Path(TARGET).read_text()
    assert "TODO: Turn this on once tests are fixed" not in src, \
        "TODO comment should be removed"


def test_eslint_disable_present():
    """eslint-disable comment for no-production-logging should be present."""
    src = Path(TARGET).read_text()
    assert "react-internal/no-production-logging" in src, \
        "Should have eslint-disable for no-production-logging"


def test_function_has_type_annotation():
    """onRecoverableError should have type annotations."""
    src = Path(TARGET).read_text()
    assert "onRecoverableError(error: mixed): void" in src or \
           "onRecoverableError(error:" in src, \
        "onRecoverableError should have type annotation"
