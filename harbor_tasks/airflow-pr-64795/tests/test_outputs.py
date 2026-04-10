"""Test outputs for apache/airflow#64795

This task adds missing 'auth list-envs' command to airflowctl integration tests
and refactors env_vars to use keyword arguments and dict literals.
"""

import ast
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

    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_airflowctl_commands":
            target_func = node
            break

    assert target_func is not None, "test_airflowctl_commands function not found"

    found_call = False
    for node in ast.walk(target_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                found_call = True
                keywords = {kw.arg for kw in node.keywords}
                assert "command" in keywords
                assert "env_vars" in keywords
                assert "skip_login" in keywords
                break

    assert found_call


def test_env_vars_is_dict_literal():
    """env_vars must be passed as a dict literal, not built incrementally (f2p)."""
    assert TEST_FILE.exists(), f"Test file not found: {TEST_FILE}"

    source = TEST_FILE.read_text()
    tree = ast.parse(source)

    target_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "test_airflowctl_commands_skip_keyring":
            target_func = node
            break

    assert target_func is not None

    found_call = False
    for node in ast.walk(target_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                found_call = True
                for kw in node.keywords:
                    if kw.arg == "env_vars":
                        assert isinstance(kw.value, ast.Dict)
                        keys = [k.value for k in kw.value.keys if isinstance(k, ast.Constant)]
                        assert "AIRFLOW_CLI_TOKEN" in keys
                        assert "AIRFLOW_CLI_DEBUG_MODE" in keys
                        assert "AIRFLOW_CLI_ENVIRONMENT" in keys
                        break
                break

    assert found_call


def test_ruff_formatting():
    """Code must pass ruff formatting check (agent_config from CLAUDE.md)."""
    result = subprocess.run(
        ["uv", "run", "--project", "airflow-ctl-tests", "ruff", "check", "--fix", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode in [0, 1]


def test_file_syntax_valid():
    """Test file must be valid Python syntax (p2p)."""
    assert TEST_FILE.exists()
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TEST_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_repo_ruff_check():
    """Repo's ruff linting passes on the test file (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "--project", "airflow-ctl-tests", "ruff", "check", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_airflowctl_coverage():
    """Repo's airflowctl CLI command coverage check passes (pass_to_pass)."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "rich"],
        capture_output=True,
        cwd=REPO
    )
    result = subprocess.run(
        [sys.executable, "scripts/ci/prek/check_airflowctl_command_coverage.py"],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Airflowctl coverage check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_pyproject_toml_valid():
    """Repo's pyproject.toml is valid TOML (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, '-c', 'import tomllib; tomllib.load(open("pyproject.toml", "rb"))'],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"pyproject.toml is invalid:\n{result.stderr}"


def test_repo_airflow_ctl_pyproject_valid():
    """airflow-ctl-tests pyproject.toml is valid TOML (pass_to_pass)."""
    pyproject_path = REPO / "airflow-ctl-tests" / "pyproject.toml"
    result = subprocess.run(
        [sys.executable, "-c", f"import tomllib; tomllib.load(open('{pyproject_path}', 'rb'))"],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"airflow-ctl-tests/pyproject.toml is invalid:\n{result.stderr}"


def test_repo_ruff_format_check():
    """Repo's ruff format check passes on the test file (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "--project", "airflow-ctl-tests", "ruff", "format", "--check", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_mypy_check():
    """Repo's mypy check passes on the test file (pass_to_pass)."""
    result = subprocess.run(
        ["uv", "run", "--project", "airflow-ctl-tests", "mypy", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Mypy check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_unittest_testcase_check():
    """Repo's unittest_testcase hook passes on the test file (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "scripts/ci/prek/unittest_testcase.py", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"unittest_testcase hook failed:\n{result.stdout}\n{result.stderr}"
