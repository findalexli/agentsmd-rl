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
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "1.9.x") !== false; echo $has ? "1" : "0";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "1.9.x should be added"


def test_updateSdkVersion_uses_callback_for_scoping():
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "function (\$blockMatch)") !== false; echo $has ? "1" : "0";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "updateSdkVersion should use block-scoped callback"


def test_empty_git_commit_handling():
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "No changes to commit") !== false; echo $has ? "1" : "0";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "Should handle empty git commit"


def test_updateExistingPr_handles_existing_pr():
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $hasUpdate = strpos($c, "updateExistingPr") !== false; $hasUrl = strpos($c, "\$existingPrUrl") !== false; echo ($hasUpdate && $hasUrl) ? "1" : "0";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "updateExistingPr should handle existing PR"


def test_cleanupTarget_not_called():
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "\$this->cleanupTarget(") !== false; echo $has ? "0" : "1";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "cleanupTarget should not be called"


def test_cleanupTarget_method_removed():
    code = '$f = "/workspace/appwrite/src/Appwrite/Platform/Tasks/SDKs.php"; $c = file_get_contents($f); $has = strpos($c, "function cleanupTarget") !== false; echo $has ? "0" : "1";'
    stdout, stderr, rc = php_exec(code)
    assert stdout.strip() == "1", "cleanupTarget method should be removed"


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
