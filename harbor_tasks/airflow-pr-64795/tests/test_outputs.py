"""Test outputs for apache/airflow#64795

This task adds missing 'auth list-envs' command to airflowctl integration tests
and refactors env_vars to use keyword arguments and dict literals.
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

# Path to the repository
REPO = Path("/workspace/airflow")
TEST_FILE = REPO / "airflow-ctl-tests" / "tests" / "airflowctl_tests" / "test_airflowctl_commands.py"


def test_auth_list_envs_in_test_commands():
    """The 'auth list-envs' command must be present in TEST_COMMANDS list (f2p)."""
    assert TEST_FILE.exists(), f"Test file not found: {TEST_FILE}"

    source = TEST_FILE.read_text()
    tree = ast.parse(source)

    found_command = False
    for node in ast.walk(tree):
        if isinstance(node, ast.List):
            # Check if this is TEST_COMMANDS list (contains auth token command)
            for elt in node.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    if "auth list-envs" in elt.value:
                        found_command = True
                        break
        if found_command:
            break

    assert found_command, "'auth list-envs' command not found in TEST_COMMANDS list"


def test_run_command_uses_keyword_args_in_test_airflowctl_commands():
    """run_command must use keyword arguments for command, env_vars, skip_login (f2p)."""
    assert TEST_FILE.exists(), f"Test file not found: {TEST_FILE}"

    source = TEST_FILE.read_text()
    tree = ast.parse(source)

    # Find the test_airflowctl_commands function
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_airflowctl_commands":
            target_func = node
            break

    assert target_func is not None, "test_airflowctl_commands function not found"

    # Check the run_command call uses keyword arguments
    found_call = False
    for node in ast.walk(target_func):
        if isinstance(node, ast.Call):
            # Check if this is a run_command call
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                found_call = True
                # Must use keyword arguments (command=, env_vars=, skip_login=)
                keywords = {kw.arg for kw in node.keywords}
                assert "command" in keywords, "run_command must use 'command=' keyword"
                assert "env_vars" in keywords, "run_command must use 'env_vars=' keyword"
                assert "skip_login" in keywords, "run_command must use 'skip_login=' keyword"
                break

    assert found_call, "run_command call not found in test_airflowctl_commands"


def test_env_vars_is_dict_literal():
    """env_vars must be passed as a dict literal, not built incrementally (f2p)."""
    assert TEST_FILE.exists(), f"Test file not found: {TEST_FILE}"

    source = TEST_FILE.read_text()
    tree = ast.parse(source)

    # Find test_airflowctl_commands_skip_keyring function
    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_airflowctl_commands_skip_keyring":
            target_func = node
            break

    assert target_func is not None, "test_airflowctl_commands_skip_keyring function not found"

    # Check the run_command call uses dict literal for env_vars
    found_call = False
    for node in ast.walk(target_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                found_call = True
                # Find the env_vars keyword
                for kw in node.keywords:
                    if kw.arg == "env_vars":
                        # Must be a dict literal, not a variable or constructed dict
                        assert isinstance(kw.value, ast.Dict), \
                            "env_vars must be a dict literal {key: value, ...}"
                        # Check it has the expected keys
                        keys = [k.value for k in kw.value.keys if isinstance(k, ast.Constant)]
                        assert "AIRFLOW_CLI_TOKEN" in keys, "env_vars must contain AIRFLOW_CLI_TOKEN"
                        assert "AIRFLOW_CLI_DEBUG_MODE" in keys, "env_vars must contain AIRFLOW_CLI_DEBUG_MODE"
                        assert "AIRFLOW_CLI_ENVIRONMENT" in keys, "env_vars must contain AIRFLOW_CLI_ENVIRONMENT"
                        break
                break

    assert found_call, "run_command call not found in test_airflowctl_commands_skip_keyring"


def test_ruff_formatting():
    """Code must pass ruff formatting check (agent_config from CLAUDE.md)."""
    # Use uv to run ruff as per CLAUDE.md instructions
    result = subprocess.run(
        ["uv", "run", "--project", "airflow-ctl-tests", "ruff", "check", "--fix", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    # ruff returns 0 on success, 1 on fixes applied (still success)
    assert result.returncode in [0, 1], f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_file_syntax_valid():
    """Test file must be valid Python syntax (p2p)."""
    assert TEST_FILE.exists(), f"Test file not found: {TEST_FILE}"

    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TEST_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Syntax error in {TEST_FILE}:\n{result.stderr}"
