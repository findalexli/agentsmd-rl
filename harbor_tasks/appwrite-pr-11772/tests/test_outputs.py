"""Tests for VectorsDB metadata bootstrap race condition fix.

This verifies that the Create.php file properly handles concurrent
database metadata bootstrapping without separate existence checks.
"""

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

REPO = Path("/workspace/appwrite")
TARGET_FILE = REPO / "src/Appwrite/Platform/Modules/Databases/Http/VectorsDB/Collections/Create.php"

COMPOSER_JSON = REPO / "composer.json"
PINT_JSON = REPO / "pint.json"
PHPSTAN_NEON = REPO / "phpstan.neon"
PHPUNIT_XML = REPO / "phpunit.xml"


def test_target_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_php_syntax_valid():
    """PHP file must have valid syntax."""
    result = subprocess.run(
        ["php", "-l", str(TARGET_FILE)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"PHP syntax error: {result.stderr}"


def test_bootstrap_comment_present():
    """Must include explanatory comment about race condition fix."""
    content = TARGET_FILE.read_text()
    assert "Bootstrap the database metadata without a separate existence" in content, \
        "Missing bootstrap comment explaining the race condition fix"
    assert "avoid races when multiple first collections are created" in content, \
        "Missing comment about concurrent collection creation"


def test_retry_loop_structure():
    """Must have a retry loop with 5 attempts."""
    content = TARGET_FILE.read_text()

    # Check for retry loop with 5 attempts
    loop_pattern = r'for\s*\(\s*\$attempt\s*=\s*0\s*;\s*\$attempt\s*<\s*5\s*;\s*\$attempt\+\+\s*\)'
    assert re.search(loop_pattern, content), \
        "Missing or incorrect retry loop structure (for $attempt = 0; $attempt < 5; $attempt++)"


def test_duplicate_exception_handling():
    """Must catch DuplicateException and break out of loop."""
    content = TARGET_FILE.read_text()

    # Check for DuplicateException catch with break
    dup_pattern = r'catch\s*\(\s*DuplicateException\s*\)\s*\{[^}]*break\s*;[^}]*\}'
    assert re.search(dup_pattern, content, re.DOTALL), \
        "Must catch DuplicateException and break out of the retry loop"


def test_throwable_catch_with_exists_check():
    """Must catch Throwable and check if metadata exists before retrying."""
    content = TARGET_FILE.read_text()

    # Check for Throwable catch with exists check
    catch_pattern = r'catch\s*\(\s*\\?Throwable\s+\$e\s*\)'
    assert re.search(catch_pattern, content), \
        "Must catch Throwable to handle race conditions from Swoole PDO proxy"

    # Check for exists call within the catch
    exists_pattern = r'if\s*\(\s*\$dbForDatabases->exists\s*\(\s*null\s*,\s*Database::METADATA\s*\)\s*\)'
    assert re.search(exists_pattern, content), \
        "Must check if METADATA exists after catching Throwable"


def test_max_attempts_check():
    """Must check for max attempts (4th index) before throwing."""
    content = TARGET_FILE.read_text()

    # Check for attempt limit check before rethrowing
    attempt_check = r'if\s*\(\s*\$attempt\s*===?\s*4\s*\)'
    assert re.search(attempt_check, content), \
        "Must check if attempt is at limit (4 or === 4) before throwing exception"


def test_usleep_retry_delay():
    """Must have usleep with 100ms delay between retries."""
    content = TARGET_FILE.read_text()

    # Check for usleep with 100_000 microseconds (100ms)
    usleep_pattern = r'\\?usleep\s*\(\s*100_000\s*\)'
    assert re.search(usleep_pattern, content), \
        "Must have usleep(100_000) for 100ms delay between retry attempts"


def test_no_pre_check_exists():
    """The old pattern of pre-checking exists() before create() should be removed."""
    content = TARGET_FILE.read_text()

    # The old pattern was: if (!$dbForDatabases->exists(null, Database::METADATA)) { try { $dbForDatabases->create(); } ... }
    # We should not see exists() used as a pre-condition before create()

    # Find the create() call context - it should be inside the retry loop, not preceded by an exists check
    # This is a negative test - we're checking the bad pattern is NOT present

    # Look for the bad pattern: exists check wrapping create
    bad_pattern = r'if\s*\(\s*!\s*\$dbForDatabases->exists\s*\([^)]*\)\s*\)\s*\{[^}]*\$dbForDatabases->create\s*\('
    match = re.search(bad_pattern, content, re.DOTALL)
    assert match is None, \
        "Must NOT pre-check exists() before calling create() - this is the race condition being fixed"


def test_create_called_in_loop():
    """create() must be called inside the retry loop."""
    content = TARGET_FILE.read_text()

    # Verify that $dbForDatabases->create() is inside a for loop
    # Look for create() call followed by break inside loop braces
    create_in_loop = r'for\s*\([^)]*\)\s*\{[^}]*\$dbForDatabases->create\s*\(\s*\)[^}]*break\s*;[^}]*\}'
    assert re.search(create_in_loop, content, re.DOTALL), \
        "$dbForDatabases->create() must be called inside the retry loop with a break statement"


def test_retry_logic_comprehensive():
    """Comprehensive check for all retry logic components in correct order."""
    content = TARGET_FILE.read_text()

    # Find the try block structure - it should have:
    # 1. for loop with 5 attempts
    # 2. inner try with create() and break
    # 3. catch DuplicateException with break
    # 4. catch Throwable with exists check, retry logic, and rethrow

    # Check sequence of elements in the try block
    try_block_start = content.find('try {')
    assert try_block_start != -1, "Must have a try block"

    # Get the try block content (simplified - find the matching closing brace)
    brace_count = 1
    idx = try_block_start + 5
    while brace_count > 0 and idx < len(content):
        if content[idx] == '{':
            brace_count += 1
        elif content[idx] == '}':
            brace_count -= 1
        idx += 1

    try_block = content[try_block_start:idx]

    # Check for required components in order
    assert '$attempt = 0' in try_block or '$attempt=0' in try_block, \
        "Retry loop must start with $attempt = 0"
    assert '$attempt < 5' in try_block or '$attempt<5' in try_block, \
        "Retry loop must check $attempt < 5"
    assert '$dbForDatabases->create()' in try_block, \
        "Must call $dbForDatabases->create() in the loop"

    # Check that DuplicateException comes before Throwable (order matters)
    dup_pos = try_block.find('DuplicateException')
    throwable_pos = try_block.find('Throwable')

    if dup_pos != -1 and throwable_pos != -1:
        assert dup_pos < throwable_pos, \
            "DuplicateException catch must come before Throwable catch"


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD tests (origin: repo_tests)
# These run actual CI commands via subprocess.run()
# =============================================================================


def test_composer_validate():
    """Repo's composer.json passes composer validation (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "validate", "--no-check-publish", str(COMPOSER_JSON)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"composer validate failed:\n{result.stdout}\n{result.stderr}"


def test_composer_audit():
    """Repo's dependencies pass composer security audit (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "audit", "--no-interaction"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Audit returns 0 on success, 1 on warnings, 2 on errors
    # We accept 0 and 1 (warnings are OK for p2p)
    assert result.returncode in [0, 1], f"composer audit found critical issues:\n{result.stderr}"


def test_php_syntax_check():
    """Target PHP file passes php -l syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["php", "-l", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"PHP syntax check failed:\n{result.stderr}"


# =============================================================================
# PASS-TO-PASS TESTS - Static file validation (origin: static)
# These validate file structure without running CI commands
# =============================================================================


def test_composer_json_valid():
    """Repo's composer.json is valid JSON with required structure (pass_to_pass)."""
    assert COMPOSER_JSON.exists(), "composer.json must exist"
    content = COMPOSER_JSON.read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"composer.json is not valid JSON: {e}")

    # Basic structure validation
    assert "name" in data, "composer.json must have name field"
    assert "require" in data, "composer.json must have require section"
    assert "scripts" in data, "composer.json must have scripts section"

    # Verify expected scripts exist (as defined in CI/CD)
    expected_scripts = {"test", "lint", "analyze", "check"}
    actual_scripts = set(data.get("scripts", {}).keys())
    for script in expected_scripts:
        assert script in actual_scripts, f"composer.json must have '{script}' script"


def test_pint_json_valid():
    """Repo's pint.json (linter config) is valid JSON with PSR-12 preset (pass_to_pass)."""
    assert PINT_JSON.exists(), "pint.json must exist"
    content = PINT_JSON.read_text()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        pytest.fail(f"pint.json is not valid JSON: {e}")

    # Validate pint.json structure
    assert "preset" in data, "pint.json must have preset"
    assert data["preset"] == "psr12", "pint.json preset should be psr12"


def test_phpstan_config_valid():
    """Repo's phpstan.neon config is valid YAML (pass_to_pass)."""
    assert PHPSTAN_NEON.exists(), "phpstan.neon must exist"
    content = PHPSTAN_NEON.read_text()
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        pytest.fail(f"phpstan.neon is not valid YAML: {e}")

    # Basic structure validation
    assert data is not None, "phpstan.neon must not be empty"
    assert "parameters" in data, "phpstan.neon must have parameters section"


def test_phpunit_xml_valid():
    """Repo's phpunit.xml is valid XML (pass_to_pass)."""
    assert PHPUNIT_XML.exists(), "phpunit.xml must exist"
    content = PHPUNIT_XML.read_text()
    try:
        import xml.etree.ElementTree as ET
        ET.fromstring(content)
    except ET.ParseError as e:
        pytest.fail(f"phpunit.xml is not valid XML: {e}")


def test_target_file_no_syntax_errors():
    """Target PHP file has balanced braces/parens/brackets (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check for balanced braces
    open_count = content.count('{')
    close_count = content.count('}')
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"

    # Check for balanced parentheses
    open_paren = content.count('(')
    close_paren = content.count(')')
    assert open_paren == close_paren, f"Unbalanced parentheses: {open_paren} open, {close_paren} close"

    # Check for balanced square brackets
    open_bracket = content.count('[')
    close_bracket = content.count(']')
    assert open_bracket == close_bracket, f"Unbalanced brackets: {open_bracket} open, {close_bracket} close"


def test_php_namespace_declarations_valid():
    """PHP namespace and use statements are valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check namespace declaration
    namespace_pattern = r'namespace\s+([A-Za-z_][A-Za-z0-9_]*(?:\\[A-Za-z_][A-Za-z0-9_]*)*)\s*;'
    namespace_match = re.search(namespace_pattern, content)
    assert namespace_match, "Must have valid namespace declaration"

    # Check use statements (basic validation)
    use_pattern = r'use\s+([A-Za-z_][A-Za-z0-9_]*(?:\\[A-Za-z_][A-Za-z0-9_]*)*)(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?\s*;'
    use_matches = re.findall(use_pattern, content)

    # Verify use statements have valid structure
    for match in use_matches:
        class_path = match[0] if isinstance(match, tuple) else match
        assert '::' not in class_path, f"Use statement should not contain ::: {class_path}"


def test_repo_directory_structure_valid():
    """Repo has expected directory structure for CI/CD (pass_to_pass)."""
    # Verify essential directories exist
    required_dirs = [
        REPO / "src",
        REPO / "tests",
        REPO / ".github" / "workflows",
    ]
    for dir_path in required_dirs:
        assert dir_path.exists(), f"Required directory must exist: {dir_path}"

    # Verify essential files exist
    required_files = [
        REPO / "composer.json",
        REPO / "phpunit.xml",
        REPO / "Dockerfile",
    ]
    for file_path in required_files:
        assert file_path.exists(), f"Required file must exist: {file_path}"


def test_php_class_structure_valid():
    """Target file has valid PHP class structure (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check class declaration
    class_pattern = r'class\s+([A-Za-z_][A-Za-z0-9_]*)'
    class_match = re.search(class_pattern, content)
    assert class_match, "Must have a class declaration"
    assert class_match.group(1) == "Create", "Class name should be 'Create'"

    # Check method declarations
    method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\('
    methods = re.findall(method_pattern, content)
    assert 'action' in methods, "Must have 'action' method"

    # Verify class has proper opening and closing
    assert content.count('class Create') == 1, "Should have exactly one 'class Create' declaration"


def test_no_merge_conflicts_in_file():
    """No Git merge conflict markers in target file (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    conflict_patterns = [
        '<<<<<<< HEAD',
        '=======',
        '>>>>>>>',
        '<<<<<<< ',  # Any branch marker
    ]

    for pattern in conflict_patterns:
        assert pattern not in content, f"Found merge conflict marker: {pattern}"


def test_php_opening_tag_present():
    """PHP files have proper opening tag (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check for PHP opening tag
    assert content.strip().startswith('<?php'), "Must start with <?php"

    # Check no short tags
    assert '<?=' not in content, "Should not use short echo tags in this file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
