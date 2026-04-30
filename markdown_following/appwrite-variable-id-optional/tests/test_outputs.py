"""Tests for appwrite-variable-id-optional task.

Verifies that the createProjectVariable endpoint correctly makes variableId optional
with a default value that generates unique IDs.
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/appwrite"
TARGET_FILE = f"{REPO}/src/Appwrite/Platform/Modules/Project/Http/Project/Variables/Create.php"
COMPOSER_JSON = f"{REPO}/composer.json"


def php_syntax_valid():
    """Check if PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def extract_param_info(param_line):
    """Parse the variableId param line to extract key information.

    Returns dict with 'default' (the default value string) and 'is_optional' (bool).
    """
    # Find param name
    name_match = re.search(r"->param\s*\(\s*'([^']+)'", param_line)
    if not name_match:
        return None

    # After name, find default (2nd arg - quoted string)
    rest = param_line[name_match.end():]
    comma_pos = rest.find(',')
    if comma_pos == -1:
        return None

    after_name = rest[comma_pos+1:].strip()
    default_match = re.match(r"'([^']*)'", after_name)
    default = default_match.group(1) if default_match else None

    # The optional flag is the 5th argument, which comes just before the injects array
    # Pattern: , [dbForProject] at end of param definition
    # The optional flag is right before this pattern
    opt_match = re.search(r',\s*(true|false)\s*,\s*\[', param_line)
    is_optional = opt_match.group(1).lower() == 'true' if opt_match else False

    return {'default': default, 'is_optional': is_optional}


def test_php_syntax_valid():
    """Verify the modified PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_param_optional():
    """Verify variableId param is marked as optional.

    In Appwrite's param system, the optional flag is the 5th argument.
    A truthy value means the param is optional (not required).
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the variableId param line
    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break

    assert param_line is not None, "Could not find variableId param definition"

    info = extract_param_info(param_line)
    assert info is not None, f"Could not parse param line: {param_line[:100]}"

    assert info['is_optional'], (
        f"variableId param must be optional (5th argument should be truthy).\n"
        f"The optional flag must be true to allow requests without variableId.\n"
        f"Found optional flag: {info['is_optional']}"
    )


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_has_non_empty_default():
    """Verify variableId param has a non-empty default value.

    A non-empty default is required for optional params so that when no variableId
    is provided, a valid unique ID is generated automatically.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break

    assert param_line is not None, "Could not find variableId param definition"

    info = extract_param_info(param_line)
    assert info is not None, f"Could not parse param line"

    default = info.get('default')
    assert default is not None, f"variableId param has no default value"
    assert default != '', f"variableId param default must be non-empty for optional params with auto-generation"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_uses_custom_id_validator():
    """Verify variableId param uses the CustomId validator.

    The CustomId validator is required to validate user-provided variableIds
    while allowing auto-generated unique IDs.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break

    assert param_line is not None, "Could not find variableId param definition"

    assert 'CustomId' in param_line, (
        f"variableId param must use CustomId validator to validate user-provided IDs.\n"
        f"CustomId not found in param line."
    )


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_matches_pattern_used_elsewhere():
    """Verify variableId param follows the same optional pattern as other variable endpoints.

    Functions and Sites variable endpoints use optional variableId with auto-generation.
    This test ensures the Project variable endpoint follows the same pattern.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break

    assert param_line is not None, "Could not find variableId param definition"

    info = extract_param_info(param_line)
    assert info is not None, f"Could not parse param line"

    # Both conditions must be true: optional AND non-empty default
    is_optional = info.get('is_optional', False)
    has_valid_default = info.get('default') not in (None, '')

    assert is_optional and has_valid_default, (
        f"variableId must be optional with non-empty default (like Functions/Sites endpoints).\n"
        f"Optional: {is_optional}, Default: '{info.get('default')}'"
    )


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks)
# These tests verify that repo-level CI/CD checks pass both before and after
# the gold fix is applied, ensuring the fix doesn't break existing functionality.
# =============================================================================


def test_repo_composer_validate():
    """Repo's composer.json is valid (pass_to_pass).

    This test validates that composer.json has valid structure and schema.
    This is a CI check that runs on every PR.
    """
    result = subprocess.run(
        ["composer", "validate", "--no-check-publish", COMPOSER_JSON],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"composer validate failed:\n{result.stdout}\n{result.stderr}"


def test_repo_php_syntax_all():
    """All PHP files in modified module have valid syntax (pass_to_pass).

    This test runs php -l on all PHP files in the Variables module
    to ensure no syntax errors were introduced.
    """
    variables_dir = os.path.dirname(TARGET_FILE)
    php_files = []
    for root, _, files in os.walk(variables_dir):
        for f in files:
            if f.endswith('.php'):
                php_files.append(os.path.join(root, f))

    errors = []
    for php_file in php_files:
        result = subprocess.run(
            ["php", "-l", php_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append(f"{php_file}: {result.stderr}")

    assert not errors, f"PHP syntax errors found:\n" + "\n".join(errors[:5])


def test_repo_pint_lint():
    """Repo passes PSR-12 lint checks (pass_to_pass).

    This test runs Laravel Pint to verify all PHP files follow PSR-12
    coding standards. This is a CI check that runs on every PR.
    """
    # First install dependencies
    install_result = subprocess.run(
        ["composer", "install", "--ignore-platform-reqs"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert install_result.returncode == 0, f"composer install failed:\n{install_result.stderr[-500:]}"

    # Run Pint linter
    result = subprocess.run(
        [f"{REPO}/vendor/bin/pint", "--test", "--config", f"{REPO}/pint.json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Pint lint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_phpstan_variables():
    """Modified file passes PHPStan static analysis (pass_to_pass).

    This test runs PHPStan level 3 static analysis on the modified Variables
    Create.php file. This is the same check that runs in CI.
    """
    # First install dependencies (idempotent if already installed)
    install_result = subprocess.run(
        ["composer", "install", "--ignore-platform-reqs"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert install_result.returncode == 0, f"composer install failed:\n{install_result.stderr[-500:]}"

    # Run PHPStan on the modified file only (faster than full analysis)
    result = subprocess.run(
        [
            f"{REPO}/vendor/bin/phpstan",
            "analyse",
            "-c", f"{REPO}/phpstan.neon",
            "--memory-limit=1G",
            "--no-progress",
            TARGET_FILE,
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHPStan analysis failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_unit_custom_id():
    """CustomId validator unit tests pass (pass_to_pass).

    This test runs the unit tests for the CustomId validator, which is
    the validator used by the variableId parameter in the fix.
    """
    # First install dependencies (idempotent if already installed)
    install_result = subprocess.run(
        ["composer", "install", "--ignore-platform-reqs"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert install_result.returncode == 0, f"composer install failed:\n{install_result.stderr[-500:]}"

    # Run unit tests for CustomId validator
    result = subprocess.run(
        [
            f"{REPO}/vendor/bin/phpunit",
            f"{REPO}/tests/unit/Utopia/Database/Validator/CustomIdTest.php",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"CustomId unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
