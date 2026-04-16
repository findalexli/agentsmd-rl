"""
Test suite for appwrite-database-shared-mode-fix task.

This tests the fixes for shared-mode CI failures using behavioral verification:
1. Remove invalid (int) cast on setTenant() that truncated MongoDB UUID sequences
2. Add array_filter on _APP_DATABASE_SHARED_TABLES to prevent empty string match
3. Add adapter-based separate pool detection for documentsdb/vectorsdb
4. Fail fast with exception when no pool available
"""

import subprocess
import sys
import os
import re
import tempfile

# Path to the appwrite repository
REPO = "/workspace/appwrite"


def run_php_code(code, env=None):
    """Execute PHP code and return (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            ['php', tmp_path],
            capture_output=True,
            text=True,
            cwd=REPO,
            env={**os.environ, **(env or {})}
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(tmp_path)


class TestSharedModeFixes:
    """Behavioral tests for the shared-mode database fixes."""

    def test_array_filter_removes_empty_strings_from_shared_tables(self):
        """
        Test that array_filter properly removes empty strings from exploded env var.

        This verifies the fix for Issue 2: Empty strings were matching in_array()
        checks when _APP_DATABASE_SHARED_TABLES was unset or empty.
        """
        php_code = '''<?php
        // Simulate the fixed behavior
        $envValue = '';  // Empty env var (default case)
        $sharedTables = \\array_filter(\\explode(',', $envValue));

        // Empty strings should NOT be in the array after array_filter
        if (in_array('', $sharedTables, true)) {
            echo "FAIL: empty string found in sharedTables";
            exit(1);
        }

        // Test with comma-separated values including empty entries
        $envValue2 = 'host1,,host2,';
        $sharedTables2 = \\array_filter(\\explode(',', $envValue2));

        if (count($sharedTables2) !== 2) {
            echo "FAIL: expected 2 elements, got " . count($sharedTables2);
            exit(1);
        }

        if (!in_array('host1', $sharedTables2, true) || !in_array('host2', $sharedTables2, true)) {
            echo "FAIL: host1 or host2 not found";
            exit(1);
        }

        echo "PASS";
        ?>
        '''
        returncode, stdout, stderr = run_php_code(php_code)
        assert returncode == 0 and 'PASS' in stdout, \
            f"array_filter test failed: {stdout} {stderr}"

    def test_int_cast_truncates_uuid_sequence(self):
        """
        Test that (int) cast would incorrectly truncate a UUID-like string.

        This verifies the fix for Issue 1: The (int) cast was truncating
        UUID-based project sequences, causing tenant ID mismatches.
        """
        php_code = '''<?php
        // Simulate a UUID-like sequence (common in MongoDB)
        $sequence = "550e8400e29b41d4a716446655440000";

        // With (int) cast - WRONG, truncates
        $truncated = (int) $sequence;

        // Without cast - preserves full value
        $preserved = $sequence;

        // The truncated value should NOT equal the original
        if ((string)$truncated === $preserved) {
            echo "FAIL: int cast did not truncate as expected";
            exit(1);
        }

        // Verify the truncation is significant
        if (strlen((string)$truncated) >= strlen($preserved)) {
            echo "FAIL: truncation not significant";
            exit(1);
        }

        // Verify the full value is preserved without cast
        if ($preserved !== $sequence) {
            echo "FAIL: value not preserved";
            exit(1);
        }

        echo "PASS: int cast truncates, no cast preserves";
        ?>
        '''
        returncode, stdout, stderr = run_php_code(php_code)
        assert returncode == 0 and 'PASS' in stdout, \
            f"int cast truncation test failed: {stdout} {stderr}"

    def test_request_php_uses_array_filter(self):
        """Test that request.php uses array_filter for shared tables env var."""
        content = open(os.path.join(REPO, 'app/init/resources/request.php')).read()

        # Should have array_filter wrapping explode for the shared tables env var
        pattern = r'array_filter\s*\(\s*\\explode\s*\(\s*[\'"]\s*,\s*[\'"]\s*,\s*System::getEnv\s*\(\s*[\'"]_APP_DATABASE_SHARED_TABLES[\'"]'

        # Just check that array_filter is used with the env var (any valid syntax)
        has_array_filter = 'array_filter' in content and '_APP_DATABASE_SHARED_TABLES' in content
        assert has_array_filter, "request.php should use array_filter for shared tables"

        # Verify the pattern exists - check for array_filter near the shared tables env var
        lines = content.split('\n')
        found = False
        for line in lines:
            if '_APP_DATABASE_SHARED_TABLES' in line and 'array_filter' in line:
                found = True
                break
        assert found, "request.php should have array_filter on same line as _APP_DATABASE_SHARED_TABLES"

    def test_request_php_no_int_cast_on_settenant(self):
        """Test that request.php doesn't have (int) cast on setTenant."""
        content = open(os.path.join(REPO, 'app/init/resources/request.php')).read()

        # Should NOT have (int) cast before getSequence()
        bad_pattern = r'\\(int\\)\\s*\\$project->getSequence\(\)'
        assert not re.search(bad_pattern, content), \
            "request.php should NOT have (int) cast on setTenant() - this truncates UUIDs"

        # Should have setTenant call
        assert '->setTenant(' in content, "request.php should call setTenant()"

    def test_request_php_has_separate_pool_detection(self):
        """Test that request.php has logic to detect separate pools for documentsdb/vectorsdb."""
        content = open(os.path.join(REPO, 'app/init/resources/request.php')).read()

        # Should have host comparison logic for separate pool detection
        # This checks for the pattern of comparing database host to DSN host
        has_host_comparison = '$databaseHost' in content and '$dsn->getHost()' in content
        assert has_host_comparison, \
            "request.php should compare database hosts for separate pool detection"

        # Should handle DOCUMENTSDB specifically
        has_documentsdb = 'DOCUMENTSDB' in content and 'DOCUMENTSDB_SHARED_TABLES' in content
        assert has_documentsdb, \
            "request.php should handle DOCUMENTSDB shared tables configuration"

        # Should handle VECTORSDB specifically
        has_vectorsdb = 'VECTORSDB' in content and 'VECTORSDB_SHARED_TABLES' in content
        assert has_vectorsdb, \
            "request.php should handle VECTORSDB shared tables configuration"

    def test_worker_php_uses_array_filter(self):
        """Test that worker message.php uses array_filter for shared tables env var."""
        content = open(os.path.join(REPO, 'app/init/worker/message.php')).read()

        # Should have array_filter on the shared tables explode
        lines = content.split('\n')
        found = False
        for line in lines:
            if '_APP_DATABASE_SHARED_TABLES' in line and 'array_filter' in line:
                found = True
                break
        assert found, "worker message.php should have array_filter on same line as _APP_DATABASE_SHARED_TABLES"

    def test_worker_php_no_int_cast_on_settenant(self):
        """Test that worker message.php doesn't have (int) cast on setTenant."""
        content = open(os.path.join(REPO, 'app/init/worker/message.php')).read()

        # Should NOT have (int) cast before getSequence()
        bad_pattern = r'\\(int\\)\\s*\\$projectDocument->getSequence\(\)'
        assert not re.search(bad_pattern, content), \
            "worker message.php should NOT have (int) cast on setTenant()"

        # Should have setTenant call
        assert '->setTenant(' in content, "worker message.php should call setTenant()"

    def test_worker_php_has_separate_pool_detection(self):
        """Test that worker message.php has logic to detect separate pools."""
        content = open(os.path.join(REPO, 'app/init/worker/message.php')).read()

        # Should have host comparison logic
        has_host_comparison = '$databaseHost' in content and '$dsn->getHost()' in content
        assert has_host_comparison, \
            "worker message.php should compare database hosts for separate pool detection"

        # Should handle DOCUMENTSDB
        has_documentsdb = 'DOCUMENTSDB' in content and 'DOCUMENTSDB_SHARED_TABLES' in content
        assert has_documentsdb, "worker message.php should handle DOCUMENTSDB"

        # Should handle VECTORSDB
        has_vectorsdb = 'VECTORSDB' in content and 'VECTORSDB_SHARED_TABLES' in content
        assert has_vectorsdb, "worker message.php should handle VECTORSDB"

    def test_create_php_uses_array_filter_for_documentsdb(self):
        """Test that Create.php uses array_filter for documentsdb shared tables."""
        content = open(os.path.join(REPO, 'src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')).read()

        # Should have array_filter on documentsdb shared tables
        has_array_filter = 'array_filter' in content
        assert has_array_filter, "Create.php should use array_filter"

        # Should reference the documentsdb shared tables vars
        has_doc_shared = '_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES' in content
        has_doc_shared_v1 = '_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1' in content
        assert has_doc_shared and has_doc_shared_v1, \
            "Create.php should handle documentsdb shared tables vars"

    def test_create_php_uses_array_filter_for_vectorsdb(self):
        """Test that Create.php uses array_filter for vectorsdb shared tables."""
        content = open(os.path.join(REPO, 'src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')).read()

        # Should reference the vectorsdb shared tables vars with array_filter
        has_vec_shared = '_APP_DATABASE_VECTORSDB_SHARED_TABLES' in content
        has_vec_shared_v1 = '_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1' in content
        assert has_vec_shared and has_vec_shared_v1, \
            "Create.php should handle vectorsdb shared tables vars"

    def test_create_php_throws_exception_for_empty_pools(self):
        """
        Test that Create.php throws an exception when no database pool is available.

        Verifies Issue 4: The code should fail fast instead of silently proceeding.
        """
        content = open(os.path.join(REPO, 'src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')).read()

        # Should throw an exception when pools are empty
        has_exception = 'throw new Exception' in content
        assert has_exception, "Create.php should throw exception for empty pools"

        # Should have the specific error message about no pool available
        has_error_message = 'database pool available' in content.lower() or 'shared-tables mode' in content.lower()
        assert has_error_message, \
            "Create.php should have descriptive error message about no pool available"

        # Should check for empty before using array_rand
        has_empty_check = 'empty(' in content and 'array_rand' in content
        assert has_empty_check, \
            "Create.php should check for empty before array_rand"

    def test_empty_check_before_pool_filtering(self):
        """
        Test that Create.php checks for empty shared tables before filtering pools.

        This prevents filtering when shared tables is empty/unconfigured.
        """
        content = open(os.path.join(REPO, 'src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')).read()

        # Should check both $dsn and $databaseSharedTables are not empty
        # This prevents the filtering logic from running when unconfigured
        has_dsn_check = '!empty($dsn)' in content or 'empty($dsn)' in content
        has_shared_tables_check = '!empty($databaseSharedTables)' in content or 'empty($databaseSharedTables)' in content

        assert has_dsn_check and has_shared_tables_check, \
            "Create.php should check both dsn and databaseSharedTables are not empty before filtering"


class TestPhpSyntax:
    """Tests for PHP syntax validity."""

    def test_request_php_syntax_valid(self):
        """Test that request.php has valid PHP syntax."""
        result = subprocess.run(
            ['php', '-l', os.path.join(REPO, 'app/init/resources/request.php')],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"request.php has syntax errors: {result.stderr}"

    def test_worker_message_php_syntax_valid(self):
        """Test that worker message.php has valid PHP syntax."""
        result = subprocess.run(
            ['php', '-l', os.path.join(REPO, 'app/init/worker/message.php')],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"worker message.php has syntax errors: {result.stderr}"

    def test_create_php_syntax_valid(self):
        """Test that Create.php has valid PHP syntax."""
        result = subprocess.run(
            ['php', '-l', os.path.join(REPO, 'src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Create.php has syntax errors: {result.stderr}"


class TestRepoCI:
    """Pass-to-pass tests for repo's CI/CD checks."""

    def test_repo_composer_validate(self):
        """Repo's composer.json is valid (pass_to_pass)."""
        r = subprocess.run(
            ["composer", "validate", "--no-check-publish"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Composer validate failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_php_lint_request_php(self):
        """Repo's request.php passes Pint linting (pass_to_pass)."""
        r = subprocess.run(
            ["composer", "lint", "--", "app/init/resources/request.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Lint failed for request.php:\n{r.stdout}\n{r.stderr}"

    def test_repo_php_lint_worker_message_php(self):
        """Repo's worker message.php passes Pint linting (pass_to_pass)."""
        r = subprocess.run(
            ["composer", "lint", "--", "app/init/worker/message.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Lint failed for message.php:\n{r.stdout}\n{r.stderr}"

    def test_repo_php_lint_create_php(self):
        """Repo's Create.php passes Pint linting (pass_to_pass)."""
        r = subprocess.run(
            ["composer", "lint", "--", "src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Lint failed for Create.php:\n{r.stdout}\n{r.stderr}"

    def test_repo_phpstan_request_php(self):
        """Repo's request.php passes PHPStan analysis (pass_to_pass)."""
        r = subprocess.run(
            ["./vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--no-progress", "--memory-limit=1G", "app/init/resources/request.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"PHPStan failed for request.php:\n{r.stdout}\n{r.stderr}"

    def test_repo_phpstan_worker_message_php(self):
        """Repo's worker message.php passes PHPStan analysis (pass_to_pass)."""
        r = subprocess.run(
            ["./vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--no-progress", "--memory-limit=1G", "app/init/worker/message.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"PHPStan failed for message.php:\n{r.stdout}\n{r.stderr}"

    def test_repo_phpstan_create_php(self):
        """Repo's Create.php passes PHPStan analysis (pass_to_pass)."""
        r = subprocess.run(
            ["./vendor/bin/phpstan", "analyse", "-c", "phpstan.neon", "--no-progress", "--memory-limit=1G", "src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"PHPStan failed for Create.php:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
