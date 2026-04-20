"""Test outputs for SetTitleCallbackProcessor polling fix.

This validates that the PR changes have been applied behaviorally:
1. Old constant _TITLE_POLL_DELAYS_S is removed
2. A constant with value 3 (delay) exists and is used for polling sleep
3. A constant with value 4 (attempts) exists and is used for polling loop
4. New async helper function exists with correct signature
5. Log level changed from debug to warning for failed polls
6. Polling logic is extracted to the new function
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


def _find_constant_with_value(tree, value):
    """Find all constant names that have the given value."""
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if isinstance(node.value, ast.Constant) and node.value.value == value:
                        names.append(target.id)
    return names


def test_old_constant_removed():
    """FAIL-TO-PASS: Old _TITLE_POLL_DELAYS_S constant must be removed.

    The old code had: _TITLE_POLL_DELAYS_S = (0.25, 0.5, 1.0, 2.0)
    This tuple-based approach should be replaced with new constants.
    """
    tree = _get_ast()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == '_TITLE_POLL_DELAYS_S':
                        raise AssertionError(
                            "Old _TITLE_POLL_DELAYS_S constant should be removed"
                        )


def test_delay_constant_exists_and_is_three():
    """FAIL-TO-PASS: A constant with value 3 must exist (for delay seconds).

    The new code should have a constant set to 3 for the polling delay.
    We don't check the name - we check the value and its usage.
    """
    tree = _get_ast()
    delay_constants = _find_constant_with_value(tree, 3)

    assert len(delay_constants) > 0, \
        "No constant with value 3 found (needed for polling delay)"


def test_attempts_constant_exists_and_is_four():
    """FAIL-TO-PASS: A constant with value 4 must exist (for number of attempts).

    The new code should have a constant set to 4 for the number of polling attempts.
    We don't check the name - we check the value and its usage.
    """
    tree = _get_ast()
    attempts_constants = _find_constant_with_value(tree, 4)

    assert len(attempts_constants) > 0, \
        "No constant with value 4 found (needed for polling attempts)"


def test_async_polling_function_exists():
    """FAIL-TO-PASS: An async helper function for polling must exist.

    The polling logic should be extracted to a dedicated async function
    that takes appropriate parameters (httpx client, url, session API key)
    and returns str | None.
    """
    tree = _get_ast()

    # Find all async functions
    async_funcs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            async_funcs.append(node)

    # Find one that looks like a polling function:
    # - Takes httpx_client, url, session_api_key (or similar)
    # - Returns str | None
    polling_func = None
    for func in async_funcs:
        args = [arg.arg for arg in func.args.args]
        arg_names_lower = [a.lower() for a in args]

        # Check for required parameter types (flexible naming)
        has_client = any('client' in a or 'httpx' in a for a in arg_names_lower)
        has_url = 'url' in arg_names_lower
        has_api_key = any('api' in a or 'key' in a or 'session' in a for a in arg_names_lower)

        # Check return type is str | None or Optional[str]
        has_str_none_return = False
        if func.returns:
            return_str = ast.unparse(func.returns)
            if 'str' in return_str and 'None' in return_str:
                has_str_none_return = True

        if has_client and has_url and has_api_key and has_str_none_return:
            polling_func = func
            break

    assert polling_func is not None, \
        "No async polling function found with required parameters (client, url, api_key) " \
        "and return type str | None"


def test_polling_function_uses_delay_constant():
    """FAIL-TO-PASS: The polling function must sleep using the delay constant.

    The async helper should call asyncio.sleep with the delay constant (value 3).
    """
    tree = _get_ast()

    # Find the delay constant name
    delay_constants = _find_constant_with_value(tree, 3)
    assert len(delay_constants) > 0, "No constant with value 3 found"
    delay_const_name = delay_constants[0]

    # Find the polling function (async function with appropriate signature)
    polling_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            args = [arg.arg for arg in node.args.args]
            arg_names_lower = [a.lower() for a in args]
            has_client = any('client' in a or 'httpx' in a for a in arg_names_lower)
            has_url = 'url' in arg_names_lower
            has_api_key = any('api' in a or 'key' in a or 'session' in a for a in arg_names_lower)

            if has_client and has_url and has_api_key:
                if node.returns:
                    return_str = ast.unparse(node.returns)
                    if 'str' in return_str and 'None' in return_str:
                        polling_func = node
                        break

    assert polling_func is not None, "Could not find polling function"

    # Check that the function uses the delay constant in an asyncio.sleep call
    func_source = ast.unparse(polling_func)

    # Look for asyncio.sleep or sleep being called with the delay constant
    assert 'asyncio.sleep' in func_source or 'sleep(' in func_source, \
        "Polling function must call asyncio.sleep for delays"

    # The delay constant should be used in the function
    assert delay_const_name in func_source, \
        f"Polling function must use the delay constant ({delay_const_name})"


def test_polling_function_uses_attempts_constant():
    """FAIL-TO-PASS: The polling function must use the attempts constant.

    The async helper should use the attempts constant (value 4) for loop count.
    """
    tree = _get_ast()

    # Find the attempts constant name
    attempts_constants = _find_constant_with_value(tree, 4)
    assert len(attempts_constants) > 0, "No constant with value 4 found"
    attempts_const_name = attempts_constants[0]

    # Find the polling function
    polling_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            args = [arg.arg for arg in node.args.args]
            arg_names_lower = [a.lower() for a in args]
            has_client = any('client' in a or 'httpx' in a for a in arg_names_lower)
            has_url = 'url' in arg_names_lower
            has_api_key = any('api' in a or 'key' in a or 'session' in a for a in arg_names_lower)

            if has_client and has_url and has_api_key:
                if node.returns:
                    return_str = ast.unparse(node.returns)
                    if 'str' in return_str and 'None' in return_str:
                        polling_func = node
                        break

    assert polling_func is not None, "Could not find polling function"

    # Check that the function uses the attempts constant
    func_source = ast.unparse(polling_func)
    assert attempts_const_name in func_source, \
        f"Polling function must use the attempts constant ({attempts_const_name})"

    # Should be used in a range() or similar loop construct
    assert 'range' in func_source or 'for ' in func_source, \
        "Polling function should loop using the attempts constant"


def test_warning_log_level_for_failed_polls():
    """FAIL-TO-PASS: Failed polls must use warning log level, not debug.

    The polling function should use _logger.warning() for failed HTTP requests,
    not _logger.debug() which was used in the old code.
    """
    tree = _get_ast()

    # Find the polling function
    polling_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            args = [arg.arg for arg in node.args.args]
            arg_names_lower = [a.lower() for a in args]
            has_client = any('client' in a or 'httpx' in a for a in arg_names_lower)
            has_url = 'url' in arg_names_lower
            has_api_key = any('api' in a or 'key' in a or 'session' in a for a in arg_names_lower)

            if has_client and has_url and has_api_key:
                if node.returns:
                    return_str = ast.unparse(node.returns)
                    if 'str' in return_str and 'None' in return_str:
                        polling_func = node
                        break

    assert polling_func is not None, "Could not find polling function"

    func_source = ast.unparse(polling_func)

    # Should use warning, not debug, for failures
    assert '_logger.warning(' in func_source or 'logger.warning(' in func_source, \
        "Polling function must use _logger.warning() for failed polls"

    # Should NOT use debug for the error handling path
    assert '_logger.debug(' not in func_source, \
        "Polling function should not use _logger.debug() - use warning instead"


def test_call_method_uses_polling_helper():
    """FAIL-TO-PASS: __call__ method must await the polling helper.

    The __call__ method should delegate to the new async polling function
    instead of having inline retry logic.
    """
    tree = _get_ast()

    # Find the polling function name
    polling_func_name = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef):
            args = [arg.arg for arg in node.args.args]
            arg_names_lower = [a.lower() for a in args]
            has_client = any('client' in a or 'httpx' in a for a in arg_names_lower)
            has_url = 'url' in arg_names_lower
            has_api_key = any('api' in a or 'key' in a or 'session' in a for a in arg_names_lower)

            if has_client and has_url and has_api_key:
                if node.returns:
                    return_str = ast.unparse(node.returns)
                    if 'str' in return_str and 'None' in return_str:
                        polling_func_name = node.name
                        break

    assert polling_func_name is not None, "Could not find polling function"

    # Find the SetTitleCallbackProcessor class and its __call__ method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name == 'SetTitleCallbackProcessor':
                for item in node.body:
                    if isinstance(item, ast.AsyncFunctionDef) and item.name == '__call__':
                        call_source = ast.unparse(item)

                        # Should await the polling function
                        assert f'await {polling_func_name}(' in call_source or \
                               f'await {polling_func_name}' in call_source, \
                            f"__call__ method must await the polling helper ({polling_func_name})"
                        return

    raise AssertionError("Could not find __call__ method in SetTitleCallbackProcessor")


def test_constants_via_import():
    """FAIL-TO-PASS: Module constants must be importable with correct values.

    Import the module and verify the constants for delay (3) and attempts (4)
    are accessible with correct values.
    """
    sys.path.insert(0, str(REPO))

    try:
        from openhands.app_server.event_callback import set_title_callback_processor

        # Find constants with values 3 and 4 by checking module attributes
        delay_found = False
        attempts_found = False

        for attr_name in dir(set_title_callback_processor):
            attr_value = getattr(set_title_callback_processor, attr_name)
            if isinstance(attr_value, int):
                if attr_value == 3:
                    delay_found = True
                elif attr_value == 4:
                    attempts_found = True

        assert delay_found, \
            "Module should have an integer constant with value 3 (delay)"
        assert attempts_found, \
            "Module should have an integer constant with value 4 (attempts)"

    except ImportError as e:
        # If import fails due to missing dependencies, skip
        if 'pydantic' in str(e) or 'openhands' in str(e):
            pytest.skip(f"Skipping due to missing dependencies: {e}")
        else:
            raise AssertionError(f"Import failed: {e}")


# =============================================================================
# PASS-TO-PASS: Repo CI Tests
# These tests run actual CI commands from the repo's test suite.
# =============================================================================


def test_file_is_valid_python():
    """PASS-TO-PASS: The modified file must be valid Python syntax."""
    content = TARGET_FILE.read_text()

    try:
        compile(content, str(TARGET_FILE), 'exec')
    except SyntaxError as e:
        raise AssertionError(f"File has Python syntax error: {e}")


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
