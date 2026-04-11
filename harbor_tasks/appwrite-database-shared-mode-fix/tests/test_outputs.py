"""
Test suite for appwrite-database-shared-mode-fix task.

This tests the fixes for shared-mode CI failures:
1. Remove invalid (int) cast on setTenant() that truncated MongoDB UUID sequences
2. Add array_filter on _APP_DATABASE_SHARED_TABLES to prevent empty string match
3. Add adapter-based separate pool detection for documentsdb/vectorsdb
4. Fail fast with exception when no pool available
"""

import subprocess
import sys
import os
import re

# Path to the appwrite repository
REPO = "/workspace/appwrite"

def read_file(path):
    """Read file content."""
    full_path = os.path.join(REPO, path)
    with open(full_path, 'r') as f:
        return f.read()


class TestSharedModeFixes:
    """Tests for the shared-mode database fixes."""

    def test_request_php_has_array_filter_for_shared_tables(self):
        """Test that request.php uses array_filter on _APP_DATABASE_SHARED_TABLES."""
        content = read_file('app/init/resources/request.php')

        # Should have array_filter on the shared tables explode
        assert 'array_filter(\\explode(\',\', System::getEnv(\'_APP_DATABASE_SHARED_TABLES\', \'\')))' in content, \
            "request.php should use array_filter on _APP_DATABASE_SHARED_TABLES"

    def test_request_php_removes_int_cast_from_setTenant(self):
        """Test that request.php removes the invalid (int) cast on setTenant()."""
        content = read_file('app/init/resources/request.php')

        # Should NOT have (int) cast before getSequence()
        bad_pattern = r'\(int\)\s*\$project->getSequence\(\)'
        assert not re.search(bad_pattern, content), \
            "request.php should NOT have (int) cast on setTenant() - this truncates UUIDs"

        # Should have the uncast version
        assert '->setTenant($project->getSequence())' in content, \
            "request.php should call setTenant with raw getSequence() without (int) cast"

    def test_request_php_has_separate_pool_detection(self):
        """Test that request.php has separate pool detection for documentsdb/vectorsdb."""
        content = read_file('app/init/resources/request.php')

        # Should have the separate pool detection logic
        assert '$databaseHost !== $dsn->getHost()' in content, \
            "request.php should check for separate pools (documentsdb/vectorsdb)"

        # Should have DOCUMENTSDB case with its own shared tables config
        assert "DOCUMENTSDB => \\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', '')))" in content, \
            "request.php should have separate shared tables config for DOCUMENTSDB"

        # Should have VECTORSDB case with its own shared tables config
        assert "VECTORSDB => \\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', '')))" in content, \
            "request.php should have separate shared tables config for VECTORSDB"

    def test_worker_php_has_array_filter_for_shared_tables(self):
        """Test that worker message.php uses array_filter on _APP_DATABASE_SHARED_TABLES."""
        content = read_file('app/init/worker/message.php')

        # Should have array_filter on the shared tables explode
        assert 'array_filter(\\explode(\',\', System::getEnv(\'_APP_DATABASE_SHARED_TABLES\', \'\')))' in content, \
            "worker message.php should use array_filter on _APP_DATABASE_SHARED_TABLES"

    def test_worker_php_removes_int_cast_from_setTenant(self):
        """Test that worker message.php removes the invalid (int) cast on setTenant()."""
        content = read_file('app/init/worker/message.php')

        # Should NOT have (int) cast before getSequence()
        bad_pattern = r'\(int\)\s*\$projectDocument->getSequence\(\)'
        assert not re.search(bad_pattern, content), \
            "worker message.php should NOT have (int) cast on setTenant() - this truncates UUIDs"

        # Should have the uncast version
        assert '->setTenant($projectDocument->getSequence())' in content, \
            "worker message.php should call setTenant with raw getSequence() without (int) cast"

    def test_worker_php_has_separate_pool_detection(self):
        """Test that worker message.php has separate pool detection for documentsdb/vectorsdb."""
        content = read_file('app/init/worker/message.php')

        # Should have the separate pool detection logic
        assert '$databaseHost !== $dsn->getHost()' in content, \
            "worker message.php should check for separate pools (documentsdb/vectorsdb)"

        # Should have DOCUMENTSDB case with its own shared tables config
        assert "DOCUMENTSDB => \\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', '')))" in content, \
            "worker message.php should have separate shared tables config for DOCUMENTSDB"

        # Should have VECTORSDB case with its own shared tables config
        assert "VECTORSDB => \\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', '')))" in content, \
            "worker message.php should have separate shared tables config for VECTORSDB"

    def test_create_php_has_array_filter_for_documentsdb_shared_tables(self):
        """Test that Create.php uses array_filter for documentsdb shared tables."""
        content = read_file('src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')

        # Should have array_filter on documentsdb shared tables
        assert "\\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES', '')))" in content, \
            "Create.php should use array_filter on _APP_DATABASE_DOCUMENTSDB_SHARED_TABLES"

        # Should have array_filter on documentsdb shared tables v1
        assert "\\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1', '')))" in content, \
            "Create.php should use array_filter on _APP_DATABASE_DOCUMENTSDB_SHARED_TABLES_V1"

    def test_create_php_has_array_filter_for_vectorsdb_shared_tables(self):
        """Test that Create.php uses array_filter for vectorsdb shared tables."""
        content = read_file('src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')

        # Should have array_filter on vectorsdb shared tables
        assert "\\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES', '')))" in content, \
            "Create.php should use array_filter on _APP_DATABASE_VECTORSDB_SHARED_TABLES"

        # Should have array_filter on vectorsdb shared tables v1
        assert "\\array_filter(\\explode(',', System::getEnv('_APP_DATABASE_VECTORSDB_SHARED_TABLES_V1', '')))" in content, \
            "Create.php should use array_filter on _APP_DATABASE_VECTORSDB_SHARED_TABLES_V1"

    def test_create_php_has_empty_shared_tables_check(self):
        """Test that Create.php checks for empty shared tables before filtering pools."""
        content = read_file('src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')

        # Should check for both !empty($dsn) AND !empty($databaseSharedTables)
        assert "if (!empty($dsn) && !empty($databaseSharedTables))" in content, \
            "Create.php should check both !empty($dsn) && !empty($databaseSharedTables) before filtering"

    def test_create_php_has_exception_for_empty_pools(self):
        """Test that Create.php throws exception when no database pool available."""
        content = read_file('src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')

        # Should have the exception throw for empty pools
        assert 'throw new Exception(Exception::GENERAL_SERVER_ERROR' in content, \
            "Create.php should throw exception when no database pool available"

        # Should have the specific error message
        assert 'database pool available for the current shared-tables mode' in content, \
            "Create.php should have descriptive error message about shared-tables mode"

    def test_create_php_has_explicit_empty_databases_check(self):
        """Test that Create.php explicitly checks for empty databases after filtering."""
        content = read_file('src/Appwrite/Platform/Modules/Databases/Http/Databases/Create.php')

        # Should have explicit empty check before array_rand
        assert "if (empty($databases))" in content, \
            "Create.php should have explicit empty check before array_rand"


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
