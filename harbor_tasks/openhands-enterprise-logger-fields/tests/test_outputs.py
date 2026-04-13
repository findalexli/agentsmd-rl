"""
Tests for OpenHands Enterprise Logger Fix (PR #13612)

This tests that the JSON logger now includes module, funcName, and lineno fields.
"""

import json
import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest

# Add enterprise directory to path
REPO = Path("/workspace/OpenHands")
sys.path.insert(0, str(REPO / "enterprise"))
sys.path.insert(0, str(REPO))  # For openhands imports

def get_logger_output():
    """Helper to capture logger output and return parsed JSON."""
    from enterprise.server.logger import setup_json_logger

    string_io = StringIO()
    logger = logging.getLogger("test_logger_" + str(id(string_io)))
    logger.handlers = []  # Clear existing handlers
    logger.filters = []    # Clear filters
    logger.propagate = False

    setup_json_logger(logger, _out=string_io)
    return logger, string_io


def test_logger_includes_module_field():
    """Fail-to-pass: Logger output must include 'module' field."""
    logger, string_io = get_logger_output()

    # Set module to something predictable
    logger.name = "test_logger_module"

    logger.info("Test message for module")
    output = json.loads(string_io.getvalue())

    assert "module" in output, f"Missing 'module' field in output: {output}"
    assert output["module"] == "test_outputs", f"Expected 'test_outputs', got {output['module']}"


def test_logger_includes_funcname_field():
    """Fail-to-pass: Logger output must include 'funcName' field."""
    logger, string_io = get_logger_output()

    def my_test_function():
        logger.info("Test message for funcName")

    my_test_function()
    output = json.loads(string_io.getvalue())

    assert "funcName" in output, f"Missing 'funcName' field in output: {output}"
    assert output["funcName"] == "my_test_function", f"Expected 'my_test_function', got {output['funcName']}"


def test_logger_includes_lineno_field():
    """Fail-to-pass: Logger output must include 'lineno' field."""
    logger, string_io = get_logger_output()

    # Log from a specific line - lineno should be an integer
    logger.info("Test message for lineno")  # This is line 59
    output = json.loads(string_io.getvalue())

    assert "lineno" in output, f"Missing 'lineno' field in output: {output}"
    assert isinstance(output["lineno"], int), f"lineno should be an integer, got {type(output['lineno'])}"
    assert output["lineno"] > 0, f"lineno should be positive, got {output['lineno']}"


def test_logger_all_fields_present():
    """Fail-to-pass: All expected fields (message, severity, module, funcName, lineno) must be present."""
    logger, string_io = get_logger_output()

    def comprehensive_test():
        logger.info("Comprehensive test message")

    comprehensive_test()
    output = json.loads(string_io.getvalue())

    required_fields = ["message", "severity", "module", "funcName", "lineno"]
    for field in required_fields:
        assert field in output, f"Missing required field '{field}' in output: {output}"

    assert output["message"] == "Comprehensive test message"
    assert output["severity"] == "INFO"
    assert output["module"] == "test_outputs"
    assert output["funcName"] == "comprehensive_test"


def test_logger_error_level_includes_fields():
    """Fail-to-pass: Error level logs must also include module, funcName, lineno."""
    logger, string_io = get_logger_output()

    def error_test_function():
        logger.error("Error test message")

    error_test_function()
    output = json.loads(string_io.getvalue())

    assert output["message"] == "Error test message"
    assert output["severity"] == "ERROR"
    assert "module" in output, "Missing 'module' field in ERROR log"
    assert "funcName" in output, "Missing 'funcName' field in ERROR log"
    assert "lineno" in output, "Missing 'lineno' field in ERROR log"
    assert output["funcName"] == "error_test_function"


def test_logger_with_extra_fields():
    """Fail-to-pass: Logs with extra fields must include module, funcName, lineno alongside extras."""
    logger, string_io = get_logger_output()

    def extra_fields_test():
        logger.info("Extra fields message", extra={"custom_key": "custom_value"})

    extra_fields_test()
    output = json.loads(string_io.getvalue())

    assert output["message"] == "Extra fields message"
    assert output["severity"] == "INFO"
    assert output["custom_key"] == "custom_value"
    assert "module" in output, "Missing 'module' field in log with extra fields"
    assert "funcName" in output, "Missing 'funcName' field in log with extra fields"
    assert "lineno" in output, "Missing 'lineno' field in log with extra fields"


def test_code_syntax_valid():
    """Pass-to-pass: Modified file must have valid Python syntax."""
    import ast

    logger_file = REPO / "enterprise" / "server" / "logger.py"
    source = logger_file.read_text()

    try:
        ast.parse(source)
    except SyntaxError as e:
        pytest.fail(f"Syntax error in logger.py: {e}")


def test_logger_json_formatter_imports():
    """Pass-to-pass: Logger module must import JsonFormatter correctly."""
    try:
        from enterprise.server.logger import setup_json_logger, JsonFormatter
        assert callable(setup_json_logger)
        assert JsonFormatter is not None
    except ImportError as e:
        pytest.fail(f"Failed to import from logger module: {e}")


# ============================================================================
# Repo CI/CD Pass-to-Pass Tests
# These tests verify that the repo's own CI/CD checks pass on both base
# and after the fix, ensuring candidate solutions don't break existing
# functionality.
# ============================================================================

REPO_ROOT = REPO
ENTERPRISE_DIR = REPO_ROOT / "enterprise"


def test_repo_ruff_lint():
    """Repo's Ruff linting passes on enterprise/server (pass_to_pass).

    Ignores I001 (import sorting) as those are pre-existing in the codebase
    and not related to the fix being tested.
    """
    r = subprocess.run(
        ["poetry", "run", "ruff", "check", "server",
         "--config", "dev_config/python/ruff.toml",
         "--ignore", "I001"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=ENTERPRISE_DIR,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


def test_repo_unit_tests():
    """Repo's enterprise server unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["poetry", "run", "pytest", "tests/unit/server", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=ENTERPRISE_DIR,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_repo_ruff_format():
    """Repo's Ruff format check passes on enterprise/server (pass_to_pass).

    Verifies that all Python files in the server directory follow
    the project's code formatting standards.
    """
    r = subprocess.run(
        ["poetry", "run", "ruff", "format", "--check",
         "--config", "dev_config/python/ruff.toml", "server"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=ENTERPRISE_DIR,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_logger_unit_tests():
    """Repo's logger unit tests pass (pass_to_pass).

    These tests cover the server/logger.py module that the fix modifies,
    ensuring existing logging functionality isn't broken.

    Note: The unit tests check for exact output equality. The fix adds new
    fields (module, funcName, lineno), so we need to update the assertions
    to expect these fields when running on fixed code.
    """
    import re

    test_file = ENTERPRISE_DIR / "tests/unit/test_logger.py"
    content = test_file.read_text()

    # Check if fix is applied by looking at the formatter format string
    logger_file = ENTERPRISE_DIR / "server/logger.py"
    logger_content = logger_file.read_text()
    fix_applied = "%(module)s%(funcName)s%(lineno)d" in logger_content

    if fix_applied:
        # Fix is applied - update assertions to expect new fields
        # For test_info - replace exact equality with field checks
        content = re.sub(
            r"assert output == \{\n            'message': 'Test message',\n            'severity': 'INFO',\n            'ts': FROZEN_TIMESTAMP,\n        \}",
            """assert output['message'] == 'Test message'
        assert output['severity'] == 'INFO'
        assert output['ts'] == FROZEN_TIMESTAMP
        assert 'module' in output
        assert 'funcName' in output
        assert 'lineno' in output""",
            content
        )

        # For test_error - replace exact equality with field checks
        content = re.sub(
            r"assert output == \{\n            'message': 'Test message',\n            'severity': 'ERROR',\n            'ts': FROZEN_TIMESTAMP,\n        \}",
            """assert output['message'] == 'Test message'
        assert output['severity'] == 'ERROR'
        assert output['ts'] == FROZEN_TIMESTAMP
        assert 'module' in output
        assert 'funcName' in output
        assert 'lineno' in output""",
            content
        )

        # For test_extra_fields - replace exact equality with field checks
        content = re.sub(
            r"assert output == \{\n            'key': '\.\.val\.\.',\n            'message': 'Test message',\n            'severity': 'INFO',\n            'ts': FROZEN_TIMESTAMP,\n        \}",
            """assert output['key'] == '..val..'
        assert output['message'] == 'Test message'
        assert output['severity'] == 'INFO'
        assert output['ts'] == FROZEN_TIMESTAMP
        assert 'module' in output
        assert 'funcName' in output
        assert 'lineno' in output""",
            content
        )

        # For test_filtering - replace exact equality with field checks
        content = re.sub(
            r"assert output == \{\n            'message': 'The secret key was \*\*\*\*\*\*',\n            'severity': 'INFO',\n            'ts': FROZEN_TIMESTAMP,\n        \}",
            """assert output['message'] == 'The secret key was ******'
        assert output['severity'] == 'INFO'
        assert output['ts'] == FROZEN_TIMESTAMP
        assert 'module' in output
        assert 'funcName' in output
        assert 'lineno' in output""",
            content
        )

        test_file.write_text(content)

    r = subprocess.run(
        ["poetry", "run", "pytest", "tests/unit/test_logger.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=ENTERPRISE_DIR,
    )
    assert r.returncode == 0, f"Logger unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_repo_pyproject_valid():
    """Repo's pyproject.toml is valid (pass_to_pass)."""
    import tomllib

    pyproject_path = ENTERPRISE_DIR / "pyproject.toml"
    content = pyproject_path.read_text()

    try:
        tomllib.loads(content)
    except Exception as e:
        pytest.fail(f"Invalid pyproject.toml: {e}")


def test_repo_mypy_logger():
    """Repo's mypy type checking passes on server/logger.py (pass_to_pass).

    Verifies that the modified logger module has valid type annotations
    and passes mypy type checking.
    """
    r = subprocess.run(
        ["poetry", "run", "mypy",
         "--config-file", "dev_config/python/mypy.ini",
         "server/logger.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=ENTERPRISE_DIR,
    )
    assert r.returncode == 0, f"MyPy type check failed:\n{r.stdout}\n{r.stderr}"
