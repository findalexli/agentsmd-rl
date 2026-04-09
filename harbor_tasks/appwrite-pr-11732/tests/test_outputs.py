"""Tests for the beforeCreateGitDeployment hook implementation."""

import subprocess
import sys
import ast
import re
from pathlib import Path

REPO = Path("/workspace/appwrite")
TARGET_FILE = REPO / "src/Appwrite/Platform/Modules/VCS/Http/GitHub/Deployment.php"


def test_method_exists():
    """Verify the beforeCreateGitDeployment method exists in the Deployment class."""
    content = TARGET_FILE.read_text()
    pattern = r'protected\s+function\s+beforeCreateGitDeployment\s*\('
    match = re.search(pattern, content)
    assert match is not None, "beforeCreateGitDeployment method not found"


def test_method_signature():
    """Verify the method has the correct signature with all required parameters."""
    content = TARGET_FILE.read_text()
    pattern = r'protected\s+function\s+beforeCreateGitDeployment\s*\(\s*Document\s+\$project\s*,\s*Document\s+\$repository\s*,\s*Database\s+\$dbForPlatform\s*,\s*Authorization\s+\$authorization\s*\)\s*:\s*void'
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, "Method signature does not match expected: protected function beforeCreateGitDeployment(Document $project, Document $repository, Database $dbForPlatform, Authorization $authorization): void"


def test_method_is_called_in_createGitDeployments():
    """Verify the hook is called within the createGitDeployments method after project validation."""
    content = TARGET_FILE.read_text()

    # Find the createGitDeployments method
    method_start = content.find('protected function createGitDeployments(')
    assert method_start != -1, "createGitDeployments method not found"

    # Find the next method or end of class to bound our search
    next_method = content.find('protected function', method_start + 1)
    if next_method == -1:
        next_method = len(content)

    method_body = content[method_start:next_method]

    # Check that beforeCreateGitDeployment is called
    call_pattern = r'\$this->beforeCreateGitDeployment\s*\('
    call_match = re.search(call_pattern, method_body)
    assert call_match is not None, "beforeCreateGitDeployment is not called in createGitDeployments"

    # Verify it appears after PROJECT_NOT_FOUND check (after project validation)
    project_check = method_body.find("PROJECT_NOT_FOUND")
    hook_call = method_body.find("beforeCreateGitDeployment")
    assert project_check != -1, "PROJECT_NOT_FOUND check not found"
    assert hook_call > project_check, "beforeCreateGitDeployment should be called after project validation"


def test_method_has_no_op_implementation():
    """Verify the hook method has an empty (no-op) implementation for extensibility."""
    content = TARGET_FILE.read_text()

    # Find the beforeCreateGitDeployment method
    method_pattern = r'protected\s+function\s+beforeCreateGitDeployment\s*\([^)]*\)\s*:\s*void\s*\{([^}]*)\}'
    match = re.search(method_pattern, content, re.DOTALL)
    assert match is not None, "Could not find method implementation"

    method_body = match.group(1).strip()
    # The body should be empty or whitespace only (no-op implementation)
    assert method_body == '' or method_body.isspace(), f"Method body should be empty (no-op), found: {repr(method_body)}"


def test_hook_is_called_with_correct_arguments():
    """Verify the hook is called with the correct arguments in the correct order."""
    content = TARGET_FILE.read_text()

    # Find the method call
    call_pattern = r'\$this->beforeCreateGitDeployment\s*\(\s*\$project\s*,\s*\$repository\s*,\s*\$dbForPlatform\s*,\s*\$authorization\s*\)'
    match = re.search(call_pattern, content, re.DOTALL)
    assert match is not None, "Hook call with correct arguments not found. Expected: $this->beforeCreateGitDeployment($project, $repository, $dbForPlatform, $authorization)"


def test_php_syntax_valid():
    """Verify the PHP file has valid syntax."""
    result = subprocess.run(
        ["php", "-l", str(TARGET_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"PHP syntax check failed: {result.stderr}"


def test_no_duplicate_method_definitions():
    """Verify there's only one definition of beforeCreateGitDeployment."""
    content = TARGET_FILE.read_text()
    matches = list(re.finditer(r'protected\s+function\s+beforeCreateGitDeployment', content))
    assert len(matches) == 1, f"Expected exactly one method definition, found {len(matches)}"
