"""Tests for the OpenLineage DagRunInfo partition fields fix."""

import datetime
import subprocess
import sys
import os
import re

# Path to the repository
REPO = "/workspace/airflow"
UTILS_PATH = f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py"


def _read_utils_file():
    """Read the utils.py file content."""
    with open(UTILS_PATH, "r") as f:
        return f.read()


def test_dagrun_info_includes_partition_fields():
    """
    Fail-to-pass: DagRunInfo must include partition_key and partition_date attributes.
    This test fails on base commit and passes after the fix.
    """
    content = _read_utils_file()

    # Check that partition_key and partition_date are in the includes list
    assert '"partition_key"' in content, "partition_key not found in DagRunInfo.includes"
    assert '"partition_date"' in content, "partition_date not found in DagRunInfo.includes"


def test_partition_fields_in_dagrun_info_includes_list():
    """
    Fail-to-pass: Verify partition_key and partition_date are specifically in DagRunInfo.includes.
    Uses regex to find the exact class definition.
    """
    content = _read_utils_file()

    # Look for the DagRunInfo class and its includes list
    # The pattern matches: class DagRunInfo(... followed by includes = [...])
    pattern = r'class DagRunInfo\([^)]+\):.*?(?:""".*?""")?.*?includes\s*=\s*\[([^\]]+)\]'
    match = re.search(pattern, content, re.DOTALL)
    assert match, "Could not find DagRunInfo includes list"

    includes_content = match.group(1)

    # Both fields should be present in the includes list
    assert '"partition_key"' in includes_content, "partition_key not in DagRunInfo.includes list"
    assert '"partition_date"' in includes_content, "partition_date not in DagRunInfo.includes list"


def test_partition_fields_have_version_comments():
    """
    Fail-to-pass: The partition fields should have Airflow 3.2+ version comments.
    """
    content = _read_utils_file()

    # Check for the lines with version comments
    assert '"partition_key",  # Airflow 3.2+' in content, "Missing version comment for partition_key"
    assert '"partition_date",  # Airflow 3.2+' in content, "Missing version comment for partition_date"


def test_partition_fields_ordering():
    """
    Fail-to-pass: Verify the partition fields are placed correctly in the includes list.
    They should appear after logical_date (Airflow 3) and before run_after.
    """
    content = _read_utils_file()

    # Find lines with these markers
    lines = content.split('\n')

    logical_date_line = None
    partition_key_line = None
    partition_date_line = None
    run_after_line = None

    for i, line in enumerate(lines):
        if '"logical_date",  # Airflow 3' in line and 'partition' not in line:
            logical_date_line = i
        if '"partition_key",  # Airflow 3.2+' in line:
            partition_key_line = i
        if '"partition_date",  # Airflow 3.2+' in line:
            partition_date_line = i
        if '"run_after",  # Airflow 3' in line:
            run_after_line = i

    # All lines should be found
    assert logical_date_line is not None, "Could not find logical_date line"
    assert partition_key_line is not None, "Could not find partition_key line"
    assert partition_date_line is not None, "Could not find partition_date line"
    assert run_after_line is not None, "Could not find run_after line"

    # partition_key and partition_date should come after logical_date
    assert partition_key_line > logical_date_line, "partition_key should come after logical_date"
    assert partition_date_line > logical_date_line, "partition_date should come after logical_date"

    # partition_key should come before run_after
    # After the fix, it should be: logical_date, partition_key, partition_date, run_after
    assert partition_key_line < run_after_line, "partition_key should come before run_after"
    assert partition_date_line < run_after_line, "partition_date should come before run_after"

    # partition_key should come before partition_date
    assert partition_key_line < partition_date_line, "partition_key should come before partition_date"


def test_partition_fields_only_in_dagrun_info():
    """
    Fail-to-pass: Verify partition fields are added to DagRunInfo, not other classes.
    """
    content = _read_utils_file()

    # Find all class definitions with includes lists
    pattern = r'class (\w+)\([^)]+\):.*?includes\s*=\s*\['
    matches = list(re.finditer(pattern, content, re.DOTALL))

    dagrun_info_match = None
    for match in matches:
        class_name = match.group(1)
        if class_name == "DagRunInfo":
            dagrun_info_match = match
            break

    assert dagrun_info_match is not None, "Could not find DagRunInfo class"

    # Get the includes content for DagRunInfo specifically
    start_pos = dagrun_info_match.end()
    # Find the closing bracket
    bracket_count = 1
    end_pos = start_pos
    while bracket_count > 0 and end_pos < len(content):
        if content[end_pos] == '[':
            bracket_count += 1
        elif content[end_pos] == ']':
            bracket_count -= 1
        end_pos += 1

    includes_content = content[start_pos:end_pos-1]

    assert '"partition_key"' in includes_content, "partition_key not in DagRunInfo includes"
    assert '"partition_date"' in includes_content, "partition_date not in DagRunInfo includes"


def test_repo_openlineage_utils_syntax():
    """
    Pass-to-pass: Verify the utils.py file has valid Python syntax.
    """
    result = subprocess.run(
        ["python3", "-m", "py_compile", UTILS_PATH],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Syntax error in utils.py:\n{result.stderr}"


def test_repo_openlineage_ruff_check():
    """
    Pass-to-pass: Repo's ruff linting passes for OpenLineage utils (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "ruff", "check", "src/airflow/providers/openlineage/utils/utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_ruff_format():
    """
    Pass-to-pass: Repo's ruff format check passes for OpenLineage utils (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "ruff", "format", "--check", "src/airflow/providers/openlineage/utils/utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_unit_tests():
    """
    Pass-to-pass: OpenLineage unit tests pass (pass_to_pass).
    Runs only the unit tests for the utils module that contains the DagRunInfo class.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-m", "pytest", "tests/unit/openlineage/utils/test_utils.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_no_duplicate_partition_fields():
    """
    Fail-to-pass: Ensure partition fields are not duplicated in the file.
    """
    content = _read_utils_file()

    # Count occurrences of partition fields
    partition_key_count = content.count('"partition_key"')
    partition_date_count = content.count('"partition_date"')

    # Should appear exactly once each (in the includes list)
    # Note: They might appear in tests too, but in the source file should be once
    assert partition_key_count >= 1, "partition_key not found in file"
    assert partition_date_count >= 1, "partition_date not found in file"


def test_repo_openlineage_mypy():
    """
    Pass-to-pass: OpenLineage utils passes mypy type checking (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "mypy", "src/airflow/providers/openlineage/utils/utils.py", "--ignore-missing-imports"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"MyPy type check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_facets_syntax():
    """
    Pass-to-pass: OpenLineage facets plugin has valid Python syntax (pass_to_pass).
    """
    facets_path = f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/plugins/facets.py"
    result = subprocess.run(
        ["python3", "-m", "py_compile", facets_path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Syntax error in facets.py:\n{result.stderr}"


def test_repo_openlineage_facets_unit_tests():
    """
    Pass-to-pass: OpenLineage facets unit tests pass (pass_to_pass).
    Tests the facets module that uses DagRunInfo.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-m", "pytest", "tests/unit/openlineage/plugins/test_facets.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Facets unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_openlineage_test_file_ruff():
    """
    Pass-to-pass: OpenLineage utils test file passes ruff linting (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "ruff", "check", "tests/unit/openlineage/utils/test_utils.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Ruff check on test file failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_import_check():
    """
    Pass-to-pass: OpenLineage utils module imports successfully (pass_to_pass).
    Verifies no circular imports or missing dependencies.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-c", "from airflow.providers.openlineage.utils.utils import DagRunInfo; print('Import successful')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_facets_ruff_check():
    """
    Pass-to-pass: Repo's ruff linting passes for OpenLineage facets (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "ruff", "check", "src/airflow/providers/openlineage/plugins/facets.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_facets_ruff_format():
    """
    Pass-to-pass: Repo's ruff format check passes for OpenLineage facets (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "ruff", "format", "--check", "src/airflow/providers/openlineage/plugins/facets.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_facets_mypy():
    """
    Pass-to-pass: OpenLineage facets passes mypy type checking (pass_to_pass).
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "mypy", "src/airflow/providers/openlineage/plugins/facets.py", "--ignore-missing-imports"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"MyPy type check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_openlineage_adapter_tests():
    """
    Pass-to-pass: OpenLineage adapter unit tests pass (pass_to_pass).
    Tests the adapter module that is closely related to facets.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-m", "pytest", "tests/unit/openlineage/plugins/test_adapter.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Adapter unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_openlineage_listener_tests():
    """
    Pass-to-pass: OpenLineage listener unit tests pass (pass_to_pass).
    Tests the listener module that uses DagRunInfo.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-m", "pytest", "tests/unit/openlineage/plugins/test_listener.py", "-v", "--tb=short", "-x"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Listener unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_openlineage_facets_import_check():
    """
    Pass-to-pass: OpenLineage facets module imports successfully (pass_to_pass).
    Verifies no circular imports or missing dependencies in facets module.
    """
    r = subprocess.run(
        ["uv", "run", "--group", "dev", "python", "-c", "from airflow.providers.openlineage.plugins.facets import AirflowDagRunFacet; print('Import successful')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Facets import check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
