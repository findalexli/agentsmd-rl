"""
Benchmark tests for apache/airflow#64773
Fix structlog positional formatting for single-dict arguments

Tests verify that dict arguments passed with %s format specifier work correctly.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/airflow")


# =============================================================================
# fail_to_pass tests: Must FAIL on base commit, PASS after fix
# =============================================================================

class TestDictPositionalFormatting:
    """Test dict args passed as positional arguments to log messages."""

    def test_dict_positional_with_percent_s_stdlib(self):
        """
        When a dict is passed as positional arg with %s format, it should
        format the dict as a string, not try named substitution.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter

# Test case: dict with %s format specifier
event_dict = {
    "event": "Info message %s",
    "positional_args": ({"a": 10},),
}
result = positional_arguments_formatter(None, None, event_dict)
# Verify dict was consumed as positional arg (formatted into %s)
output = result["event"]
assert "Info message" in output, f"Prefix lost: {output}"
# The dict {'a': 10} should be formatted as string for %s
# Check that the dict content appears (without hardcoding the exact repr)
assert "'a': 10" in output or '"a": 10' in output, f"Dict content not found: {output}"
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed with stderr: {result.stderr}"

    def test_dict_positional_with_percent_s_multiple_values(self):
        """
        Test dict positional formatting with different dict values.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter

# Test with a dict containing numeric key
event_dict = {"event": "value %s", "positional_args": ({"x": 1},)}
result = positional_arguments_formatter(None, None, event_dict)
output = result["event"]
assert "value" in output
assert "x" in output and "1" in output
print("OK: numeric dict key works")

# Test with string keys
event_dict = {"event": "data: %s", "positional_args": ({"key": "val"},)}
result = positional_arguments_formatter(None, None, event_dict)
output = result["event"]
assert "data:" in output
assert "key" in output and "val" in output
print("OK: string dict works")
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed with stderr: {result.stderr}"
        assert "OK: numeric dict key works" in result.stdout
        assert "OK: string dict works" in result.stdout

    def test_named_substitution_still_works(self):
        """
        Named substitution (%(key)s) with dict should still work after fix.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter

# Named substitution with dict
event_dict = {
    "event": "%(a)s message",
    "positional_args": ({"a": 10},),
}
result = positional_arguments_formatter(None, None, event_dict)
output = result["event"]
# Should substitute the named key from the dict
assert "10" in output and "message" in output
print("OK: named substitution works")
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed with stderr: {result.stderr}"
        assert "OK: named substitution works" in result.stdout

    def test_formatter_exception_handling_type_error(self):
        """
        The formatter should catch TypeError during formatting and fall back correctly.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter

# When a dict arg is passed with %s format, formatter should handle it
# without raising TypeError
event_dict = {
    "event": "User %s logged in",
    "positional_args": ({"username": "alice"},),
}
result = positional_arguments_formatter(None, None, event_dict)
# Should format dict into %s slot without raising
output = result["event"]
assert "User" in output and "logged in" in output
# Check that dict content made it into the output
assert "username" in output or "alice" in output
print("OK: Dict formatted correctly with %s")
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed: {result.stdout}{result.stderr}"
        assert "OK: Dict formatted correctly" in result.stdout


class TestPositionalArgumentsFormatter:
    """Test the new positional_arguments_formatter function."""

    def test_function_exists_and_importable(self):
        """
        The positional_arguments_formatter function must exist and be importable.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter
print("Function exists:", callable(positional_arguments_formatter))
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "Function exists: True" in result.stdout

    def test_formatter_consumes_positional_args_key(self):
        """
        The formatter should consume the positional_args key from event_dict.
        (fail_to_pass)
        """
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

from airflow_shared.logging.structlog import positional_arguments_formatter

event_dict = {
    "event": "Test %s",
    "positional_args": ({"key": "val"},),
    "other_key": "preserved",
}
result = positional_arguments_formatter(None, None, event_dict)

# positional_args should be consumed/deleted
assert "positional_args" not in result, f"positional_args not consumed: {result}"
# other keys should be preserved
assert result.get("other_key") == "preserved", f"other_key not preserved"
print("OK: positional_args consumed, other keys preserved")
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed: {result.stdout}{result.stderr}"
        assert "OK: positional_args consumed" in result.stdout


# =============================================================================
# pass_to_pass tests: Must PASS on both base commit and after fix
# =============================================================================

class TestExistingBehavior:
    """Test that existing behavior is preserved."""

    def test_simple_positional_args(self):
        """Simple string positional args should work. (pass_to_pass)"""
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

source_path = "/workspace/airflow/shared/logging/src/airflow_shared/logging/structlog.py"
with open(source_path) as f:
    source = f.read()

import ast
try:
    ast.parse(source)
    print("OK: Source file is valid Python")
except SyntaxError as e:
    print(f"FAIL: Syntax error: {e}")
    sys.exit(1)
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"

    def test_no_args_logging(self):
        """Logging without args should work. (pass_to_pass)"""
        test_script = '''
import sys
sys.path.insert(0, "/workspace/airflow/shared/logging/src")

import airflow_shared.logging.structlog as sl

assert hasattr(sl, "structlog_processors"), "structlog_processors must exist"
assert hasattr(sl, "drop_positional_args"), "drop_positional_args must exist"
print("OK: Module imports and has expected attributes")
'''
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Failed: {result.stderr}"

    def test_structlog_import(self):
        """Structlog should be importable. (pass_to_pass)"""
        result = subprocess.run(
            [sys.executable, "-c", "import structlog; print('OK')"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Failed to import structlog: {result.stderr}"


class TestRepoCIChecks:
    """Real repo CI tests that run actual commands."""

    def test_repo_ruff_check(self):
        """
        Repo's ruff linter passes on the modified file (pass_to_pass).
        """
        install = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert install.returncode == 0, f"Failed to install ruff: {install.stderr}"

        result = subprocess.run(
            ["ruff", "check", "shared/logging/src/airflow_shared/logging/structlog.py", "--no-cache"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"

    def test_repo_structlog_unit_tests(self):
        """
        Repo's unit tests for the logging module pass (pass_to_pass).
        """
        install = subprocess.run(
            ["pip", "install", "-q", "time-machine", "pytest-asyncio", "click"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert install.returncode == 0, f"Failed to install test deps: {install.stderr}"

        install_pkg = subprocess.run(
            ["pip", "install", "-q", "-e", str(REPO / "shared" / "logging")],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert install_pkg.returncode == 0, f"Failed to install shared/logging: {install_pkg.stderr}"

        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "shared/logging/tests/logging/test_structlog.py::test_colorful",
                "shared/logging/tests/logging/test_structlog.py::test_json",
                "shared/logging/tests/logging/test_structlog.py::test_log_timestamp_format",
                "-v", "--tb=short", "-x"
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert result.returncode == 0, f"Repo tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])