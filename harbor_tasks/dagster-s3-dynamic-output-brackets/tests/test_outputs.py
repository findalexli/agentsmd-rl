"""Test module for dagster-s3-dynamic-output-brackets task.

Tests that the s3_pickle_io_manager properly sanitizes square brackets from
dynamic output paths, fixing the issue where downstream ops failed when
loading stored objects.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/dagster")
IO_MANAGER_PATH = REPO / "python_modules/libraries/dagster-aws/dagster_aws/s3/io_manager.py"


def test_sanitize_path_method_exists():
    """FAIL_TO_PASS: _sanitize_path method must exist on PickledObjectS3IOManager.

    The fix adds a _sanitize_path static method to the class.
    This test verifies the method exists.
    """
    # Import the class - this will fail if the module doesn't exist
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "python_modules/libraries/dagster-aws"))

    from dagster_aws.s3.io_manager import PickledObjectS3IOManager

    # The method must exist
    assert hasattr(PickledObjectS3IOManager, "_sanitize_path"), \
        "PickledObjectS3IOManager must have _sanitize_path method"


def test_sanitize_path_transforms_brackets():
    """FAIL_TO_PASS: _sanitize_path must transform [ to -- and remove ].

    Test various input scenarios:
    - "return_value[foo]" -> "return_value--foo"
    - "step[key_1]" -> "step--key_1"
    - "op[0]" -> "op--0"
    - "no_brackets" -> "no_brackets"
    """
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "python_modules/libraries/dagster-aws"))

    from dagster_aws.s3.io_manager import PickledObjectS3IOManager
    from upath import UPath

    # Test cases: (input, expected)
    test_cases = [
        ("return_value[foo]", "return_value--foo"),
        ("step[key_1]", "step--key_1"),
        ("op[0]", "op--0"),
        ("dynamic[bar]", "dynamic--bar"),
        ("nested[inner][outer]", "nested--inner--outer"),  # Multiple brackets
        ("no_brackets", "no_brackets"),  # No brackets - unchanged
    ]

    for input_path, expected_name in test_cases:
        input_upath = UPath(input_path)
        result = PickledObjectS3IOManager._sanitize_path(input_upath)
        result_name = result.name if result.name else str(result)

        assert result_name == expected_name, \
            f"_sanitize_path({input_path!r}) returned {result_name!r}, expected {expected_name!r}"


def test_get_op_output_relative_path_uses_sanitization():
    """FAIL_TO_PASS: get_op_output_relative_path must call _sanitize_path.

    This verifies that the fix is actually applied in the method that
    generates S3 object keys. We check by examining the source code
    since we can't easily mock the full context.
    """
    import ast

    source = IO_MANAGER_PATH.read_text()
    tree = ast.parse(source)

    # Find the get_op_output_relative_path method
    found_sanitize_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_op_output_relative_path":
            # Check if it calls _sanitize_path
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute) and child.func.attr == "_sanitize_path":
                        found_sanitize_call = True
                    elif isinstance(child.func, ast.Name) and child.func.id == "_sanitize_path":
                        found_sanitize_call = True

    assert found_sanitize_call, \
        "get_op_output_relative_path must call _sanitize_path to fix the bracket issue"


def test_repo_ruff():
    """PASS_TO_PASS: Repo code quality checks pass.

    As per CLAUDE.md, make ruff must pass after any code changes.
    """
    r = subprocess.run(
        ["make", "ruff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # ruff may modify files, but return code 0 means no unfixable issues
    assert r.returncode == 0, \
        f"make ruff failed with return code {r.returncode}:\n{r.stdout}\n{r.stderr}"


def test_repo_check_ruff():
    """PASS_TO_PASS: Repo code quality checks pass without auto-fix.

    Verifies that the code already passes ruff linting and formatting checks.
    """
    r = subprocess.run(
        ["make", "check_ruff"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert r.returncode == 0, \
        f"make check_ruff failed with return code {r.returncode}:\n{r.stdout}\n{r.stderr}"


def test_repo_s3_io_manager_tests():
    """PASS_TO_PASS: S3 IO manager unit tests pass.

    Runs the existing S3 IO manager tests from the repo's test suite.
    These tests verify that the PickledObjectS3IOManager and S3PickleIOManager
    work correctly with mocked S3.
    """
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "python_modules/libraries/dagster-aws/dagster_aws_tests/s3_tests/test_io_manager.py",
            "-v",
            "--tb=short"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert r.returncode == 0, \
        f"S3 IO manager tests failed with return code {r.returncode}:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_module_imports():
    """PASS_TO_PASS: dagster_aws.s3.io_manager module must import cleanly."""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "python_modules/libraries/dagster-aws"))

    # Clear any cached imports
    modules_to_clear = [k for k in sys.modules.keys() if k.startswith("dagster_aws")]
    for m in modules_to_clear:
        del sys.modules[m]

    from dagster_aws.s3.io_manager import PickledObjectS3IOManager, S3PickleIOManager

    assert PickledObjectS3IOManager is not None
    assert S3PickleIOManager is not None
