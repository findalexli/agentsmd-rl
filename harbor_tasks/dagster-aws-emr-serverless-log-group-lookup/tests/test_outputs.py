"""Tests for EMR Serverless log group name lookup fix.

This tests the fix for dagster-io/dagster#33578 where the log group name
was being read from the wrong nesting level in the monitoring configuration.
"""

import sys
import os
import subprocess
import re
import ast


DAGSTER_REPO = "/workspace/dagster"
DAGSTER_AWS_PATH = "/workspace/dagster/python_modules/libraries/dagster-aws"
EMR_SERVERLESS_PATH = f"{DAGSTER_AWS_PATH}/dagster_aws/pipes/clients/emr_serverless.py"


def _extract_log_group_expression_from_source():
    """Extract the log group computation expression from the source file.
    
    Returns a string containing the Python expression that computes log_group.
    Handles multi-line expressions with parentheses.
    """
    with open(EMR_SERVERLESS_PATH, 'r') as f:
        lines = f.readlines()
    
    # Find the line that starts the log_group assignment
    pattern = r'^\s*log_group\s*='
    
    start_line = None
    for i, line in enumerate(lines):
        if re.match(pattern, line):
            start_line = i
            break
    
    if start_line is None:
        return None
    
    # Extract the full expression, handling multi-line with parentheses
    # We need to count parentheses to know when the expression ends
    expression_parts = []
    paren_count = 0
    i = start_line
    
    while i < len(lines):
        line = lines[i]
        
        # Count opening and closing parentheses
        for char in line:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
        
        expression_parts.append(line.rstrip())
        
        # If paren_count is 0 and we've started a new statement (has ;)
        # or we're past the assignment line and hit a line that starts a new statement
        if paren_count == 0 and i > start_line:
            # Check if this looks like a complete expression
            full_expr = ' '.join(expression_parts)
            # Try to see if the next non-empty line starts a new statement
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith('#'):
                    # We might be at a continuation, but let's check if ; is in our expr
                    if ';' in full_expr or (paren_count == 0 and not line.rstrip().endswith('\\')):
                        break
            else:
                break
        i += 1
    
    full_expr = ' '.join(expression_parts)
    # Remove "log_group = " prefix
    match = re.match(r'^\s*log_group\s*=\s*(.+)', full_expr)
    if match:
        return match.group(1).strip()
    return None


def test_log_group_extraction_from_nested_config():
    """Test that log group name is extracted from cloudWatchLoggingConfiguration.

    This is the fail-to-pass test for the bug fix. Before the fix, the code
    looked for logGroupName at the top level of monitoring_configuration,
    but the EMR API nests it under cloudWatchLoggingConfiguration.
    """
    monitoring_config = {
        "cloudWatchLoggingConfiguration": {
            "enabled": True,
            "logGroupName": "/custom/log/group",
            "logStreamNamePrefix": "my-prefix",
        }
    }
    
    # Get the actual code from the source file
    actual_code = _extract_log_group_expression_from_source()
    assert actual_code is not None, "Could not find log_group computation in source"
    
    # Execute the actual code from the file and get the result
    test_code = f'''
monitoring_configuration = {monitoring_config!r}
log_group = {actual_code}
print(log_group)
'''
    
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    assert r.returncode == 0, f"Failed to execute code: {r.stderr}\nCode was:\n{actual_code}"
    result = r.stdout.strip()
    
    # The fixed code should return "/custom/log/group"
    # The buggy code would return "/aws/emr-serverless"
    assert result == "/custom/log/group", (
        f"Expected '/custom/log/group' but got '{result}'. "
        "The log group name should be extracted from cloudWatchLoggingConfiguration.logGroupName. "
        f"Actual code from source: {actual_code}"
    )


def test_log_group_fallback_when_not_configured():
    """Test that default log group is used when cloudWatchLoggingConfiguration.logGroupName is missing."""
    monitoring_config = {
        "cloudWatchLoggingConfiguration": {
            "enabled": True,
        }
    }
    
    actual_code = _extract_log_group_expression_from_source()
    assert actual_code is not None, "Could not find log_group computation in source"
    
    test_code = f'''
monitoring_configuration = {monitoring_config!r}
log_group = {actual_code}
print(log_group)
'''
    
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    assert r.returncode == 0, f"Failed to execute code: {r.stderr}\nCode was:\n{actual_code}"
    result = r.stdout.strip()
    
    # Both buggy and fixed should return default
    assert result == "/aws/emr-serverless", (
        f"Expected default '/aws/emr-serverless' but got '{result}'"
    )


def test_log_group_fallback_with_empty_config():
    """Test that default log group is used when cloudWatchLoggingConfiguration is missing."""
    monitoring_config = {}
    
    actual_code = _extract_log_group_expression_from_source()
    assert actual_code is not None, "Could not find log_group computation in source"
    
    test_code = f'''
monitoring_configuration = {monitoring_config!r}
log_group = {actual_code}
print(log_group)
'''
    
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    assert r.returncode == 0, f"Failed to execute code: {r.stderr}\nCode was:\n{actual_code}"
    result = r.stdout.strip()
    
    # Both buggy and fixed should return default
    assert result == "/aws/emr-serverless", (
        f"Expected default '/aws/emr-serverless' but got '{result}'"
    )


def test_log_group_extraction_variations():
    """Test various configurations to ensure proper extraction."""
    test_cases = [
        ({"cloudWatchLoggingConfiguration": {"logGroupName": "/custom/group"}}, "/custom/group", "Basic nested logGroupName"),
        ({"cloudWatchLoggingConfiguration": {"enabled": True, "logGroupName": "/my/logs"}}, "/my/logs", "Nested with other fields present"),
        ({"cloudWatchLoggingConfiguration": {}}, "/aws/emr-serverless", "Empty cloudWatchLoggingConfiguration"),
        ({}, "/aws/emr-serverless", "Empty monitoring config"),
        ({"cloudWatchLoggingConfiguration": {"logGroupName": ""}}, "/aws/emr-serverless", "Empty string logGroupName"),
        ({"cloudWatchLoggingConfiguration": {"logGroupName": "/prod/emr/jobs"}}, "/prod/emr/jobs", "Production-style log group path"),
    ]
    
    actual_code = _extract_log_group_expression_from_source()
    assert actual_code is not None, "Could not find log_group computation in source"
    
    for config, expected, description in test_cases:
        test_code = f'''
monitoring_configuration = {config!r}
log_group = {actual_code}
print(log_group)
'''
        r = subprocess.run(
            ["python", "-c", test_code],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Test case '{description}' failed to execute: {r.stderr}\nCode was:\n{actual_code}"
        result = r.stdout.strip()
        assert result == expected, (
            f"Test case '{description}' failed: expected '{expected}', got '{result}'. "
            f"Actual code from source: {actual_code}"
        )


def test_fix_is_applied():
    """Test that the fix is actually applied by checking the actual code behavior.

    This test verifies behavior by executing the actual code from the source file,
    not by asserting on specific text patterns (which would fail alternative correct fixes).
    """
    monitoring_config = {"cloudWatchLoggingConfiguration": {"logGroupName": "/custom/log/group"}}
    
    actual_code = _extract_log_group_expression_from_source()
    assert actual_code is not None, "Could not find log_group computation in source"
    
    test_code = f'''
monitoring_configuration = {monitoring_config!r}
log_group = {actual_code}
print(log_group)
'''
    
    r = subprocess.run(
        ["python", "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    assert r.returncode == 0, f"Failed to execute code: {r.stderr}\nCode was:\n{actual_code}"
    result = r.stdout.strip()
    
    # If the fix is applied, this will return "/custom/log/group"
    # If the bug is present, this will return "/aws/emr-serverless"
    assert result == "/custom/log/group", (
        f"The fix appears not to be applied. Expected '/custom/log/group' but got '{result}'. "
        f"The actual code is still reading logGroupName from the wrong level. "
        f"Actual code from source: {actual_code}"
    )


def test_emr_serverless_file_syntax():
    """Verify the Python file has valid syntax."""
    r = subprocess.run(
        ["python", "-m", "py_compile", EMR_SERVERLESS_PATH],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


def test_ruff_linting():
    """Pass-to-pass test: Repo ruff linting passes."""
    r = subprocess.run(
        ["make", "ruff"],
        cwd=DAGSTER_REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff linting failed: {r.stderr[-1000:]}"


def test_ruff_check_dagster_aws():
    """Pass-to-pass test: Ruff check passes on dagster-aws package."""
    r = subprocess.run(
        ["ruff", "check", "."],
        cwd=DAGSTER_AWS_PATH,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed: {r.stderr[-500:]}"


def test_ruff_format_check_dagster_aws():
    """Pass-to-pass test: Ruff format check passes on dagster-aws package."""
    r = subprocess.run(
        ["ruff", "format", "--check", "."],
        cwd=DAGSTER_AWS_PATH,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff format check failed: {r.stderr[-500:]}"


def test_dagster_aws_package_syntax():
    """Pass-to-pass test: All Python files in dagster-aws have valid syntax."""
    import glob
    py_files = glob.glob(f"{DAGSTER_AWS_PATH}/dagster_aws/**/*.py", recursive=True)
    py_files += glob.glob(f"{DAGSTER_AWS_PATH}/dagster_aws/pipes/**/*.py", recursive=True)
    for py_file in set(py_files):
        r = subprocess.run(
            ["python", "-m", "py_compile", py_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"Syntax check failed for {py_file}: {r.stderr}"
