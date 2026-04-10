"""Tests for SetTitleCallbackProcessor polling fix.

This tests that:
1. The polling constants are correctly defined (_POLL_DELAY_S = 3, _NUM_POLL_ATTEMPTS = 4)
2. The _poll_for_title function exists and is extracted from the main processor
3. The logging level changed from debug to warning for failed polls
"""

import ast
import sys
from pathlib import Path

REPO = Path("/workspace/OpenHands")
TARGET_FILE = REPO / "openhands" / "app_server" / "event_callback" / "set_title_callback_processor.py"


def test_polling_constants_exist():
    """Check that _POLL_DELAY_S and _NUM_POLL_ATTEMPTS constants exist with correct values."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_delay = False
    found_attempts = False
    delay_value = None
    attempts_value = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "_POLL_DELAY_S":
                        found_delay = True
                        if isinstance(node.value, ast.Constant):
                            delay_value = node.value.value
                    elif target.id == "_NUM_POLL_ATTEMPTS":
                        found_attempts = True
                        if isinstance(node.value, ast.Constant):
                            attempts_value = node.value.value

    assert found_delay, "_POLL_DELAY_S constant not found"
    assert found_attempts, "_NUM_POLL_ATTEMPTS constant not found"
    assert delay_value == 3, f"_POLL_DELAY_S should be 3, got {delay_value}"
    assert attempts_value == 4, f"_NUM_POLL_ATTEMPTS should be 4, got {attempts_value}"


def test_total_polling_time():
    """Check that total polling time is ~12 seconds (4 attempts x 3 seconds)."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    delay_value = None
    attempts_value = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "_POLL_DELAY_S":
                        if isinstance(node.value, ast.Constant):
                            delay_value = node.value.value
                    elif target.id == "_NUM_POLL_ATTEMPTS":
                        if isinstance(node.value, ast.Constant):
                            attempts_value = node.value.value

    assert delay_value is not None, "_POLL_DELAY_S not found"
    assert attempts_value is not None, "_NUM_POLL_ATTEMPTS not found"

    total_time = delay_value * attempts_value
    assert total_time == 12, f"Total polling time should be 12 seconds (4x3), got {total_time}"


def test_poll_for_title_function_exists():
    """Check that _poll_for_title function is extracted and exists."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_function = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            if node.name == "_poll_for_title":
                found_function = True
                # Check function has correct parameters
                args = [arg.arg for arg in node.args.args]
                assert "httpx_client" in args, "_poll_for_title missing httpx_client parameter"
                assert "url" in args, "_poll_for_title missing url parameter"
                assert "session_api_key" in args, "_poll_for_title missing session_api_key parameter"
                break

    assert found_function, "_poll_for_title async function not found - polling logic should be extracted"


def test_old_polling_tuple_removed():
    """Check that the old _TITLE_POLL_DELAYS_S tuple is removed."""
    source = TARGET_FILE.read_text()

    assert "_TITLE_POLL_DELAYS_S" not in source, \
        "Old _TITLE_POLL_DELAYS_S constant should be removed (replaced by _POLL_DELAY_S and _NUM_POLL_ATTEMPTS)"


def test_logging_level_changed_to_warning():
    """Check that logging level changed from debug to warning for failed polls."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    # Find the _poll_for_title function and check for warning log
    found_warning = False
    found_debug_in_poll = False

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_poll_for_title":
            # Look for _logger.warning calls in this function
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute):
                    if child.attr == "warning":
                        found_warning = True
                    # Check it's not using debug
                    if child.attr == "debug":
                        found_debug_in_poll = True

    assert found_warning, \
        "_logger.warning not found in _poll_for_title - logging level should be warning for failed polls"
    assert not found_debug_in_poll, \
        "_logger.debug should not be used in _poll_for_title for error logging - use warning instead"


def test_poll_for_title_used_in_processor():
    """Check that the main processor uses _poll_for_title instead of inline polling."""
    source = TARGET_FILE.read_text()
    tree = ast.parse(source)

    found_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "_poll_for_title":
                found_call = True
                break
            # Also check for await _poll_for_title()
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "_poll_for_title":
                    found_call = True
                    break

    assert found_call, \
        "_poll_for_title is not being called - the main processor should use the extracted function"


def test_repo_unit_tests_pass():
    """Check that the existing unit tests for SetTitleCallbackProcessor pass."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/unit/app_server/test_set_title_callback_processor.py",
            "-v",
            "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_imports_work():
    """Check that the module can be imported without errors."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable, "-c",
            "from openhands.app_server.event_callback.set_title_callback_processor import SetTitleCallbackProcessor"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Import failed:\n{result.stderr}"


# ============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These tests verify that the repo's CI/CD checks pass on the base commit
# and continue to pass after the fix is applied.
# ============================================================================

def test_repo_ruff_linting_modified_file():
    """Ruff linting passes on the modified set_title_callback_processor.py file (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            "ruff", "check",
            "--config", "dev_config/python/ruff.toml",
            "openhands/app_server/event_callback/set_title_callback_processor.py"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Ruff linting on modified file failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_linting():
    """Repo's ruff linting passes on openhands/ directory (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            "ruff", "check",
            "--config", "dev_config/python/ruff.toml",
            "openhands/"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_format_check():
    """Ruff format check passes on the modified file (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            "ruff", "format",
            "--config", "dev_config/python/ruff.toml",
            "--check",
            "openhands/app_server/event_callback/set_title_callback_processor.py"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_python_syntax():
    """Python syntax check passes on the modified file (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable, "-m", "py_compile",
            "openhands/app_server/event_callback/set_title_callback_processor.py"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Python syntax check failed:\n{result.stderr}"


def test_repo_unit_tests_modified_file():
    """Unit tests for the modified SetTitleCallbackProcessor pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/unit/app_server/test_set_title_callback_processor.py",
            "-v", "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Unit tests for modified file failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_repo_app_server_unit_tests():
    """Repo's app_server unit tests pass (pass_to_pass)."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/unit/app_server/",
            "-v", "--tb=short", "-x"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    assert result.returncode == 0, \
        f"App server unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_repo_precommit_hooks():
    """Repo's pre-commit hooks pass (pass_to_pass) - runs ruff, mypy, format checks."""
    import subprocess

    result = subprocess.run(
        [
            "pre-commit", "run", "--all-files",
            "--show-diff-on-failure",
            "--config", "./dev_config/python/.pre-commit-config.yaml"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Pre-commit hooks failed:\n{result.stdout}\n{result.stderr}"
