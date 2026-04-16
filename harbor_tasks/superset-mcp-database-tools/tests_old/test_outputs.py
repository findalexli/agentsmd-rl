"""Test the MCP database tools PR fixes."""

import ast
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/superset")


class TestDatabaseFilterCreatedBy:
    """Test that DatabaseFilter includes created_by_fk and changed_by_fk."""

    def test_database_filter_includes_created_by_fk(self):
        """DatabaseFilter.col should accept 'created_by_fk' as valid value."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        # Check that created_by_fk is in the Union type for col field
        assert '"created_by_fk"' in content, \
            "DatabaseFilter.col should include 'created_by_fk'"

    def test_database_filter_includes_changed_by_fk(self):
        """DatabaseFilter.col should accept 'changed_by_fk' as valid value."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        assert '"changed_by_fk"' in content, \
            "DatabaseFilter.col should include 'changed_by_fk'"

    def test_database_filter_description_updated(self):
        """DatabaseFilter description should mention created_by_fk usage."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        # Check that the description mentions created_by_fk for user filtering
        assert "created_by_fk with the user" in content, \
            "DatabaseFilter description should document created_by_fk usage"


class TestListDatabasesRequestValidators:
    """Test that ListDatabasesRequest has field validators for JSON parsing."""

    def test_parse_filters_validator_exists(self):
        """ListDatabasesRequest should have parse_filters field_validator."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        # Check for parse_filters validator
        assert "def parse_filters" in content, \
            "ListDatabasesRequest should have parse_filters validator"
        assert '@field_validator("filters"' in content, \
            "parse_filters should use @field_validator('filters')"

    def test_parse_columns_validator_exists(self):
        """ListDatabasesRequest should have parse_columns field_validator."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        assert "def parse_columns" in content, \
            "ListDatabasesRequest should have parse_columns validator"
        assert '@field_validator("select_columns"' in content, \
            "parse_columns should use @field_validator('select_columns')"

    def test_field_validator_imported(self):
        """field_validator should be imported from pydantic."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        assert "field_validator," in content, \
            "field_validator should be imported from pydantic"

    def test_schema_utils_imported(self):
        """parse_json_or_list and parse_json_or_model_list should be imported."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        assert "parse_json_or_list" in content, \
            "parse_json_or_list should be imported from schema_utils"
        assert "parse_json_or_model_list" in content, \
            "parse_json_or_model_list should be imported from schema_utils"


class TestDuplicateDefaultColumnsRemoved:
    """Test that duplicate DEFAULT_DATABASE_COLUMNS is removed and import is used."""

    def test_no_local_default_database_columns_definition(self):
        """list_databases.py should not define DEFAULT_DATABASE_COLUMNS locally."""
        list_db_path = REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
        content = list_db_path.read_text()

        # Should not have the local definition
        assert "DEFAULT_DATABASE_COLUMNS = [" not in content, \
            "list_databases.py should not define DEFAULT_DATABASE_COLUMNS locally"

    def test_imports_database_default_columns(self):
        """list_databases.py should import DATABASE_DEFAULT_COLUMNS from schema_discovery."""
        list_db_path = REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
        content = list_db_path.read_text()

        assert "DATABASE_DEFAULT_COLUMNS," in content, \
            "list_databases.py should import DATABASE_DEFAULT_COLUMNS from schema_discovery"

    def test_uses_imported_database_default_columns(self):
        """list_databases.py should use the imported DATABASE_DEFAULT_COLUMNS."""
        list_db_path = REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
        content = list_db_path.read_text()

        # Check that default_columns parameter uses the imported constant
        assert "default_columns=DATABASE_DEFAULT_COLUMNS" in content, \
            "list_databases.py should use imported DATABASE_DEFAULT_COLUMNS"


class TestTimezoneHandling:
    """Test that DatabaseError.create and _humanize_timestamp handle timezones correctly."""

    def test_database_error_uses_timezone_utc(self):
        """DatabaseError.create should use datetime.now(timezone.utc)."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        # Check for timezone.utc import and usage
        assert "from datetime import datetime, timezone" in content, \
            "DatabaseError.create should import timezone from datetime"
        assert "datetime.now(timezone.utc)" in content, \
            "DatabaseError.create should use datetime.now(timezone.utc)"

    def test_humanize_timestamp_uses_tzinfo(self):
        """_humanize_timestamp should handle timezone-aware datetimes."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"
        content = schemas_path.read_text()

        # Check for the improved timezone handling
        assert "dt.tzinfo" in content, \
            "_humanize_timestamp should check dt.tzinfo for timezone-aware handling"


class TestAppInstructionsUpdated:
    """Test that app.py instructions are updated for database filtering."""

    def test_app_mentions_databases_in_find_own(self):
        """app.py instructions should mention databases alongside charts/dashboards."""
        app_path = REPO / "superset" / "mcp_service" / "app.py"
        content = app_path.read_text()

        # Should mention databases in the find your own section
        assert "charts/dashboards/databases" in content, \
            "app.py should mention databases in find your own section"

    def test_app_has_database_filter_example(self):
        """app.py should have example for list_databases with created_by_fk filter."""
        app_path = REPO / "superset" / "mcp_service" / "app.py"
        content = app_path.read_text()

        assert "list_databases(filters=[{{\"col\": \"created_by_fk\"" in content, \
            "app.py should have list_databases filter example with created_by_fk"

    def test_app_has_my_databases_section(self):
        """app.py should have 'My databases' section in examples."""
        app_path = REPO / "superset" / "mcp_service" / "app.py"
        content = app_path.read_text()

        assert "My databases:" in content, \
            "app.py should have 'My databases:' section in examples"


class TestTypeAnnotations:
    """Test that create_mock_database has proper type annotations."""

    def test_create_mock_database_has_type_hints(self):
        """create_mock_database should have Python 3.10+ type annotations."""
        test_path = REPO / "tests" / "unit_tests" / "mcp_service" / "database" / "tool" / "test_database_tools.py"
        content = test_path.read_text()

        # Check for type annotations on parameters
        assert "database_id: int = 1" in content, \
            "create_mock_database should have database_id: int type annotation"
        assert "database_name: str = \"examples\"" in content, \
            "create_mock_database should have database_name: str type annotation"
        assert "-> MagicMock" in content, \
            "create_mock_database should have -> MagicMock return type"


class TestMcpCoreDocstring:
    """Test that mcp_core.py docstring is updated to include database."""

    def test_model_type_docstring_includes_database(self):
        """ModelGetSchemaCore docstring should include database in model_type description."""
        mcp_core_path = REPO / "superset" / "mcp_service" / "mcp_core.py"
        content = mcp_core_path.read_text()

        # Check that the docstring mentions database
        assert "(chart, dataset, dashboard, database)" in content, \
            "mcp_core.py docstring should include 'database' in model_type description"


class TestRepoPassToPass:
    """Pass-to-pass tests using repository's own test/lint commands."""

    def test_database_schemas_syntax(self):
        """Database schemas.py should be syntactically valid Python."""
        schemas_path = REPO / "superset" / "mcp_service" / "database" / "schemas.py"

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(schemas_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, \
            f"schemas.py has syntax errors: {result.stderr}"

    def test_list_databases_syntax(self):
        """list_databases.py should be syntactically valid Python."""
        list_db_path = REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(list_db_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, \
            f"list_databases.py has syntax errors: {result.stderr}"

    def test_app_py_syntax(self):
        """app.py should be syntactically valid Python."""
        app_path = REPO / "superset" / "mcp_service" / "app.py"

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(app_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, \
            f"app.py has syntax errors: {result.stderr}"

    def test_imports_resolve(self):
        """Key imports should be resolvable."""
        # Test that schema_utils imports work
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.utils.schema_utils import parse_json_or_list, parse_json_or_model_list"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO
        )
        # This might fail due to dependencies, but we check the error isn't about missing module
        if result.returncode != 0:
            # If it fails, it should be due to missing dependencies, not missing functions
            assert "parse_json_or_list" not in result.stderr or "No module named" in result.stderr, \
                f"Import failed unexpectedly: {result.stderr}"

    def test_repo_ruff_database_module(self):
        """Repo's ruff linter passes on database module (pass_to_pass)."""
        result = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        # Install may fail if already installed, that's OK

        result = subprocess.run(
            ["ruff", "check", "superset/mcp_service/database/"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, \
            f"Ruff linting failed on database module:\n{result.stdout[-500:]}{result.stderr[-500:]}"

    def test_repo_ruff_mcp_app(self):
        """Repo's ruff linter passes on mcp_service app.py (pass_to_pass)."""
        result = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        result = subprocess.run(
            ["ruff", "check", "superset/mcp_service/app.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, \
            f"Ruff linting failed on app.py:\n{result.stdout[-500:]}{result.stderr[-500:]}"

    def test_repo_ruff_mcp_tests(self):
        """Repo's ruff linter passes on MCP unit tests (pass_to_pass)."""
        result = subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
        )

        result = subprocess.run(
            ["ruff", "check", "tests/unit_tests/mcp_service/"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert result.returncode == 0, \
            f"Ruff linting failed on MCP tests:\n{result.stdout[-500:]}{result.stderr[-500:]}"

    def test_database_schemas_imports(self):
        """Database schemas module imports should be resolvable (pass_to_pass)."""
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.database.schemas import DatabaseFilter, DatabaseInfo, DatabaseList, ListDatabasesRequest"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, \
            f"Database schemas imports failed:\n{result.stderr[-500:]}"

    def test_database_test_file_syntax(self):
        """Database test file should be syntactically valid Python (pass_to_pass)."""
        test_path = REPO / "tests" / "unit_tests" / "mcp_service" / "database" / "tool" / "test_database_tools.py"

        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(test_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, \
            f"test_database_tools.py has syntax errors: {result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
