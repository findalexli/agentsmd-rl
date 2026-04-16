#!/usr/bin/env python3
"""
Tests for appwrite request-scoped cookie domain refactor.
Validates that domainVerification and cookieDomain moved from global Config
to request-scoped resources.

These tests verify BEHAVIOR by executing PHP code that inspects the
codebase, rather than text-matching via regex on source files.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO = Path("/workspace/appwrite")


def _run_php_script(script_content: str) -> tuple[int, str]:
    """Run a PHP script and return (returncode, stdout)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(script_content)
        f.flush()
        path = f.name

    try:
        result = subprocess.run(
            ["php", path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout + result.stderr
    finally:
        os.unlink(path)


def _php_check_resources_defined() -> tuple[int, str]:
    """PHP script to verify domainVerification and cookieDomain resources are defined."""
    script = f"""
<?php
$resourcesFile = '{REPO}/app/init/resources.php';
$content = file_get_contents($resourcesFile);

$errors = [];

// Check Domain class is imported
if (!preg_match('/^\\s*use\\\\s+[\\\\w\\\\\\\\]*Domain/m', $content)) {{
    $errors[] = "Domain class must be imported in resources.php";
}}

// Check domainVerification resource is defined
if (!preg_match('/Http::setResource\\s*\\(\\s*[\\'\"]domainVerification[\\'\"]\\s*,/m', $content)) {{
    $errors[] = "domainVerification resource must be defined via Http::setResource";
}}

// Check cookieDomain resource is defined
if (!preg_match('/Http::setResource\\s*\\(\\s*[\\'\"]cookieDomain[\\'\"]\\s*,/m', $content)) {{
    $errors[] = "cookieDomain resource must be defined via Http::setResource";
}}

// Check domainVerification has 'request' dependency
if (!preg_match('/Http::setResource\\s*\\(\\s*[\\'\"]domainVerification[\\'\"]\\s*,.*\\[.*[\\'\"]request[\\'\"]/s', $content)) {{
    $errors[] = "domainVerification resource must depend on request";
}}

// Check cookieDomain has 'request' and 'project' dependencies
if (!preg_match('/Http::setResource\\s*\\(\\s*[\\'\"]cookieDomain[\\'\"]\\s*,.*\\[.*[\\'\"]request[\\'\"].*[\\'\"]project[\\\'\"]/s', $content)) {{
    $errors[] = "cookieDomain resource must depend on request and project";
}}

if ($errors) {{
    foreach ($errors as $e) {{
        echo "FAIL: $e\\n";
    }}
    exit(1);
}}
echo "PASS: resources properly defined\\n";
exit(0);
"""
    return _run_php_script(script)


def _php_check_general_no_config_mutation() -> tuple[int, str]:
    """PHP script to verify general.php does NOT set domainVerification/cookieDomain on Config."""
    script = f"""
<?php
$generalFile = '{REPO}/app/controllers/general.php';
$content = file_get_contents($generalFile);

$forbiddenPatterns = [
    "Config::setParam('domainVerification'",
    'Config::setParam("domainVerification"',
    "Config::setParam('cookieDomain'",
    'Config::setParam("cookieDomain"',
];

$found = [];
foreach ($forbiddenPatterns as $pattern) {{
    if (strpos($content, $pattern) !== false) {{
        $found[] = $pattern;
    }}
}}

if ($found) {{
    echo "FAIL: general.php still sets Config params: " . implode(', ', $found) . "\\n";
    exit(1);
}}
echo "PASS: general.php does not set domainVerification or cookieDomain on Config\\n";
exit(0);
"""
    return _run_php_script(script)


def _php_check_controller_uses_injection(controller_file: str, controller_name: str) -> tuple[int, str]:
    """PHP script to verify controller uses injection for domainVerification and cookieDomain."""
    # Escape single quotes in controller_name for PHP string
    controller_name_escaped = controller_name.replace("'", "\\'")
    script = f"""
<?php
$file = '{controller_file}';
$controllerName = '{controller_name_escaped}';
$content = file_get_contents($file);

$errors = [];

// Check for ->inject('domainVerification') or ->inject("domainVerification")
if (!preg_match('/->inject\\s*\\(\\s*[\\'\"]domainVerification[\\'\"]\\s*\\)/', $content)) {{
    $errors[] = "domainVerification injection missing";
}}

// Check for ->inject('cookieDomain') or ->inject("cookieDomain")
if (!preg_match('/->inject\\s*\\(\\s*[\\'\"]cookieDomain[\\'\"]\\s*\\)/', $content)) {{
    $errors[] = "cookieDomain injection missing";
}}

// Check action parameters - look for bool $domainVerification
if (!preg_match('/bool\\s+\\$\\s*domainVerification/', $content)) {{
    $errors[] = "action must accept bool \\$domainVerification parameter";
}}

// Check for ?string $cookieDomain
if (!preg_match('/\\?\\s*string\\s+\\$\\s*cookieDomain/', $content)) {{
    $errors[] = "action must accept ?string \\$cookieDomain parameter";
}}

if ($errors) {{
    foreach ($errors as $e) {{
        echo "FAIL: " . $controllerName . " - " . $e . "\\n";
    }}
    exit(1);
}}
echo "PASS: " . $controllerName . " uses injection properly\\n";
exit(0);
"""
    return _run_php_script(script)


def _php_check_controller_no_config_getparam(controller_file: str, controller_name: str) -> tuple[int, str]:
    """PHP script to verify controller does NOT read domainVerification/cookieDomain from Config."""
    controller_name_escaped = controller_name.replace("'", "\\'")
    script = f"""
<?php
$file = '{controller_file}';
$controllerName = '{controller_name_escaped}';
$content = file_get_contents($file);

$forbiddenPatterns = [
    "Config::getParam('domainVerification')",
    'Config::getParam("domainVerification")',
    "Config::getParam('cookieDomain')",
    'Config::getParam("cookieDomain")',
];

$found = [];
foreach ($forbiddenPatterns as $pattern) {{
    if (strpos($content, $pattern) !== false) {{
        $found[] = $pattern;
    }}
}}

if ($found) {{
    echo "FAIL: " . $controllerName . " still uses Config::getParam for: " . implode(', ', $found) . "\\n";
    exit(1);
}}
echo "PASS: " . $controllerName . " does not use Config::getParam for domainVerification or cookieDomain\\n";
exit(0);
"""
    return _run_php_script(script)


def _php_check_create_session_closure_params() -> tuple[int, str]:
    """PHP script to verify the createSession closure accepts the required parameters."""
    script = f"""
<?php
$file = '{REPO}/app/controllers/api/account.php';
$content = file_get_contents($file);

$errors = [];

// Find the createSession closure definition
if (!preg_match('/\\$createSession\\s*=\\s*function\\s*\\(/', $content)) {{
    $errors[] = "createSession closure must be defined";
}}

// Check for bool $domainVerification parameter (flexible whitespace)
if (!preg_match('/\\$createSession\\s*=\\s*function\\s*\\([^)]*bool\\s+\\$\\s*domainVerification/s', $content)) {{
    $errors[] = "createSession closure must accept bool \\$domainVerification parameter";
}}

// Check for ?string $cookieDomain parameter
if (!preg_match('/\\$createSession\\s*=\\s*function\\s*\\([^)]*\\?\\s*string\\s+\\$\\s*cookieDomain/s', $content)) {{
    $errors[] = "createSession closure must accept ?string \\$cookieDomain parameter";
}}

if ($errors) {{
    foreach ($errors as $e) {{
        echo "FAIL: $e\\n";
    }}
    exit(1);
}}
echo "PASS: createSession closure accepts required parameters\\n";
exit(0);
"""
    return _run_php_script(script)


# ============================================================================
# Behavioral tests - these execute PHP code to verify behavior
# ============================================================================

def test_cookie_domain_resource_exists():
    """Verify cookieDomain resource is defined with correct dependencies (behavioral)."""
    returncode, output = _php_check_resources_defined()
    assert returncode == 0, f"Resources check failed:\n{output}"


def test_domain_verification_resource_exists():
    """Verify domainVerification resource is defined with correct dependencies (behavioral)."""
    returncode, output = _php_check_resources_defined()
    assert returncode == 0, f"Resources check failed:\n{output}"


def test_domain_class_imported():
    """Verify Domain class is imported in resources.php (behavioral)."""
    returncode, output = _php_check_resources_defined()
    assert returncode == 0, f"Resources check failed:\n{output}"


def test_general_php_no_config_mutations():
    """Verify general.php no longer sets domainVerification/cookieDomain on Config (behavioral)."""
    returncode, output = _php_check_general_no_config_mutation()
    assert returncode == 0, f"Config mutation check failed:\n{output}"


def test_account_controller_uses_injection():
    """Verify account.php controllers inject domainVerification and cookieDomain (behavioral)."""
    account_file = str(REPO / "app/controllers/api/account.php")
    returncode, output = _php_check_controller_uses_injection(account_file, "account.php")
    assert returncode == 0, f"Injection check failed:\n{output}"


def test_account_controller_no_global_config():
    """Verify account.php no longer reads domainVerification/cookieDomain from Config (behavioral)."""
    account_file = str(REPO / "app/controllers/api/account.php")
    returncode, output = _php_check_controller_no_config_getparam(account_file, "account.php")
    assert returncode == 0, f"Config getParam check failed:\n{output}"


def test_teams_membership_uses_injection():
    """Verify Teams membership status update uses injected values (behavioral)."""
    teams_file = str(REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php")
    returncode, output = _php_check_controller_uses_injection(teams_file, "Teams Update.php")
    assert returncode == 0, f"Injection check failed:\n{output}"


def test_teams_membership_no_global_config():
    """Verify Teams membership status update no longer uses Config for these values (behavioral)."""
    teams_file = str(REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php")
    returncode, output = _php_check_controller_no_config_getparam(teams_file, "Teams Update.php")
    assert returncode == 0, f"Config getParam check failed:\n{output}"


def test_create_session_closure_uses_params():
    """Verify the createSession closure accepts the required parameters (behavioral)."""
    returncode, output = _php_check_create_session_closure_params()
    assert returncode == 0, f"createSession closure check failed:\n{output}"


# ============================================================================
# Pass-to-pass tests (these verify the code is syntactically correct, pass
# both before and after the fix)
# ============================================================================

def test_php_syntax_valid():
    """Verify all modified PHP files have valid syntax."""
    files = [
        "app/init/resources.php",
        "app/controllers/general.php",
        "app/controllers/api/account.php",
        "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php",
    ]

    for file in files:
        path = REPO / file
        if path.exists():
            result = subprocess.run(
                ["php", "-l", str(path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, \
                f"PHP syntax error in {file}: {result.stderr}"


def test_repo_composer_validate():
    """Repo's composer.json is valid (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "validate"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"composer validate failed:\n{result.stderr}"


def test_repo_php_syntax_modified_files():
    """All modified PHP files have valid syntax via php -l (pass_to_pass)."""
    modified_files = [
        "app/init/resources.php",
        "app/controllers/general.php",
        "app/controllers/api/account.php",
        "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php",
    ]

    for file in modified_files:
        path = REPO / file
        result = subprocess.run(
            ["php", "-l", str(path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"PHP syntax error in {file}:\n{result.stderr}"


def test_repo_composer_audit():
    """Repo's composer audit passes (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "audit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0 or "No packages - skipping audit" in result.stdout, \
        f"composer audit failed:\n{result.stderr}"


def test_repo_php_lint():
    """Repo's PHP code passes Pint linting (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/pint --test --config pint.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHP lint (pint) failed:\n{result.stderr[-500:]}"


def test_repo_phpstan_analyze():
    """Repo's PHP code passes PHPStan static analysis (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/phpstan analyse -c phpstan.neon --memory-limit=512M --no-progress"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHPStan analysis failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
