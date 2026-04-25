#!/usr/bin/env python3
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
    """Behavioral: 1.9.x should be a valid supported version."""
    code = '''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
if (preg_match_all("/'(\\d+\\.\\d+\\.x)'/", $c, $m)) {
    $versions = $m[1];
    echo in_array("1.9.x", $versions) ? "1" : "0";
} else {
    echo "0";
}
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"1.9.x should be in supported versions (got: {stdout.strip()})"


def test_updateSdkVersion_uses_block_scoping():
    """Behavioral: updateSdkVersion should use nested callback structure for block-scoped pattern matching."""
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
$hasOuterCallback = preg_match('/preg_replace_callback\s*\([^,]+,\s*function\s*\([^)]*\)\s*use\s*\(/s', $c) > 0;
$hasInnerConditional = preg_match('/function\s*\([^)]*\)\s*use\s*\([^)]+\)\s*\{[^}]*(if|switch)[^}]*\}/s', $c) > 0;
echo ($hasOuterCallback && $hasInnerConditional) ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"updateSdkVersion should use nested callback (got: {stdout.strip()})"


def test_empty_git_commit_handling():
    """Behavioral: empty git commit should be handled gracefully with catch Throwable around commit."""
    # Check that catch Throwable exists AND commit is attempted
    # Note: \\\\Throwable in PHP single-quoted string = two backslashes = matches literal backslash in code
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
$hasCatch = preg_match('/catch\s*\(\s*\\\\Throwable/', $c) > 0;
$hasCommitAttempt = strpos($c, 'commit($commitMessage)') !== false || strpos($c, '->commit(') !== false;
echo ($hasCatch && $hasCommitAttempt) ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"Empty git commit should use try-catch Throwable (got: {stdout.strip()})"


def test_updateExistingPr_accepts_url_param():
    """Behavioral: updateExistingPr should accept an existingPrUrl parameter and use regex extraction."""
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
// Check that updateExistingPr function has URL parameter
$hasParam = preg_match('/function\s+updateExistingPr\s*\([^)]+(?:existingPrUrl|prUrl|prevPr)[^)]*\)/i', $c) > 0;
// Check that preg_match with pull exists (anywhere in file - we just need the function to exist)
$hasExtraction = preg_match('/preg_match.*pull/s', $c) > 0;
echo ($hasParam && $hasExtraction) ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"updateExistingPr should accept URL param (got: {stdout.strip()})"


def test_updateExistingPr_extracts_pr_from_error():
    """Behavioral: updateExistingPr should extract PR number from URL using regex."""
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
// Check for regex pattern with pull and digits (extracting PR number from URL)
$hasPrExtract = preg_match('/preg_match.*pull.*\d/s', $c) > 0;
echo $hasPrExtract ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"PR extraction from URL should use regex (got: {stdout.strip()})"


def test_cleanupTarget_not_called():
    """Behavioral: cleanupTarget should not be invoked."""
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "cleanupTarget(") !== false; echo $has ? "0" : "1";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "cleanupTarget should not be called"


def test_cleanupTarget_method_removed():
    """Behavioral: cleanupTarget method definition should be removed."""
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "function cleanupTarget") !== false; echo $has ? "0" : "1";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "cleanupTarget method should be removed"


def test_console_output_formatting_improved():
    """Behavioral: Console output should use variable interpolation."""
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
// Check for {$variable} style interpolation in Console calls
$interpolated = preg_match_all('/Console::(log|info|warning|success|error)\([^)]*\{\\$/', $c);
echo $interpolated > 0 ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"Console output should use variable interpolation (got: {stdout.strip()})"


def test_block_scoped_version_update_logic():
    """Behavioral: Version update should scope to platform block using nested pattern."""
    code = r'''
$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php";
$c = file_get_contents($f);
// Check for nested pattern: function() use() { ... if/switch ... }
$hasNested = preg_match('/function\s*\([^)]*\)\s*use\s*\([^)]+\)\s*\{[^}]{20,}\}(?:\s|\S)*?\}/s', $c) > 0;
echo $hasNested ? "1" : "0";
'''
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", f"Block-scoped version update should use nested pattern (got: {stdout.strip()})"


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
