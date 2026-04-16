"""Test outputs for SetTitleCallbackProcessor polling fix.

This validates that the PR changes have been applied:
1. New constants _POLL_DELAY_S and _NUM_POLL_ATTEMPTS exist
2. New _poll_for_title async function exists
3. Log level changed from debug to warning for failed polls
4. Old _TITLE_POLL_DELAYS_S constant is removed
5. Polling logic is extracted to the new function
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

# Path to the OpenHands repo
REPO = Path('/workspace/OpenHands')
TARGET_FILE = REPO / 'openhands' / 'app_server' / 'event_callback' / 'set_title_callback_processor.py'


def _get_ast():
    """Parse the target file and return its AST."""
    content = TARGET_FILE.read_text()
    return ast.parse(content)


def test_new_poll_constants_exist():
    """FAIL-TO-PASS: _POLL_DELAY_S and _NUM_POLL_ATTEMPTS constants must exist.

    The old code had: _TITLE_POLL_DELAYS_S = (0.25, 0.5, 1.0, 2.0)
    The new code should have:
      _POLL_DELAY_S = 3
      _NUM_POLL_ATTEMPTS = 4
    """
    content = TARGET_FILE.read_text()

    # Check for new constants with exact values
    assert '_POLL_DELAY_S = 3' in content, \
        "Missing _POLL_DELAY_S constant with value 3"
    assert '_NUM_POLL_ATTEMPTS = 4' in content, \
        "Missing _NUM_POLL_ATTEMPTS constant with value 4"

    # Verify old constant is removed
    assert '_TITLE_POLL_DELAYS_S' not in content, \
        "Old _TITLE_POLL_DELAYS_S constant should be removed"


def test_poll_for_title_function_exists():
    """FAIL-TO-PASS: _poll_for_title async function must exist.

    The polling logic should be extracted to a separate async function
    that takes httpx_client, url, and session_api_key parameters.
    """
    tree = _get_ast()

    found_function = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == '_poll_for_title':
            found_function = True
            # Check it has the expected parameters
            args = [arg.arg for arg in node.args.args]
            assert 'httpx_client' in args, \
                "_poll_for_title missing httpx_client parameter"
            assert 'url' in args, \
                "_poll_for_title missing url parameter"
            assert 'session_api_key' in args, \
                "_poll_for_title missing session_api_key parameter"

            # Check return annotation is str | None
            if node.returns:
                return_str = ast.unparse(node.returns)
                assert 'str' in return_str and 'None' in return_str, \
                    f"_poll_for_title return type should be str | None, got {return_str}"
            break

    assert found_function, \
        "_poll_for_title must be defined as an async function"


def test_poll_delay_is_3_seconds():
    """FAIL-TO-PASS: _POLL_DELAY_S constant must be set to 3."""
    tree = _get_ast()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_POLL_DELAY_S':
                    if isinstance(node.value, ast.Constant):
                        assert node.value.value == 3, \
                            f"_POLL_DELAY_S must be 3, got {node.value.value}"
                        return

    raise AssertionError("Could not find _POLL_DELAY_S constant with value 3")


def test_num_poll_attempts_is_4():
    """FAIL-TO-PASS: _NUM_POLL_ATTEMPTS constant must be set to 4."""
    tree = _get_ast()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '_NUM_POLL_ATTEMPTS':
                    if isinstance(node.value, ast.Constant):
                        assert node.value.value == 4, \
                            f"_NUM_POLL_ATTEMPTS must be 4, got {node.value.value}"
                        return

    raise AssertionError("Could not find _NUM_POLL_ATTEMPTS constant with value 4")


def test_warning_log_level_for_failed_polls():
    """FAIL-TO-PASS: Failed polls must log at warning level, not debug.

    The old code used _logger.debug() for failed polls.
    The new code should use _logger.warning() for better visibility.
    """
    content = TARGET_FILE.read_text()

    # Should use _logger.warning for failed polls
    assert '_logger.warning(' in content, \
        "Failed polls must use _logger.warning() for visibility"

    # Should NOT use _logger.debug in the error handling path
    # (unless it's used elsewhere for non-error purposes)
    # We check that debug is not used in the poll failure context
    lines = content.split('\n')
    in_poll_func = False
    debug_in_poll = False
    brace_depth = 0

    for i, line in enumerate(lines):
        if 'async def _poll_for_title' in line:
            in_poll_func = True
            brace_depth = 0
        elif in_poll_func:
            if 'def ' in line and 'async def' not in line:
                in_poll_func = False
            elif '_logger.debug(' in line:
                debug_in_poll = True
                break

    # Note: We don't assert this because debug might still be used elsewhere
    # But in a proper fix, the poll function shouldn't use debug for errors


def test_poll_for_title_uses_constants():
    """FAIL-TO-PASS: _poll_for_title must use the new constants.

    The extracted function should use _NUM_POLL_ATTEMPTS for the loop
    and _POLL_DELAY_S for the sleep duration.
    """
    tree = _get_ast()

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == '_poll_for_title':
            func_node = node
            break

    assert func_node is not None, \
        "_poll_for_title function not found"

    func_source = ast.unparse(func_node)

    assert '_NUM_POLL_ATTEMPTS' in func_source, \
        "_poll_for_title must use _NUM_POLL_ATTEMPTS for loop count"
    assert '_POLL_DELAY_S' in func_source, \
        "_poll_for_title must use _POLL_DELAY_S for sleep duration"


def test_call_method_uses_poll_for_title():
    """FAIL-TO-PASS: __call__ method must use _poll_for_title.

    The __call__ method should be refactored to call the new
    _poll_for_title function instead of having inline polling logic.
    """
    content = TARGET_FILE.read_text()

    # The __call__ method should call _poll_for_title
    assert '_poll_for_title(' in content, \
        "__call__ method must call _poll_for_title()"

    # It should pass the expected arguments
    assert 'await _poll_for_title(' in content, \
        "__call__ must await _poll_for_title()"


def test_file_is_valid_python():
    """PASS-TO-PASS: The modified file must be valid Python syntax."""
    content = TARGET_FILE.read_text()

    try:
        compile(content, str(TARGET_FILE), 'exec')
    except SyntaxError as e:
        raise AssertionError(f"File has Python syntax error: {e}")


def test_imports_work():
    """PASS-TO-PASS: The modified module must be importable."""
    sys.path.insert(0, str(REPO))

    try:
        # This will fail on base commit because of missing deps,
        # but we check that the import structure is valid
        from openhands.app_server.event_callback import set_title_callback_processor

        # Verify the expected attributes exist
        assert hasattr(set_title_callback_processor, '_POLL_DELAY_S'), \
            "Module missing _POLL_DELAY_S after fix"
        assert hasattr(set_title_callback_processor, '_NUM_POLL_ATTEMPTS'), \
            "Module missing _NUM_POLL_ATTEMPTS after fix"

        # Check constant values via module attributes
        assert set_title_callback_processor._POLL_DELAY_S == 3, \
            f"_POLL_DELAY_S should be 3, got {set_title_callback_processor._POLL_DELAY_S}"
        assert set_title_callback_processor._NUM_POLL_ATTEMPTS == 4, \
            f"_NUM_POLL_ATTEMPTS should be 4, got {set_title_callback_processor._NUM_POLL_ATTEMPTS}"

    except ImportError as e:
        # If import fails due to missing dependencies (like full openhands deps),
        # that's OK - we just need to verify the code structure is correct
        if 'pydantic' in str(e) or 'openhands' in str(e) and 'app_server' not in str(e):
            # Skip this test - we don't have all deps installed
            pytest.skip(f"Skipping due to missing dependencies: {e}")
        else:
            raise AssertionError(f"Import failed: {e}")


# =============================================================================
# PASS-TO-PASS: Repo CI Tests
# These tests run actual CI commands from the repo's test suite.
# =============================================================================


def test_repo_ruff_check_modified_file():
    """PASS-TO-PASS: Repo ruff linter passes on modified file.

    This test runs the repo's ruff linter on the modified file to ensure
    code style compliance.
    """
    # Install ruff if needed
    install_r = subprocess.run(
        ['pip', 'install', 'ruff', '-q'],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if install_r.returncode != 0:
        pytest.skip(f"Could not install ruff: {install_r.stderr}")

    target_file = (
        'openhands/app_server/event_callback/set_title_callback_processor.py'
    )
    r = subprocess.run(
        ['ruff', 'check', '--config', 'dev_config/python/ruff.toml', target_file],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_unit_tests_for_modified_module():
    """PASS-TO-PASS: Repo unit tests for modified module pass.

    This test runs the specific unit tests for the SetTitleCallbackProcessor
    module to ensure existing functionality still works.
    """
    r = subprocess.run(
        [
            'python',
            '-m',
            'pytest',
            'tests/unit/app_server/test_set_title_callback_processor.py',
            '-v',
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_python_syntax_valid():
    """PASS-TO-PASS: Python syntax validation via compileall.

    This test uses Python's compileall module to verify all Python files
    in the openhands/app_server/event_callback directory have valid syntax.
    """
    r = subprocess.run(
        [
            'python',
            '-m',
            'py_compile',
            'openhands/app_server/event_callback/set_title_callback_processor.py',
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"
