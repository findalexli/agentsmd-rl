"""Tests for appwrite-variable-id-optional task.

Verifies that the createProjectVariable endpoint correctly makes variableId optional
with a default value of 'unique()' to match other variable creation endpoints.
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


def test_php_syntax_valid():
    """Verify the modified PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_param_optional_with_unique_default():
    """Verify variableId param is optional (5th param is true) with 'unique()' default."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Extract just the param line using line-based extraction
    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break
    
    assert param_line is not None, "Could not find variableId param line"
    
    # Check for the key elements
    assert "'unique()'" in param_line, "variableId param should have 'unique()' as default"
    assert "true" in param_line, "variableId param should have true as optional flag"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_matches_function_and_sites_behavior():
    """Verify the fix matches patterns used in Functions and Sites variable endpoints."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the param line
    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break
    
    assert param_line is not None, "Could not find variableId param line"
    
    # Check for unique() and CustomId
    assert "'unique()'" in param_line, "variableId param should use 'unique()' default"
    assert "CustomId" in param_line, "variableId param should use CustomId validator"


@pytest.mark.skipif(not php_syntax_valid(), reason="PHP syntax errors prevent structural analysis")
def test_variable_id_param_not_required():
    """Verify variableId param is explicitly marked as optional."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the param line
    lines = content.split('\n')
    param_line = None
    for line in lines:
        if "->param('variableId'" in line:
            param_line = line
            break
    
    assert param_line is not None, "Could not find variableId param line"
    
    # The param structure is:
    # ->param('variableId', 'unique()', fn(...) => new CustomId(...), 'description...', true, ['dbForProject'])
    # We need to verify that the 5th argument (optional) is 'true'
    
    # Split by comma and find the argument after the description (which ends with '...chars.\'')
    # The line should end with: true, ['dbForProject'])
    parts = param_line.split(',')
    
    # Look for the 'true' part that's before the injects array
    # The last two parts should be: " true" and " ['dbForProject'])"
    # or if split differently, we need to find "true" as a standalone argument
    found_true = False
    for i, part in enumerate(parts):
        part = part.strip()
        # Check if this part is 'true' and the next part is the injects array
        if part == 'true' and i + 1 < len(parts):
            next_part = parts[i + 1].strip()
            if next_part.startswith('[') or 'dbForProject' in next_part:
                found_true = True
                break
    
    assert found_true, (
        f"variableId param must be optional (5th argument should be 'true').\n"
        f"The optional flag must be true to allow requests without variableId.\n"
        f"Param line: {param_line[:100]}..."
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
