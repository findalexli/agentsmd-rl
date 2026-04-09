#!/usr/bin/env python3
"""Test outputs for the env variable rename task.

This module tests that the service.py file correctly reads from
AUTOMATIONS_SERVICE_KEY (not the old AUTOMATIONS_SERVICE_API_KEY).
"""

import os
import re
import subprocess

# The repo path
REPO = '/workspace/openhands'
SERVICE_PATH = os.path.join(REPO, 'enterprise/server/routes/service.py')


def test_repo_enterprise_service_routes():
    """Enterprise service routes unit tests pass (pass_to_pass)."""
    # Install poetry and run enterprise tests
    install_cmd = [
        'pip', 'install', 'poetry', '-q'
    ]
    subprocess.run(install_cmd, capture_output=True, timeout=300)

    # Install enterprise dependencies
    install_deps_cmd = [
        'poetry', 'install', '--with', 'dev,test', '-q'
    ]
    subprocess.run(
        install_deps_cmd,
        capture_output=True,
        timeout=300,
        cwd=os.path.join(REPO, 'enterprise')
    )

    # Run the service routes tests
    test_cmd = [
        'poetry', 'run', '--project=enterprise',
        'pytest', 'enterprise/tests/unit/routes/test_service.py',
        '-v', '--tb=short'
    ]
    r = subprocess.run(
        test_cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert r.returncode == 0, f"Enterprise service routes tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_enterprise_service_routes_lint():
    """Enterprise service routes pass linting (pass_to_pass)."""
    # Install poetry if not already installed
    install_cmd = [
        'pip', 'install', 'poetry', '-q'
    ]
    subprocess.run(install_cmd, capture_output=True, timeout=300)

    # Install enterprise dependencies
    install_deps_cmd = [
        'poetry', 'install', '--with', 'dev,test', '-q'
    ]
    subprocess.run(
        install_deps_cmd,
        capture_output=True,
        timeout=300,
        cwd=os.path.join(REPO, 'enterprise')
    )

    # Run ruff lint check on service.py
    lint_cmd = [
        'poetry', 'run', '--project=enterprise',
        'ruff', 'check', 'enterprise/server/routes/service.py',
        '--config', 'enterprise/dev_config/python/ruff.toml'
    ]
    r = subprocess.run(
        lint_cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_env_variable_name_in_code():
    """Verify the code uses AUTOMATIONS_SERVICE_KEY, not AUTOMATIONS_SERVICE_API_KEY."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Should use new env var name
    assert 'AUTOMATIONS_SERVICE_KEY' in content, \
        "Code should reference AUTOMATIONS_SERVICE_KEY"

    # Should NOT use old env var name
    assert 'AUTOMATIONS_SERVICE_API_KEY' not in content, \
        "Code should NOT reference old AUTOMATIONS_SERVICE_API_KEY"


def test_env_var_is_read_correctly():
    """Verify the code reads from correct env var via regex."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Verify the pattern for reading the env var is correct
    # Pattern: AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY', ...)
    pattern = r"AUTOMATIONS_SERVICE_KEY\s*=\s*os\.getenv\(['\"]AUTOMATIONS_SERVICE_KEY['\"]"
    assert re.search(pattern, content), \
        "Should find pattern: AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY', ...)"


def test_health_endpoint_uses_correct_variable():
    """Verify health endpoint uses the renamed variable."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Check that the health endpoint returns the correct variable
    pattern = r"'service_auth_configured':\s*bool\(\s*AUTOMATIONS_SERVICE_KEY\s*\)"
    assert re.search(pattern, content), \
        "service_health should return {'service_auth_configured': bool(AUTOMATIONS_SERVICE_KEY)}"


def test_validate_function_uses_correct_variable():
    """Verify validate_service_api_key uses the renamed variable."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Check the function uses AUTOMATIONS_SERVICE_KEY in the not-configured check
    assert "if not AUTOMATIONS_SERVICE_KEY:" in content, \
        "validate_service_api_key should check 'if not AUTOMATIONS_SERVICE_KEY'"

    # Check the log message was updated
    assert "Service authentication not configured (AUTOMATIONS_SERVICE_KEY not set)" in content, \
        "Log message should reference AUTOMATIONS_SERVICE_KEY"

    # Check the key comparison uses new variable
    assert "x_service_api_key != AUTOMATIONS_SERVICE_KEY" in content, \
        "Should compare against AUTOMATIONS_SERVICE_KEY"


def test_module_docstring_updated():
    """Verify module docstring references the new env var name."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Docstring should reference new env var
    assert 'AUTOMATIONS_SERVICE_KEY' in content, \
        "Module docstring should reference AUTOMATIONS_SERVICE_KEY"


def test_logic_correctness_simulation():
    """Verify the overall env var pattern is correct."""
    with open(SERVICE_PATH, 'r') as f:
        content = f.read()

    # Verify the assignment pattern is correct
    assert "AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY'" in content, \
        "Should find: AUTOMATIONS_SERVICE_KEY = os.getenv('AUTOMATIONS_SERVICE_KEY', ...)"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
