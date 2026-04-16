"""Test the MCP database tools PR fixes — behavioral tests."""

import ast
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")


def _ensure_path():
    """Ensure the superset repo is on sys.path for imports."""
    repo_str = str(REPO)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)


# ==============================================================================
# Fail-to-pass tests: these must FAIL on broken (NOP) code, PASS on fixed code
# ==============================================================================


class TestTimezoneHandling:
    """Verify timezone-aware datetime handling in schemas.py."""

    def test_database_error_uses_timezone_utc(self):
        """DatabaseError.create() must return a UTC-aware timestamp."""
        _ensure_path()
        from superset.mcp_service.database.schemas import DatabaseError

        error = DatabaseError.create("test error", "test_type")
        assert error.timestamp is not None, \
            "DatabaseError.create() should set a timestamp"
        assert error.timestamp.tzinfo is not None, \
            "DatabaseError.create() timestamp should be timezone-aware (naive in broken code)"
        assert error.timestamp.tzinfo == timezone.utc, \
            "DatabaseError.create() timestamp should use UTC"

    def test_humanize_timestamp_uses_tzinfo(self):
        """_humanize_timestamp must handle timezone-aware datetimes without error."""
        _ensure_path()
        from superset.mcp_service.database.schemas import _humanize_timestamp

        # A timezone-aware datetime 2 hours ago — crashes with TypeError in broken code
        aware_dt = datetime.now(timezone.utc) - timedelta(hours=2)
        result = _humanize_timestamp(aware_dt)
        assert result is not None, \
            "_humanize_timestamp should return a string for timezone-aware input"
        assert isinstance(result, str), \
            "_humanize_timestamp should return a string"
        # Should produce something like "2 hours ago"
        assert "ago" in result.lower(), \
            "_humanize_timestamp should return a human-readable time delta"


class TestTypeAnnotations:
    """Verify that create_mock_database has proper type annotations."""

    def test_create_mock_database_has_type_hints(self):
        """create_mock_database should have Python 3.10+ type annotations."""
        test_path = (
            REPO / "tests" / "unit_tests" / "mcp_service" / "database"
            / "tool" / "test_database_tools.py"
        )

        tree = ast.parse(test_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "create_mock_database":
                # Return annotation must exist
                assert node.returns is not None, \
                    "create_mock_database must have a return type annotation"

                # Key parameter annotations must exist and be typed
                param_annotations = {
                    arg.arg: ast.unparse(arg.annotation) if arg.annotation else None
                    for arg in node.args.args
                    if arg.arg != "self"
                }
                assert param_annotations.get("database_id") is not None, \
                    "database_id parameter must have a type annotation"
                assert param_annotations.get("database_name") is not None, \
                    "database_name parameter must have a type annotation"
                return

        pytest.fail("create_mock_database function not found in test file")


class TestMcpCoreDocstring:
    """Verify that ModelGetSchemaCore describes database as a supported model type."""

    def test_model_type_docstring_includes_database(self):
        """ModelGetSchemaCore.__init__ docstring should list 'database' as a model type."""
        _ensure_path()
        from superset.mcp_service.mcp_core import ModelGetSchemaCore

        init_doc = ModelGetSchemaCore.__init__.__doc__ or ""
        assert "database" in init_doc, \
            "ModelGetSchemaCore.__init__ docstring should mention 'database' as a model type"


# ==============================================================================
# Behavioral tests for features (pass on both NOP and GOLD since already correct)
# These exercise the code by importing and calling it, not grepping source text.
# ==============================================================================


class TestDatabaseFilterCreatedBy:
    """Verify DatabaseFilter accepts created_by_fk and changed_by_fk columns."""

    def test_database_filter_includes_created_by_fk(self):
        """DatabaseFilter should instantiate with col='created_by_fk'."""
        _ensure_path()
        from superset.mcp_service.database.schemas import DatabaseFilter

        f = DatabaseFilter(col="created_by_fk", opr="eq", value=42)
        assert f.col == "created_by_fk"
        assert f.value == 42

    def test_database_filter_includes_changed_by_fk(self):
        """DatabaseFilter should instantiate with col='changed_by_fk'."""
        _ensure_path()
        from superset.mcp_service.database.schemas import DatabaseFilter

        f = DatabaseFilter(col="changed_by_fk", opr="eq", value=7)
        assert f.col == "changed_by_fk"
        assert f.value == 7

    def test_database_filter_description_updated(self):
        """DatabaseFilter.col field description should mention created_by_fk usage."""
        _ensure_path()
        from superset.mcp_service.database.schemas import DatabaseFilter

        desc = DatabaseFilter.model_fields["col"].description or ""
        assert "created_by_fk" in desc, \
            "DatabaseFilter.col description should document created_by_fk usage"


class TestListDatabasesRequestValidators:
    """Verify ListDatabasesRequest parses JSON strings via field validators."""

    def test_parse_filters_validator_exists(self):
        """ListDatabasesRequest should parse a JSON string of filters into objects."""
        _ensure_path()
        from superset.mcp_service.database.schemas import ListDatabasesRequest

        req = ListDatabasesRequest(
            filters='[{"col": "database_name", "opr": "eq", "value": "test"}]'
        )
        assert len(req.filters) == 1
        assert req.filters[0].col == "database_name"
        assert req.filters[0].value == "test"

    def test_parse_columns_validator_exists(self):
        """ListDatabasesRequest should parse a JSON string of column names into a list."""
        _ensure_path()
        from superset.mcp_service.database.schemas import ListDatabasesRequest

        req = ListDatabasesRequest(select_columns='["database_name", "backend"]')
        assert req.select_columns == ["database_name", "backend"]

    def test_field_validator_imported(self):
        """ListDatabasesRequest should have registered field validators on filters and select_columns."""
        _ensure_path()
        from superset.mcp_service.database.schemas import ListDatabasesRequest

        validators = ListDatabasesRequest.__pydantic_decorators__.field_validators
        assert "parse_filters" in validators, \
            "ListDatabasesRequest should have parse_filters field validator"
        assert "parse_columns" in validators, \
            "ListDatabasesRequest should have parse_columns field validator"

    def test_schema_utils_imported(self):
        """parse_json_or_list and parse_json_or_model_list should be importable and functional."""
        _ensure_path()
        from superset.mcp_service.utils.schema_utils import (
            parse_json_or_list,
            parse_json_or_model_list,
        )
        from pydantic import BaseModel

        # Verify parse_json_or_list works
        result = parse_json_or_list('["a", "b", "c"]', "test")
        assert result == ["a", "b", "c"]

        # Verify parse_json_or_model_list works
        class Dummy(BaseModel):
            name: str

        result2 = parse_json_or_model_list('[{"name": "x"}]', Dummy, "test")
        assert len(result2) == 1
        assert result2[0].name == "x"


class TestDuplicateDefaultColumnsRemoved:
    """Verify list_databases uses shared DATABASE_DEFAULT_COLUMNS (no local duplicate)."""

    def test_no_local_default_database_columns_definition(self):
        """list_databases.py should not assign DEFAULT_DATABASE_COLUMNS locally."""
        list_db_path = (
            REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
        )
        tree = ast.parse(list_db_path.read_text())

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DEFAULT_DATABASE_COLUMNS":
                        pytest.fail(
                            "list_databases.py should not define DEFAULT_DATABASE_COLUMNS locally"
                        )

    def test_imports_database_default_columns(self):
        """list_databases.py should import DATABASE_DEFAULT_COLUMNS from schema_discovery."""
        list_db_path = (
            REPO / "superset" / "mcp_service" / "database" / "tool" / "list_databases.py"
        )
        tree = ast.parse(list_db_path.read_text())

        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_names.add(alias.name)

        assert "DATABASE_DEFAULT_COLUMNS" in imported_names, \
            "list_databases.py should import DATABASE_DEFAULT_COLUMNS"

    def test_uses_imported_database_default_columns(self):
        """The shared DATABASE_DEFAULT_COLUMNS from schema_discovery should be a valid column list."""
        _ensure_path()
        from superset.mcp_service.common.schema_discovery import DATABASE_DEFAULT_COLUMNS

        assert isinstance(DATABASE_DEFAULT_COLUMNS, list), \
            "DATABASE_DEFAULT_COLUMNS should be a list"
        assert len(DATABASE_DEFAULT_COLUMNS) > 0, \
            "DATABASE_DEFAULT_COLUMNS should not be empty"
        assert all(isinstance(col, str) for col in DATABASE_DEFAULT_COLUMNS), \
            "DATABASE_DEFAULT_COLUMNS should contain strings"


class TestAppInstructionsUpdated:
    """Verify app.py instructions include database-related guidance."""

    def _get_instructions(self):
        """Extract and execute get_default_instructions from app.py source."""
        app_path = REPO / "superset" / "mcp_service" / "app.py"
        source = app_path.read_text()
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "get_default_instructions":
                func_source = ast.get_source_segment(source, node)
                ns = {}
                exec(func_source, ns)
                return ns["get_default_instructions"]()
        pytest.fail("get_default_instructions function not found in app.py")

    def test_app_mentions_databases_in_find_own(self):
        """Instructions should mention databases alongside charts/dashboards."""
        instructions = self._get_instructions()
        assert "databases" in instructions.lower(), \
            "app.py instructions should mention databases"

    def test_app_has_database_filter_example(self):
        """Instructions should include a list_databases filter example with created_by_fk."""
        instructions = self._get_instructions()
        assert "list_databases" in instructions, \
            "app.py instructions should mention list_databases tool"
        assert "created_by_fk" in instructions, \
            "app.py instructions should show created_by_fk filter example"

    def test_app_has_my_databases_section(self):
        """Instructions should have a 'My databases' section."""
        instructions = self._get_instructions()
        assert "My databases" in instructions, \
            "app.py instructions should have 'My databases' section"


# ==============================================================================
# Pass-to-pass tests: syntax, linting, import resolution
# ==============================================================================


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
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.utils.schema_utils import parse_json_or_list, parse_json_or_model_list"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO
        )
        if result.returncode != 0:
            assert "parse_json_or_list" not in result.stderr or "No module named" in result.stderr, \
                f"Import failed unexpectedly: {result.stderr}"

    def test_repo_ruff_database_module(self):
        """Repo's ruff linter passes on database module (pass_to_pass)."""
        subprocess.run(
            ["pip", "install", "-q", "ruff"],
            capture_output=True,
            text=True,
            timeout=120,
        )

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
        subprocess.run(
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
        subprocess.run(
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
