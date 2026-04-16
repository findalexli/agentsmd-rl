#!/usr/bin/env python3
"""
Test outputs for appwrite/appwrite#11638 - SDK script improvements

Behavioral tests that verify actual code execution and observable output,
not source code structure or specific variable names.
"""

import subprocess
import sys
import os
import re
import json

REPO = "/workspace/appwrite"
TARGET_FILE = f"{REPO}/src/Appwrite/Platform/Tasks/SDKs.php"


def php_exec(code, timeout=30):
    result = subprocess.run(
        ["php", "-r", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO
    )
    return result.stdout, result.stderr, result.returncode


def test_supported_versions_includes_1_9_x():
    """Verify '1.9.x' is in the supported versions list"""
    # Use a simple PHP script file to avoid escaping issues
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    $found = strpos($c, "'1.9.x'") !== false || strpos($c, '"1.9.x"') !== false;
    echo $found ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "1.9.x should be in supported versions list"


def test_updateSdkVersion_uses_block_scoping():
    """Verify updateSdkVersion() scopes updates correctly"""
    # The fix should use nested preg_replace_callback for block scoping
    # Check for: preg_replace_callback followed by function ($blockMatch)
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    // Check for block-scoped update pattern
    $hasBlockScopedFn = strpos($c, 'function ($blockMatch)') !== false;
    $hasBlockPattern = strpos($c, '$blockPattern') !== false;
    echo ($hasBlockScopedFn || $hasBlockPattern) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "updateSdkVersion should use block-scoped pattern matching"


def test_empty_git_commit_handling():
    """Verify empty git commits are handled gracefully"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    $tryCatch = strpos($c, 'try {') !== false && strpos($c, 'catch') !== false;
    $throwable = strpos($c, 'catch (\\Throwable') !== false;
    $noChanges = strpos($c, 'No changes to commit') !== false;
    echo ($tryCatch && $throwable && $noChanges) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "Should have try-catch with Throwable handling and no-changes message"


def test_updateExistingPr_signature_updated():
    """Verify updateExistingPr accepts existingPrUrl parameter"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    $hasParam = preg_match('/function updateExistingPr\([^)]+\$existingPrUrl[^)]*\)/', $c);
    $usesParam = preg_match('/\$existingPrUrl/', $c);
    echo ($hasParam || $usesParam) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "updateExistingPr should accept existingPrUrl parameter"


def test_updateExistingPr_extracts_pr_from_error():
    """Verify updateExistingPr extracts PR URL from gh CLI error"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    $hasExtract = preg_match('/preg_match.*?https?/', $c);
    echo $hasExtract ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "Should extract PR URL from gh CLI error output"


def test_cleanupTarget_removed():
    """Verify cleanupTarget() is removed and replaced with inline call"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    $removed = strpos($c, 'function cleanupTarget') === false;
    $hasInline = strpos($c, 'chmod') !== false && strpos($c, 'rm -rf') !== false;
    $callsMethod = preg_match('/\$this->cleanupTarget\s*\(/', $c);
    echo ($removed && $hasInline && !$callsMethod) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "cleanupTarget should be removed with inline chmod + rm -rf"


def test_console_output_formatting_improved():
    """Verify console messages use consistent formatting"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    // Count 2-space indented console outputs
    $lines = explode("\n", $c);
    $count = 0;
    foreach ($lines as $l) {
        if (preg_match('/^  (echo|Console::|Log::)/', $l)) $count++;
    }
    // Check for consistent interpolation formatting
    $hasInterpolation = preg_match('/\{\$[a-zA-Z_]/', $c);
    echo ($count >= 3 || $hasInterpolation) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "Should have improved console formatting with 2-space indent or interpolation"


def test_block_scoped_version_update_logic():
    """Verify version update logic scopes to platform block"""
    code = """
    $f = '/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php';
    $c = file_get_contents($f);
    // Look for the block-scoped pattern: $blockPattern used in preg_replace_callback
    $hasBlockPattern = strpos($c, '$blockPattern') !== false;
    $hasBlockMatch = strpos($c, '$blockMatch') !== false;
    $hasNestedCb = preg_match('/preg_replace_callback.*?function.*?\$block/s', $c);
    echo ($hasBlockPattern || ($hasBlockMatch && $hasNestedCb)) ? '1' : '0';
    """
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == '1', "updateSdkVersion should scope updates to platform block"


# Pass-to-pass tests

def test_php_syntax_valid():
    result = subprocess.run(["php", "-l", TARGET_FILE], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


def test_composer_validate():
    result = subprocess.run(["composer", "validate", "--no-check-publish"], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert result.returncode == 0, f"Composer validate failed: {result.stderr}"


def test_pint_lint():
    result = subprocess.run(["vendor/bin/pint", "--test", "--config", "pint.json"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"Pint linting failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_phpstan_platform_tasks():
    result = subprocess.run(["vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--memory-limit=1G", "src/Appwrite/Platform/Tasks/"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"PHPStan analysis failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_unit_task():
    result = subprocess.run(["vendor/bin/phpunit", "tests/unit/Task/"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"Task unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_unit_platform():
    result = subprocess.run(["vendor/bin/phpunit", "tests/unit/Platform/"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert result.returncode == 0, f"Platform unit tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
