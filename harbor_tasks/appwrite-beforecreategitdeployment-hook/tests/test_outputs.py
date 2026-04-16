#!/usr/bin/env python3
"""
Tests for appwrite PR #11732: Add beforeCreateGitDeployment hook

This PR adds a hook method that allows for extensible deployment validation logic.
The hook is called after project validation but before database operations.
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/appwrite"
TARGET_FILE = f"{REPO}/src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php"


def test_method_exists_with_correct_signature():
    """Test that beforeCreateGitDeployment method exists with correct signature."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that the method exists with correct signature
    pattern = r'protected function beforeCreateGitDeployment\(\s*Document \$project,\s*Document \$repository,\s*Database \$dbForPlatform,\s*Authorization \$authorization\s*\):\s*void\s*\{'

    if not re.search(pattern, content):
        raise AssertionError(
            "beforeCreateGitDeployment method not found with correct signature. "
            "Expected: protected function beforeCreateGitDeployment(Document $project, Document $repository, Database $dbForPlatform, Authorization $authorization): void"
        )


def test_method_is_called_in_createGitDeployments():
    """Test that beforeCreateGitDeployment is called in the right place in createGitDeployments."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the createGitDeployments method
    method_start = content.find('protected function createGitDeployments(')
    if method_start == -1:
        raise AssertionError("createGitDeployments method not found")

    # Find the end of the method (next method at same indentation level or class end)
    rest_of_class = content[method_start:]
    method_content = rest_of_class[:rest_of_class.find('\n    protected function getBuildQueueName(')]

    # Check that beforeCreateGitDeployment is called
    if '$this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization)' not in method_content:
        raise AssertionError(
            "beforeCreateGitDeployment method call not found in createGitDeployments. "
            "Expected call: $this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization)"
        )

    # Verify it's called after PROJECT_NOT_FOUND check
    project_not_found_pos = method_content.find("throw new Exception(Exception::PROJECT_NOT_FOUND")
    hook_call_pos = method_content.find('$this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization)')

    if project_not_found_pos == -1:
        raise AssertionError("PROJECT_NOT_FOUND check not found in createGitDeployments")

    if hook_call_pos == -1:
        raise AssertionError("beforeCreateGitDeployment call not found")

    if hook_call_pos < project_not_found_pos:
        raise AssertionError(
            "beforeCreateGitDeployment should be called AFTER the PROJECT_NOT_FOUND validation check, not before"
        )

    # Verify it's called BEFORE the DSN/database operations
    dsn_pos = method_content.find('$dsn = new DSN($project->getAttribute')

    if dsn_pos == -1:
        raise AssertionError("DSN initialization not found in createGitDeployments")

    if hook_call_pos > dsn_pos:
        raise AssertionError(
            "beforeCreateGitDeployment should be called BEFORE database operations (DSN creation), not after"
        )


def test_method_has_noop_implementation():
    """Test that beforeCreateGitDeployment has a no-op implementation (empty body)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the method and check its body is empty
    method_pattern = r'protected function beforeCreateGitDeployment\([^)]+\):\s*void\s*\{\s*\}'

    if not re.search(method_pattern, content):
        raise AssertionError(
            "beforeCreateGitDeployment should have an empty no-op implementation. "
            "Expected: protected function beforeCreateGitDeployment(...): void { }"
        )


def test_php_syntax_valid():
    """Test that the PHP file has valid syntax."""
    result = subprocess.run(
        ['php', '-l', TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise AssertionError(f"PHP syntax error in {TARGET_FILE}:\n{result.stderr}")


def test_method_is_protected():
    """Test that beforeCreateGitDeployment is a protected method."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Ensure it's protected, not public or private
    if 'protected function beforeCreateGitDeployment' not in content:
        if 'public function beforeCreateGitDeployment' in content:
            raise AssertionError("beforeCreateGitDeployment should be protected, not public")
        elif 'private function beforeCreateGitDeployment' in content:
            raise AssertionError("beforeCreateGitDeployment should be protected, not private")
        else:
            raise AssertionError("beforeCreateGitDeployment visibility modifier not found")


def test_composer_autoload_still_works():
    """Test that composer autoload still works after changes."""
    result = subprocess.run(
        ['composer', 'dump-autoload', '--optimize'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise AssertionError(f"Composer autoload failed:\n{result.stderr}")


def test_composer_validate():
    """Repo's composer.json is valid (pass_to_pass)."""
    result = subprocess.run(
        ['composer', 'validate'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise AssertionError(f"Composer validate failed:\n{result.stderr}")


def test_vcs_module_php_syntax():
    """All PHP files in VCS module have valid syntax (pass_to_pass)."""
    vcs_dir = f"{REPO}/src/Appwrite/Platform/Modules/VCS"

    # Find all PHP files in VCS module
    result = subprocess.run(
        ['find', vcs_dir, '-name', '*.php', '-type', 'f'],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode != 0:
        raise AssertionError(f"Failed to find PHP files:\n{result.stderr}")

    php_files = [f for f in result.stdout.strip().split('\n') if f]

    # Check syntax of each file
    for php_file in php_files:
        syntax_result = subprocess.run(
            ['php', '-l', php_file],
            capture_output=True,
            text=True,
            timeout=30
        )

        if syntax_result.returncode != 0:
            raise AssertionError(f"PHP syntax error in {php_file}:\n{syntax_result.stderr}")


def test_repo_git_config_valid():
    """Git repository configuration is valid (pass_to_pass)."""
    result = subprocess.run(
        ['git', 'fsck', '--full'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise AssertionError(f"Git fsck failed:\n{result.stderr}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
