"""
Tests for airflow-openlineage-partition-info task.
Verifies that DagRunInfo properly serializes partition_key and partition_date fields.
"""
import ast
import datetime
import json
import os
import subprocess
import sys
import tempfile

import pytest

REPO = "/workspace/airflow"
TARGET_FILE = f"{REPO}/providers/openlineage/src/airflow/providers/openlineage/utils/utils.py"


def serialize_dagrun_with_ast(dagrun_attrs):
    """
    Serialize a DagRun-like object using the DagRunInfo class loaded via AST.

    This runs a subprocess that:
    1. Loads the class definitions from source
    2. Creates a mock DagRun with the given attributes
    3. Serializes it using DagRunInfo
    4. Returns the result as JSON
    """
    # Convert datetime objects to ISO format strings for JSON serialization
    serializable_attrs = {}
    for k, v in dagrun_attrs.items():
        if isinstance(v, datetime.datetime):
            serializable_attrs[k] = {"__type": "datetime", "value": v.isoformat()}
        else:
            serializable_attrs[k] = v

    script = f'''
import ast
import datetime
import json
import sys
from typing import Any

# Mock attrs module
class MockAttrs:
    @staticmethod
    def has(cls):
        return False
    class fields:
        pass

sys.modules['attrs'] = MockAttrs()

# Mock logging
class MockLog:
    @staticmethod
    def warning(*args, **kwargs):
        pass

# Read source
with open("{TARGET_FILE}", "r") as f:
    source = f.read()

tree = ast.parse(source)

# Find classes
info_json_class = None
dagruninfo_class = None

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        if node.name == "InfoJsonEncodable":
            info_json_class = node
        elif node.name == "DagRunInfo":
            dagruninfo_class = node

env = {{
    'datetime': datetime,
    'AIRFLOW_V_3_0_PLUS': True,
    'AIRFLOW_V_3_2_PLUS': True,
    'DagRun': object,
    'log': MockLog(),
    'Any': Any,
    'attrs': MockAttrs(),
}}

# Execute classes
if info_json_class:
    code = compile(ast.Module(body=[info_json_class], type_ignores=[]), "<ast>", 'exec')
    exec(code, env)

code = compile(ast.Module(body=[dagruninfo_class], type_ignores=[]), "<ast>", 'exec')
exec(code, env)

DagRunInfo = env['DagRunInfo']

# Create mock from attrs
attrs = json.loads('{json.dumps(serializable_attrs)}')

class MockDagRun:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict) and v.get("__type") == "datetime":
                v = datetime.datetime.fromisoformat(v["value"])
            setattr(self, k, v)

mock = MockDagRun(**attrs)
result = dict(DagRunInfo(mock))

# Convert result to JSON-serializable
for k, v in list(result.items()):
    if isinstance(v, datetime.datetime):
        result[k] = v.isoformat()

print(json.dumps(result))
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Subprocess failed: stderr={proc.stderr}, stdout={proc.stdout}")

        return json.loads(proc.stdout.strip())
    finally:
        os.unlink(script_path)


class TestDagRunInfoSerialization:
    """Test that DagRunInfo properly serializes partition fields (behavioral tests)."""

    def test_partition_key_is_serialized(self):
        """Verify that partition_key is included in DagRunInfo output (fail_to_pass)."""
        result = serialize_dagrun_with_ast({
            "clear_number": 0,
            "conf": {},
            "dag_id": "test_dag",
            "data_interval_end": None,
            "data_interval_start": None,
            "end_date": None,
            "execution_date": None,
            "external_trigger": False,
            "logical_date": None,
            "run_after": None,
            "run_id": "run_001",
            "run_type": "manual",
            "start_date": None,
            "triggered_by": None,
            "triggering_user_name": None,
            "partition_key": "daily_partition",
            "partition_date": None,
        })

        # Assert that partition_key is in the output with the correct value
        assert "partition_key" in result, (
            f"'partition_key' not found in serialized DagRunInfo output. "
            f"Keys present: {list(result.keys())}"
        )
        assert result["partition_key"] == "daily_partition", (
            f"partition_key value mismatch. Expected 'daily_partition', got {result['partition_key']!r}"
        )

    def test_partition_date_is_serialized(self):
        """Verify that partition_date is included in DagRunInfo output (fail_to_pass)."""
        test_date = datetime.datetime(2024, 1, 15, 10, 30, 0)

        result = serialize_dagrun_with_ast({
            "clear_number": 0,
            "conf": {},
            "dag_id": "test_dag",
            "data_interval_end": None,
            "data_interval_start": None,
            "end_date": None,
            "execution_date": None,
            "external_trigger": False,
            "logical_date": None,
            "run_after": None,
            "run_id": "run_001",
            "run_type": "manual",
            "start_date": None,
            "triggered_by": None,
            "triggering_user_name": None,
            "partition_key": None,
            "partition_date": test_date,
        })

        # Assert that partition_date is in the output with the correct value
        assert "partition_date" in result, (
            f"'partition_date' not found in serialized DagRunInfo output. "
            f"Keys present: {list(result.keys())}"
        )
        # The value should be the ISO format string
        expected_value = test_date.isoformat()
        assert result["partition_date"] == expected_value, (
            f"partition_date value mismatch. Expected {expected_value!r}, got {result['partition_date']!r}"
        )

    def test_partition_fields_with_different_values(self):
        """Verify partition fields work with various input values (fail_to_pass)."""
        test_cases = [
            {"partition_key": "weekly_partition", "partition_date": datetime.datetime(2024, 6, 1)},
            {"partition_key": "monthly_report", "partition_date": datetime.datetime(2024, 12, 25)},
            {"partition_key": "", "partition_date": None},  # Edge cases
        ]

        base_attrs = {
            "clear_number": 0,
            "conf": {},
            "dag_id": "test_dag",
            "data_interval_end": None,
            "data_interval_start": None,
            "end_date": None,
            "execution_date": None,
            "external_trigger": False,
            "logical_date": None,
            "run_after": None,
            "run_type": "manual",
            "start_date": None,
            "triggered_by": None,
            "triggering_user_name": None,
        }

        for i, kwargs in enumerate(test_cases):
            attrs = {**base_attrs, "run_id": f"run_{i}", **kwargs}
            result = serialize_dagrun_with_ast(attrs)

            # Both fields should be present
            assert "partition_key" in result, f"Test case {i}: partition_key not in output"
            assert "partition_date" in result, f"Test case {i}: partition_date not in output"

            # Values should match inputs (partition_date gets isoformatted if it's a datetime)
            assert result["partition_key"] == kwargs["partition_key"]
            expected_date = kwargs["partition_date"].isoformat() if kwargs["partition_date"] else None
            assert result["partition_date"] == expected_date

    def test_partition_fields_are_none_when_not_set(self):
        """Verify partition fields appear as None when not set on DagRun (fail_to_pass)."""
        result = serialize_dagrun_with_ast({
            "clear_number": 0,
            "conf": {},
            "dag_id": "test_dag",
            "data_interval_end": None,
            "data_interval_start": None,
            "end_date": None,
            "execution_date": None,
            "external_trigger": False,
            "logical_date": None,
            "run_after": None,
            "run_id": "run_001",
            "run_type": "manual",
            "start_date": None,
            "triggered_by": None,
            "triggering_user_name": None,
            "partition_key": None,
            "partition_date": None,
        })

        # Both fields should be present even when None
        assert "partition_key" in result, "partition_key should be in output even when None"
        assert "partition_date" in result, "partition_date should be in output even when None"

        # Values should be None
        assert result["partition_key"] is None, f"partition_key should be None, got {result['partition_key']!r}"
        assert result["partition_date"] is None, f"partition_date should be None, got {result['partition_date']!r}"

    def test_existing_fields_still_work(self):
        """Verify existing fields like run_id, dag_id still serialize correctly (pass_to_pass)."""
        result = serialize_dagrun_with_ast({
            "clear_number": 0,
            "conf": {},
            "dag_id": "my_test_dag",
            "data_interval_end": None,
            "data_interval_start": None,
            "end_date": None,
            "execution_date": None,
            "external_trigger": False,
            "logical_date": None,
            "run_after": None,
            "run_id": "manual__2024-01-01",
            "run_type": "manual",
            "start_date": None,
            "triggered_by": None,
            "triggering_user_name": None,
            "partition_key": None,
            "partition_date": None,
        })

        # Check existing fields still work
        assert result["dag_id"] == "my_test_dag"
        assert result["run_id"] == "manual__2024-01-01"
        assert result["run_type"] == "manual"


class TestCodeQuality:
    """Pass-to-pass tests for code quality (static checks)."""

    def test_python_syntax_valid(self):
        """Target file has valid Python syntax (pass_to_pass)."""
        import py_compile
        try:
            py_compile.compile(TARGET_FILE, doraise=True)
        except py_compile.PyCompileError as e:
            pytest.fail(f"Syntax error in target file: {e}")

    def test_file_can_be_parsed(self):
        """Target file can be parsed as valid Python AST (pass_to_pass)."""
        with open(TARGET_FILE, "r") as f:
            source = f.read()
        try:
            ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"AST parsing failed: {e}")


class TestRepoCICommands:
    """Pass-to-pass tests that run actual repo CI commands via subprocess."""

    def test_ruff_check_openlineage_utils(self):
        """Ruff linting passes on openlineage utils module (pass_to_pass)."""
        # Install ruff first, then run ruff check
        install_result = subprocess.run(
            ["pip", "install", "--quiet", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )

        result = subprocess.run(
            ["ruff", "check", "providers/openlineage/src/airflow/providers/openlineage/utils/"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Ruff check failed on openlineage utils:\n{result.stdout}\n{result.stderr[-500:]}"
        )

    def test_ruff_format_check_openlineage_utils(self):
        """Ruff format check passes on openlineage utils module (pass_to_pass)."""
        # Install ruff first, then run ruff format --check
        subprocess.run(
            ["pip", "install", "--quiet", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )

        result = subprocess.run(
            ["ruff", "format", "--check", "providers/openlineage/src/airflow/providers/openlineage/utils/"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Ruff format check failed:\n{result.stdout}\n{result.stderr[-500:]}"
        )

    def test_python_compile_openlineage_src(self):
        """Python compilation succeeds on openlineage source files (pass_to_pass)."""
        result = subprocess.run(
            ["python", "-m", "py_compile",
             "providers/openlineage/src/airflow/providers/openlineage/utils/utils.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, (
            f"Python compilation failed:\n{result.stderr[-500:]}"
        )
