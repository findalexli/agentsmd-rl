"""Tests for verifying removal of test_list_global_search and version bump."""

import ast
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/langgraph")
CHECKPOINT_CONFORMANCE_DIR = REPO / "libs/checkpoint-conformance"
TEST_FILE = CHECKPOINT_CONFORMANCE_DIR / "langgraph/checkpoint/conformance/spec/test_list.py"
PYPROJECT_FILE = CHECKPOINT_CONFORMANCE_DIR / "pyproject.toml"


def test_global_search_function_removed():
    """FAIL-TO-PASS: test_list_global_search function must be removed from test_list.py."""
    content = TEST_FILE.read_text()

    # Parse the AST to find all function definitions
    tree = ast.parse(content)

    function_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            function_names.append(node.name)

    # The test_list_global_search function should NOT exist
    assert "test_list_global_search" not in function_names, (
        f"test_list_global_search function still exists in {TEST_FILE}. "
        f"Found functions: {function_names}"
    )


def test_global_search_removed_from_all_list_tests():
    """FAIL-TO-PASS: test_list_global_search must be removed from ALL_LIST_TESTS list."""
    content = TEST_FILE.read_text()

    # Parse the AST to find the ALL_LIST_TESTS list
    tree = ast.parse(content)

    all_list_tests = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ALL_LIST_TESTS":
                    # Extract the list elements
                    if isinstance(node.value, ast.List):
                        all_list_tests = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Name):
                                all_list_tests.append(elt.id)

    assert all_list_tests is not None, "Could not find ALL_LIST_TESTS in the file"
    assert "test_list_global_search" not in all_list_tests, (
        f"test_list_global_search still present in ALL_LIST_TESTS. "
        f"Current tests: {all_list_tests}"
    )


def test_version_bumped_to_002():
    """FAIL-TO-PASS: Version in pyproject.toml must be bumped to 0.0.2."""
    content = PYPROJECT_FILE.read_text()

    # Check that version is 0.0.2, not 0.0.1
    assert 'version = "0.0.2"' in content or "version = '0.0.2'" in content, (
        f"Version not bumped to 0.0.2 in {PYPROJECT_FILE}. "
        f"Expected version = \"0.0.2\""
    )

    # Make sure old version is not present
    assert 'version = "0.0.1"' not in content and "version = '0.0.1'" not in content, (
        f"Old version 0.0.1 still present in {PYPROJECT_FILE}"
    )


def test_other_list_tests_still_present():
    """PASS-TO-PASS: Other essential tests should still exist in ALL_LIST_TESTS."""
    content = TEST_FILE.read_text()

    tree = ast.parse(content)

    all_list_tests = None
    function_names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "ALL_LIST_TESTS":
                    if isinstance(node.value, ast.List):
                        all_list_tests = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Name):
                                all_list_tests.append(elt.id)
        if isinstance(node, ast.AsyncFunctionDef) or isinstance(node, ast.FunctionDef):
            function_names.append(node.name)

    # Essential tests should still be present
    essential_tests = [
        "test_list_all",
        "test_list_by_thread",
        "test_list_ordering",
        "test_list_limit",
    ]

    for test_name in essential_tests:
        assert test_name in function_names, f"Essential test {test_name} is missing from functions"
        assert test_name in all_list_tests, f"Essential test {test_name} is missing from ALL_LIST_TESTS"


def test_file_syntax_valid():
    """PASS-TO-PASS: The modified Python file should have valid syntax."""
    content = TEST_FILE.read_text()

    # Try to parse the file - will raise SyntaxError if invalid
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {TEST_FILE}: {e}")


def test_repo_lint_ruff():
    """PASS-TO-PASS: Ruff linting should pass on the modified file."""
    # First check if ruff is available
    result = subprocess.run(
        ["which", "ruff"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Skip if ruff not installed
        return

    result = subprocess.run(
        ["ruff", "check", str(TEST_FILE)],
        capture_output=True,
        text=True,
        cwd=str(REPO / "libs/checkpoint-conformance")
    )

    assert result.returncode == 0, f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"


def test_import_structure_valid():
    """PASS-TO-PASS: The test module should still be importable."""
    # Test that we can import the module without errors
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, 'libs/checkpoint-conformance'); " +
         "from langgraph.checkpoint.conformance.spec.test_list import ALL_LIST_TESTS; " +
         "print(f'ALL_LIST_TESTS has {len(ALL_LIST_TESTS)} tests')"],
        capture_output=True,
        text=True,
        cwd=str(REPO)
    )

    assert result.returncode == 0, (
        f"Failed to import test_list module:\n{result.stderr}"
    )

    # Verify the count - should be 16 tests (17 originally - 1 removed)
    assert "16" in result.stdout, f"Expected 16 tests in ALL_LIST_TESTS, got: {result.stdout}"


def test_repo_make_lint():
    """PASS-TO-PASS: Repo make lint passes (CI check)."""
    result = subprocess.run(
        ["make", "lint"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(CHECKPOINT_CONFORMANCE_DIR),
    )
    assert result.returncode == 0, f"make lint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_make_test():
    """PASS-TO-PASS: Repo make test passes (CI check)."""
    result = subprocess.run(
        ["make", "test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(CHECKPOINT_CONFORMANCE_DIR),
    )
    assert result.returncode == 0, f"make test failed:\n{result.stdout}\n{result.stderr}"


def test_repo_pyproject_valid():
    """PASS-TO-PASS: pyproject.toml is valid TOML and parseable."""
    import tomllib
    content = PYPROJECT_FILE.read_bytes()
    parsed = tomllib.loads(content.decode('utf-8'))
    assert "project" in parsed, "No [project] section in pyproject.toml"
    assert parsed["project"]["name"] == "langgraph-checkpoint-conformance", \
        f"Unexpected project name: {parsed['project']['name']}"
