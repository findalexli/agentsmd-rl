"""Tests for the OpenLineage DagRunInfo partition fields fix."""

import datetime
import subprocess
import sys
import os
import re
import json

# Path to the repository
REPO = "/workspace/airflow"
UTILS_PATH = f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py"


def test_dagrun_info_includes_partition_fields():
    """
    Fail-to-pass: DagRunInfo must include partition_key and partition_date in serialization.
    This test fails on base commit and passes after the fix.
    Tests behaviorally by verifying the fields appear in the serialized output.
    """
    r = subprocess.run(
        [
            "uv", "run", "--group", "dev", "python", "-c",
            """
from unittest.mock import MagicMock
import datetime
from airflow.providers.openlineage.utils.utils import DagRunInfo

# Create a mock DagRun with partition fields
dagrun = MagicMock()
dagrun.clear_number = None
dagrun.conf = {}
dagrun.dag_id = "test_dag"
dagrun.data_interval_end = None
dagrun.data_interval_start = None
dagrun.end_date = None
dagrun.execution_date = None
dagrun.external_trigger = False
dagrun.logical_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.partition_key = "some_partition_key"
dagrun.partition_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_after = datetime.datetime(2024, 6, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_id = "test_run_id"
dagrun.run_type = "manual"
dagrun.start_date = None
dagrun.triggered_by = "user"
dagrun.triggering_user_name = "user1"
dagrun.note = None
dagrun.deadlines = None

result = DagRunInfo(dagrun)
result_dict = dict(result)

# Check partition fields are in the serialized output
assert 'partition_key' in result_dict, f"partition_key missing from result: {list(result_dict.keys())}"
assert 'partition_date' in result_dict, f"partition_date missing from result: {list(result_dict.keys())}"
print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}\nStdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_partition_fields_serialized_with_correct_values():
    """
    Fail-to-pass: Verify the partition fields appear in serialization with correct values.
    Tests that the fields are serialized with appropriate values.
    """
    r = subprocess.run(
        [
            "uv", "run", "--group", "dev", "python", "-c",
            """
from unittest.mock import MagicMock
import datetime
from airflow.providers.openlineage.utils.utils import DagRunInfo

# Create a mock DagRun with partition fields
dagrun = MagicMock()
dagrun.clear_number = None
dagrun.conf = {}
dagrun.dag_id = "test_dag"
dagrun.data_interval_end = None
dagrun.data_interval_start = None
dagrun.end_date = None
dagrun.execution_date = None
dagrun.external_trigger = False
dagrun.logical_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.partition_key = "my_partition"
dagrun.partition_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_after = datetime.datetime(2024, 6, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_id = "test_run_id"
dagrun.run_type = "manual"
dagrun.start_date = None
dagrun.triggered_by = "user"
dagrun.triggering_user_name = "user1"
dagrun.note = None
dagrun.deadlines = None

result = DagRunInfo(dagrun)
result_dict = dict(result)

# Verify the values are correctly serialized
assert result_dict.get('partition_key') == "my_partition", f"partition_key value wrong: {result_dict.get('partition_key')}"
assert result_dict.get('partition_date') == "2024-06-01T00:00:00+00:00", f"partition_date value wrong: {result_dict.get('partition_date')}"
print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}\nStdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_partition_fields_ordering():
    """
    Fail-to-pass: Verify the partition fields are placed correctly in the includes list.
    They should appear after logical_date and before run_after based on the version ordering.
    """
    r = subprocess.run(
        [
            "uv", "run", "--group", "dev", "python", "-c",
            """
from unittest.mock import MagicMock
import datetime
from airflow.providers.openlineage.utils.utils import DagRunInfo

# Create a mock DagRun with partition fields
dagrun = MagicMock()
dagrun.clear_number = None
dagrun.conf = {}
dagrun.dag_id = "test_dag"
dagrun.data_interval_end = None
dagrun.data_interval_start = None
dagrun.end_date = None
dagrun.execution_date = None
dagrun.external_trigger = False
dagrun.logical_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.partition_key = "my_partition"
dagrun.partition_date = datetime.datetime(2024, 6, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_after = datetime.datetime(2024, 6, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
dagrun.run_id = "test_run_id"
dagrun.run_type = "manual"
dagrun.start_date = None
dagrun.triggered_by = "user"
dagrun.triggering_user_name = "user1"
dagrun.note = None
dagrun.deadlines = None

result = DagRunInfo(dagrun)
result_dict = dict(result)

# The includes list controls serialization order - verify key order is correct
# by checking the output dict maintains expected ordering relative to surrounding fields
keys = list(result_dict.keys())

# logical_date should come before partition_key
assert keys.index('logical_date') < keys.index('partition_key'), \
    f"logical_date should come before partition_key. Order: {keys}"
# partition_key should come before partition_date
assert keys.index('partition_key') < keys.index('partition_date'), \
    f"partition_key should come before partition_date. Order: {keys}"
# partition_date should come before run_after
assert keys.index('partition_date') < keys.index('run_after'), \
    f"partition_date should come before run_after. Order: {keys}"
print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}\nStdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_partition_fields_only_in_dagrun_info():
    """
    Fail-to-pass: Verify partition fields are added to DagRunInfo, not other classes.
    Tests that only DagRunInfo includes the partition fields.
    """
    r = subprocess.run(
        [
            "uv", "run", "--group", "dev", "python", "-c",
            """
from airflow.providers.openlineage.utils.utils import DagRunInfo

# Check that DagRunInfo has partition_key in its includes list
assert hasattr(DagRunInfo, 'includes'), "DagRunInfo missing includes attribute"
includes = DagRunInfo.includes
assert 'partition_key' in includes, f"partition_key not in DagRunInfo.includes: {includes}"
assert 'partition_date' in includes, f"partition_date not in DagRunInfo.includes: {includes}"
print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}\nStdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_no_duplicate_partition_fields():
    """
    Fail-to-pass: Ensure partition fields appear exactly once in the includes list.
    """
    r = subprocess.run(
        [
            "uv", "run", "--group", "dev", "python", "-c",
            """
from airflow.providers.openlineage.utils.utils import DagRunInfo

includes = DagRunInfo.includes
partition_key_count = includes.count('partition_key')
partition_date_count = includes.count('partition_date')

assert partition_key_count == 1, f"partition_key appears {partition_key_count} times in includes"
assert partition_date_count == 1, f"partition_date appears {partition_date_count} times in includes"
print('PASS')
""",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/providers/openlineage",
    )
    assert r.returncode == 0, f"Behavioral test failed: {r.stderr}\nStdout: {r.stdout}"
    assert "PASS" in r.stdout


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
