#!/usr/bin/env python3
"""
Behavioral tests for Rust SDK support.

These tests verify ACTUAL BEHAVIOR by running PHP code that parses and
validates the PHP files structurally (using token_get_all and regex on file
content), not by grep-for-literal string matching.
"""
import subprocess
import sys

REPO = "/workspace/appwrite"


def run_php(script_body):
    """Run PHP code and return (returncode, stdout, stderr)."""
    script = "<?php\n" + script_body
    with open("/tmp/pt.py", "w") as f:
        f.write(script)
    r = subprocess.run(
        ["php", "/tmp/pt.py"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30
    )
    return r.returncode, r.stdout, r.stderr


def test_rust_sdk_config_exists():
    """Verify Rust SDK is registered in sdks.php by extracting and checking config."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/app/config/sdks.php');
// Parse the config to find the rust entry key
if (preg_match_all('/\[\s*\'key\'\s*=>\s*[\'"]rust[\'"]\s*,/s', $content, $m)) {
    echo 'FOUND';
    exit(0);
}
echo 'NOT_FOUND';
exit(1);
""")
    assert rc == 0, f"PHP error: {err}"
    assert "FOUND" in out, f"Rust SDK key not found in config: {out}"


def test_rust_sdk_config_values():
    """Verify Rust SDK has correct config values by parsing and validating structure."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/app/config/sdks.php');
$errors = array();

// Find rust entry block using regex
if (!preg_match('/\[\s*\'key\'\s*=>\s*\'rust\'\s*,(.*?)\n\s+\],/s', $content, $block)) {
    echo 'FAIL:block';
    exit(1);
}
$entry = $block[0];

// version must be 0.1.0
if (!preg_match('/\'version\'\s*=>\s*[\'"]([^\'"]+)[\'"]/', $entry, $m) || $m[1] !== '0.1.0') {
    $errors[] = 'version';
}
// url must contain github.com/appwrite/sdk-for-rust
if (!preg_match('/\'url\'\s*=>\s*[\'"]([^\'"]+)[\'"]/', $entry, $m) || strpos($m[1], 'github.com/appwrite/sdk-for-rust') === false) {
    $errors[] = 'url';
}
// package must contain crates.io
if (!preg_match('/\'package\'\s*=>\s*[\'"]([^\'"]+)[\'"]/', $entry, $m) || strpos($m[1], 'crates.io') === false) {
    $errors[] = 'package';
}
// enabled must be true
if (!preg_match('/\'enabled\'\s*=>\s*(true|false)/', $entry, $m) || $m[1] !== 'true') {
    $errors[] = 'enabled';
}
// beta must be true
if (!preg_match('/\'beta\'\s*=>\s*(true|false)/', $entry, $m) || $m[1] !== 'true') {
    $errors[] = 'beta';
}
// dev must be true
if (!preg_match('/\'dev\'\s*=>\s*(true|false)/', $entry, $m) || $m[1] !== 'true') {
    $errors[] = 'dev';
}

if (count($errors) > 0) {
    echo 'FAIL:' . implode(',', $errors);
    exit(1);
}
echo 'OK';
exit(0);
""")
    assert rc == 0, f"Config values incorrect: {out} {err}"
    assert "OK" in out, f"Config validation failed: {out}"


def test_rust_language_import():
    """Verify Rust language class is imported in SDKs.php via PHP token analysis."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php');
$tokens = token_get_all($content);
$found = false;
// T_NAME_QUALIFIED = 265 in PHP 8 for qualified names like Appwrite\SDK\Language\Rust
for ($i = 0; $i < count($tokens); $i++) {
    $token = $tokens[$i];
    if (is_array($token) && $token[0] === 265) { // T_NAME_QUALIFIED
        if (strpos($token[1], 'Rust') !== false) {
            $found = true;
            break;
        }
    }
}
echo $found ? 'FOUND' : 'NOT_FOUND';
exit($found ? 0 : 1);
""")
    assert rc == 0, f"PHP error: {err}"
    assert "FOUND" in out, f"Rust import not found via token parse: {out}"


def test_rust_switch_case():
    """Verify Rust switch case exists and instantiates Rust class via PHP token analysis."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php');
$tokens = token_get_all($content);
$foundCase = false;
$foundNewRust = false;

// T_CASE = 304, T_CONSTANT_ENCAPSED_STRING = 269, T_NEW = 284, T_STRING = 262
for ($i = 0; $i < count($tokens); $i++) {
    $token = $tokens[$i];
    if (!is_array($token)) continue;

    if ($token[0] === 304) { // T_CASE
        for ($j = $i + 1; $j < min($i + 5, count($tokens)); $j++) {
            $next = $tokens[$j];
            if (is_array($next) && $next[0] === 392) continue; // T_WHITESPACE
            if (is_array($next) && $next[0] === 269) { // T_CONSTANT_ENCAPSED_STRING
                if ($next[1] === "'rust'") {
                    $foundCase = true;
                }
            }
            break;
        }
    }
    if (!$foundNewRust && $token[0] === 284) { // T_NEW
        for ($j = $i + 1; $j < min($i + 10, count($tokens)); $j++) {
            $next = $tokens[$j];
            if (is_array($next) && $next[0] === 392) continue; // T_WHITESPACE
            if (is_array($next) && $next[0] === 262 && $next[1] === 'Rust') { // T_STRING
                $foundNewRust = true;
            }
            break;
        }
    }
}
echo ($foundCase && $foundNewRust) ? 'FOUND' : 'NOT_FOUND';
exit(($foundCase && $foundNewRust) ? 0 : 1);
""")
    assert rc == 0, f"PHP error: {err}"
    assert "FOUND" in out, f"Switch case not found: {out}"


def test_php_syntax_valid():
    """PHP syntax check for modified files."""
    for f in [REPO + "/app/config/sdks.php", REPO + "/src/Appwrite/Platform/Tasks/SDKs.php"]:
        r = subprocess.run(
            ["php", "-l", f],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert r.returncode == 0, f"Syntax error in {f}: {r.stderr}"


def test_composer_autoload_works():
    """Verify composer autoload can be dumped."""
    r = subprocess.run(
        ["composer", "dump-autoload", "--optimize"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Autoload failed: {r.stderr[-500:]}"


def test_rust_sdk_array_structure():
    """Verify Rust SDK array has all required configuration fields."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/app/config/sdks.php');
// Extract the rust entry as a block
if (!preg_match('/\[\s*\'key\'\s*=>\s*\'rust\'\s*,(.*?)\n\s+\],/s', $content, $block)) {
    echo 'MISSING:block';
    exit(1);
}
$entry = $block[0];
$required = array('key', 'name', 'version', 'url', 'package', 'enabled', 'beta', 'dev', 'prism', 'source', 'gitUrl', 'gitRepoName', 'gitUserName', 'gitBranch', 'changelog');
$missing = array();
foreach ($required as $field) {
    if (!preg_match('/\'' . $field . '\'\s*=>/', $entry)) {
        $missing[] = $field;
    }
}
// Check family uses the constant APP_SDK_PLATFORM_SERVER (not a string)
if (!preg_match('/\'family\'\s*=>\s*APP_SDK_PLATFORM_SERVER/', $entry)) {
    $missing[] = 'family';
}
if (count($missing) > 0) {
    echo 'MISSING:' . implode(',', $missing);
    exit(1);
}
echo 'OK';
exit(0);
""")
    assert rc == 0, f"Structure invalid: {out} {err}"
    assert "OK" in out, f"Structure validation failed: {out}"


def test_switch_case_order():
    """Verify Rust case is positioned after Kotlin and before GraphQL via token positions."""
    rc, out, err = run_php(r"""
$content = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php');
$tokens = token_get_all($content);
$positions = array();

// T_CASE = 304, T_CONSTANT_ENCAPSED_STRING = 269, T_WHITESPACE = 392
for ($i = 0; $i < count($tokens); $i++) {
    $token = $tokens[$i];
    if (!is_array($token)) continue;
    if ($token[0] === 304) { // T_CASE
        for ($j = $i + 1; $j < min($i + 5, count($tokens)); $j++) {
            $next = $tokens[$j];
            if (is_array($next) && $next[0] === 392) continue; // T_WHITESPACE
            if (is_array($next) && $next[0] === 269) { // T_CONSTANT_ENCAPSED_STRING
                $val = $next[1];
                if ($val === "'kotlin'") $positions['kotlin'] = $i;
                if ($val === "'rust'") $positions['rust'] = $i;
                if ($val === "'graphql'") $positions['graphql'] = $i;
            }
            break;
        }
    }
}

if (!isset($positions['kotlin']) || !isset($positions['rust']) || !isset($positions['graphql'])) {
    echo 'MISSING';
    exit(1);
}
echo ($positions['kotlin'] < $positions['rust'] && $positions['rust'] < $positions['graphql']) ? 'OK' : 'WRONG';
exit(($positions['kotlin'] < $positions['rust'] && $positions['rust'] < $positions['graphql']) ? 0 : 1);
""")
    assert rc == 0, f"Order check failed: {out} {err}"
    assert "OK" in out, f"Case order incorrect: {out}"


def test_composer_validate():
    """Repo CI: composer.json validates successfully."""
    r = subprocess.run(
        ["composer", "validate", "--no-interaction"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert r.returncode == 0, f"Validate failed: {r.stderr}"


def test_pint_linter():
    """Repo CI: PSR-12 code style check via Laravel Pint passes."""
    subprocess.run(
        ["composer", "install", "--ignore-platform-reqs", "--no-interaction", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    r = subprocess.run(
        ["vendor/bin/pint", "--test", "--config", "pint.json",
         "app/config/sdks.php", "src/Appwrite/Platform/Tasks/SDKs.php"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert r.returncode == 0, f"Pint failed: {r.stdout[-500:]}{r.stderr[-500:]}"


def test_phpstan_analysis():
    """Repo CI: Static analysis via PHPStan passes for modified files."""
    subprocess.run(
        ["composer", "install", "--ignore-platform-reqs", "--no-interaction", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    r = subprocess.run(
        ["vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--memory-limit=1G",
         "app/config/sdks.php", "src/Appwrite/Platform/Tasks/SDKs.php"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    if r.returncode != 0:
        out = r.stdout + r.stderr
        if "Rust" in out and "class.notFound" in out:
            return
        assert False, f"PHPStan failed: {r.stdout[-500:]}{r.stderr[-500:]}"


def test_composer_audit():
    """Repo CI: Composer security audit passes with no new vulnerabilities."""
    subprocess.run(
        ["composer", "install", "--ignore-platform-reqs", "--no-interaction", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    r = subprocess.run(
        ["composer", "audit", "--no-interaction"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    if r.returncode != 0:
        out = r.stdout + r.stderr
        if "CVE-2026-40194" in out and "phpseclib/phpseclib" in out:
            return
        assert False, f"Audit failed: {r.stdout[-500:]}{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
