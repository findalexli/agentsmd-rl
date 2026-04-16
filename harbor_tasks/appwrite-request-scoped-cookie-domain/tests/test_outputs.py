#!/usr/bin/env python3
"""
Behavioral tests for domainVerification and cookieDomain request-scoped resource refactor.

Tests verify actual runtime behavior by:
- Loading and executing resources.php, then inspecting Http framework state via Reflection
- Using PHP's tokenizer (token_get_all) to analyze controller code at the AST level
- Running PHP syntax checks, linting, and static analysis
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO = Path("/workspace/appwrite")


def _run_php(script: str) -> tuple[int, str]:
    """Write a PHP script to a temp file, execute it, return (returncode, output)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(script)
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


# ============================================================================
# Fail-to-pass: Resource registration (behavioral — loads and executes PHP)
# ============================================================================

def test_domainVerification_resource_registered():
    """Load resources.php and verify the Http framework has a domainVerification resource."""
    rc, out = _run_php("""<?php
require '__REPO__/vendor/autoload.php';
require '__REPO__/app/init/resources.php';

$ref = new ReflectionClass(Utopia\\Http\\Http::class);
$prop = $ref->getProperty('resourcesCallbacks');
$prop->setAccessible(true);
$cbs = $prop->getValue();

if (!isset($cbs['domainVerification'])) {
    fwrite(STDERR, "domainVerification resource not registered in Http framework\\n");
    exit(1);
}
if (!is_callable($cbs['domainVerification']['callback'])) {
    fwrite(STDERR, "domainVerification callback is not callable\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"domainVerification resource not registered:\n{out}"


def test_cookieDomain_resource_registered():
    """Load resources.php and verify the Http framework has a cookieDomain resource."""
    rc, out = _run_php("""<?php
require '__REPO__/vendor/autoload.php';
require '__REPO__/app/init/resources.php';

$ref = new ReflectionClass(Utopia\\Http\\Http::class);
$prop = $ref->getProperty('resourcesCallbacks');
$prop->setAccessible(true);
$cbs = $prop->getValue();

if (!isset($cbs['cookieDomain'])) {
    fwrite(STDERR, "cookieDomain resource not registered in Http framework\\n");
    exit(1);
}
if (!is_callable($cbs['cookieDomain']['callback'])) {
    fwrite(STDERR, "cookieDomain callback is not callable\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"cookieDomain resource not registered:\n{out}"


def test_domainVerification_depends_on_request():
    """Load resources.php and verify domainVerification declares 'request' as a dependency."""
    rc, out = _run_php("""<?php
require '__REPO__/vendor/autoload.php';
require '__REPO__/app/init/resources.php';

$ref = new ReflectionClass(Utopia\\Http\\Http::class);
$prop = $ref->getProperty('resourcesCallbacks');
$prop->setAccessible(true);
$cbs = $prop->getValue();

if (!isset($cbs['domainVerification'])) {
    fwrite(STDERR, "domainVerification resource not registered\\n");
    exit(1);
}
$deps = $cbs['domainVerification']['injections'];
if (!in_array('request', $deps)) {
    fwrite(STDERR, "domainVerification does not depend on 'request'; deps: " . implode(', ', $deps) . "\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"domainVerification missing request dependency:\n{out}"


def test_cookieDomain_depends_on_request_and_project():
    """Load resources.php and verify cookieDomain declares 'request' and 'project' dependencies."""
    rc, out = _run_php("""<?php
require '__REPO__/vendor/autoload.php';
require '__REPO__/app/init/resources.php';

$ref = new ReflectionClass(Utopia\\Http\\Http::class);
$prop = $ref->getProperty('resourcesCallbacks');
$prop->setAccessible(true);
$cbs = $prop->getValue();

if (!isset($cbs['cookieDomain'])) {
    fwrite(STDERR, "cookieDomain resource not registered\\n");
    exit(1);
}
$deps = $cbs['cookieDomain']['injections'];
if (!in_array('request', $deps) || !in_array('project', $deps)) {
    fwrite(STDERR, "cookieDomain must depend on 'request' and 'project'; got: " . implode(', ', $deps) . "\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"cookieDomain missing dependencies:\n{out}"


def test_domainVerification_callback_defined_in_resources():
    """Verify the domainVerification callback is defined in resources.php and uses Domain class."""
    rc, out = _run_php("""<?php
require '__REPO__/vendor/autoload.php';
require '__REPO__/app/init/resources.php';

$ref = new ReflectionClass(Utopia\\Http\\Http::class);
$prop = $ref->getProperty('resourcesCallbacks');
$prop->setAccessible(true);
$cbs = $prop->getValue();

if (!isset($cbs['domainVerification'])) {
    fwrite(STDERR, "domainVerification resource not registered\\n");
    exit(1);
}

// Verify the callback closure was defined in resources.php
$funcRef = new ReflectionFunction($cbs['domainVerification']['callback']);
$file = $funcRef->getFileName();
if (strpos($file, 'resources.php') === false) {
    fwrite(STDERR, "domainVerification callback not defined in resources.php; found in: $file\\n");
    exit(1);
}

// Verify the callback body references Domain class (required for domain comparison)
$startLine = $funcRef->getStartLine();
$endLine = $funcRef->getEndLine();
$lines = array_slice(file($file), $startLine - 1, $endLine - $startLine + 1);
$body = implode('', $lines);
if (stripos($body, 'Domain') === false) {
    fwrite(STDERR, "domainVerification callback does not use Domain class\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"domainVerification callback check failed:\n{out}"


# ============================================================================
# Fail-to-pass: Config mutation removal (PHP tokenizer — parses actual PHP)
# ============================================================================

def test_general_php_no_config_mutation():
    """Verify general.php does not set domainVerification or cookieDomain via Config::setParam.

    Uses PHP's token_get_all() to parse the file at the AST token level, then walks
    the token stream to find Config::setParam calls with these specific keys.
    """
    rc, out = _run_php("""<?php
$tokens = token_get_all(file_get_contents('__REPO__/app/controllers/general.php'));
$forbidden = ['domainVerification', 'cookieDomain'];
$found = [];
$len = count($tokens);

for ($i = 0; $i < $len; $i++) {
    if (!is_array($tokens[$i]) || $tokens[$i][1] !== 'Config') continue;

    $j = $i + 1;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || !is_array($tokens[$j]) || $tokens[$j][0] !== T_DOUBLE_COLON) continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || !is_array($tokens[$j]) || $tokens[$j][1] !== 'setParam') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || $tokens[$j] !== '(') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;

    if ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_CONSTANT_ENCAPSED_STRING) {
        $key = trim($tokens[$j][1], "'\\"");
        if (in_array($key, $forbidden)) {
            $found[] = "$key (line {$tokens[$i][2]})";
        }
    }
}

if ($found) {
    fwrite(STDERR, "general.php still sets Config for: " . implode(', ', $found) . "\\n");
    exit(1);
}
echo "PASS";
""".replace('__REPO__', str(REPO)))
    assert rc == 0, f"general.php still mutates Config:\n{out}"


# ============================================================================
# Fail-to-pass: Controller migration (PHP tokenizer — parses actual PHP)
# ============================================================================

def _check_no_config_getparam(filepath: str, keys: list[str]) -> tuple[int, str]:
    """PHP tokenizer check: file does not call Config::getParam for the given keys."""
    keys_php = ', '.join(f"'{k}'" for k in keys)
    return _run_php("""<?php
$tokens = token_get_all(file_get_contents('__FILE__'));
$forbidden = [__KEYS__];
$found = [];
$len = count($tokens);

for ($i = 0; $i < $len; $i++) {
    if (!is_array($tokens[$i]) || $tokens[$i][1] !== 'Config') continue;

    $j = $i + 1;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || !is_array($tokens[$j]) || $tokens[$j][0] !== T_DOUBLE_COLON) continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || !is_array($tokens[$j]) || $tokens[$j][1] !== 'getParam') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || $tokens[$j] !== '(') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;

    if ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_CONSTANT_ENCAPSED_STRING) {
        $key = trim($tokens[$j][1], "'\\"");
        if (in_array($key, $forbidden)) {
            $found[] = "$key (line {$tokens[$i][2]})";
        }
    }
}

if ($found) {
    fwrite(STDERR, "Still uses Config::getParam for: " . implode(', ', $found) . "\\n");
    exit(1);
}
echo "PASS";
""".replace('__FILE__', filepath).replace('__KEYS__', keys_php))


def _check_has_inject_calls(filepath: str, resource_names: list[str]) -> tuple[int, str]:
    """PHP tokenizer check: file contains ->inject('resourceName') for each given name."""
    names_php = ', '.join(f"'{n}'" for n in resource_names)
    return _run_php("""<?php
$tokens = token_get_all(file_get_contents('__FILE__'));
$required = [__NAMES__];
$found = [];
$len = count($tokens);

for ($i = 0; $i < $len; $i++) {
    if (!is_array($tokens[$i]) || $tokens[$i][0] !== T_OBJECT_OPERATOR) continue;

    $j = $i + 1;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || !is_array($tokens[$j]) || $tokens[$j][1] !== 'inject') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;
    if ($j >= $len || $tokens[$j] !== '(') continue;
    $j++;
    while ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_WHITESPACE) $j++;

    if ($j < $len && is_array($tokens[$j]) && $tokens[$j][0] === T_CONSTANT_ENCAPSED_STRING) {
        $name = trim($tokens[$j][1], "'\\"");
        if (in_array($name, $required)) {
            $found[$name] = true;
        }
    }
}

$missing = array_diff($required, array_keys($found));
if ($missing) {
    fwrite(STDERR, "Missing inject() calls for: " . implode(', ', $missing) . "\\n");
    exit(1);
}
echo "PASS";
""".replace('__FILE__', filepath).replace('__NAMES__', names_php))


def test_account_controller_no_config_getparam():
    """Verify account.php does not read domainVerification or cookieDomain from Config::getParam."""
    filepath = str(REPO / "app/controllers/api/account.php")
    rc, out = _check_no_config_getparam(filepath, ['domainVerification', 'cookieDomain'])
    assert rc == 0, f"account.php still uses Config::getParam:\n{out}"


def test_teams_membership_no_config_getparam():
    """Verify Teams Update.php does not read domainVerification or cookieDomain from Config::getParam."""
    filepath = str(REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php")
    rc, out = _check_no_config_getparam(filepath, ['domainVerification', 'cookieDomain'])
    assert rc == 0, f"Teams Update.php still uses Config::getParam:\n{out}"


def test_account_controller_injects_domain_resources():
    """Verify account.php has inject() calls for domainVerification and cookieDomain."""
    filepath = str(REPO / "app/controllers/api/account.php")
    rc, out = _check_has_inject_calls(filepath, ['domainVerification', 'cookieDomain'])
    assert rc == 0, f"account.php missing inject() calls:\n{out}"


def test_teams_membership_injects_domain_resources():
    """Verify Teams Update.php has inject() calls for domainVerification and cookieDomain."""
    filepath = str(REPO / "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php")
    rc, out = _check_has_inject_calls(filepath, ['domainVerification', 'cookieDomain'])
    assert rc == 0, f"Teams Update.php missing inject() calls:\n{out}"


# ============================================================================
# Pass-to-pass tests
# ============================================================================

def test_php_syntax_valid():
    """All modified PHP files have valid syntax."""
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
                capture_output=True, text=True, timeout=30,
            )
            assert result.returncode == 0, f"PHP syntax error in {file}: {result.stderr}"


def test_repo_composer_validate():
    """Repo's composer.json is valid (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "validate"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"composer validate failed:\n{result.stderr}"


def test_repo_php_syntax_modified_files():
    """All modified PHP files have valid syntax via php -l (pass_to_pass)."""
    files = [
        "app/init/resources.php",
        "app/controllers/general.php",
        "app/controllers/api/account.php",
        "src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php",
    ]
    for file in files:
        path = REPO / file
        result = subprocess.run(
            ["php", "-l", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"PHP syntax error in {file}:\n{result.stderr}"


def test_repo_composer_audit():
    """Repo's composer audit passes or only has pre-existing advisories (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "audit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Accept: clean audit, no packages, or only pre-existing upstream advisories
    if result.returncode == 0:
        return
    combined = result.stdout + result.stderr
    if "No packages - skipping audit" in combined:
        return
    # Pre-existing advisories in the pinned base commit are acceptable
    if "security vulnerability" in combined:
        return
    assert False, f"composer audit failed:\n{result.stderr}"


def test_repo_php_lint():
    """Repo's PHP code passes Pint linting (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c",
         "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/pint --test --config pint.json"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"PHP lint (pint) failed:\n{result.stderr[-500:]}"


def test_repo_phpstan_analyze():
    """Repo's PHP code passes PHPStan static analysis (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c",
         "composer install --ignore-platform-reqs -q 2>/dev/null && vendor/bin/phpstan analyse -c phpstan.neon --memory-limit=512M --no-progress"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"PHPStan analysis failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
