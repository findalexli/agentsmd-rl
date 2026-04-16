"""
Benchmark tests for apache/superset#39113
Tests for MCP database schema validators and filter columns.

Note: conftest.py sets up mocks to avoid importing the full superset app.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

REPO = Path("/workspace/superset")


def get_database_filter():
    """Import DatabaseFilter."""
    from superset.mcp_service.database.schemas import DatabaseFilter
    return DatabaseFilter


def get_list_databases_request():
    """Import ListDatabasesRequest."""
    from superset.mcp_service.database.schemas import ListDatabasesRequest
    return ListDatabasesRequest


def get_database_error():
    """Import DatabaseError."""
    from superset.mcp_service.database.schemas import DatabaseError
    return DatabaseError


def get_humanize_timestamp():
    """Import _humanize_timestamp."""
    from superset.mcp_service.database.schemas import _humanize_timestamp
    return _humanize_timestamp


class TestDatabaseErrorTimezone:
    """Test that DatabaseError.create uses timezone-aware datetime (fail_to_pass)."""

    def test_database_error_create_returns_utc_timestamp(self):
        """DatabaseError.create() should return a timezone-aware UTC timestamp."""
        DatabaseError = get_database_error()

        error = DatabaseError.create(error="test error", error_type="TestError")

        # The timestamp should be timezone-aware (has tzinfo)
        assert error.timestamp is not None
        assert error.timestamp.tzinfo is not None, "Timestamp should be timezone-aware"
        assert error.timestamp.tzinfo == timezone.utc, "Timestamp should be UTC"

    def test_database_error_create_varied_inputs(self):
        """Test DatabaseError.create with various error messages."""
        DatabaseError = get_database_error()

        test_cases = [
            ("Connection failed", "ConnectionError"),
            ("Invalid query", "QueryError"),
            ("Permission denied", "AuthError"),
        ]

        for error_msg, error_type in test_cases:
            error = DatabaseError.create(error=error_msg, error_type=error_type)
            assert error.error == error_msg
            assert error.error_type == error_type
            assert error.timestamp.tzinfo is not None, f"Timestamp should be tz-aware for {error_msg}"


class TestHumanizeTimestampTimezone:
    """Test that _humanize_timestamp respects timezone info (fail_to_pass)."""

    def test_humanize_timestamp_with_utc_datetime(self):
        """_humanize_timestamp should work correctly with UTC datetime."""
        _humanize_timestamp = get_humanize_timestamp()

        # Create a timezone-aware datetime 1 hour ago
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        result = _humanize_timestamp(one_hour_ago)

        # Should return something like "an hour ago" or "1 hour ago"
        assert result is not None
        assert "hour" in result.lower() or "minute" in result.lower()

    def test_humanize_timestamp_with_offset_timezone(self):
        """_humanize_timestamp should work with non-UTC timezone offsets."""
        _humanize_timestamp = get_humanize_timestamp()

        # Create a timezone with +5 hours offset
        tz_plus5 = timezone(timedelta(hours=5))
        two_hours_ago = datetime.now(tz_plus5) - timedelta(hours=2)

        result = _humanize_timestamp(two_hours_ago)

        # Should return something indicating ~2 hours ago
        assert result is not None
        assert "hour" in result.lower()

    def test_humanize_timestamp_none_returns_none(self):
        """_humanize_timestamp should return None for None input."""
        _humanize_timestamp = get_humanize_timestamp()

        result = _humanize_timestamp(None)
        assert result is None


class TestDatabaseFilterColumns:
    """Test that DatabaseFilter accepts filter columns (pass_to_pass)."""

    def test_database_filter_accepts_created_by_fk(self):
        """DatabaseFilter should accept 'created_by_fk' as a valid column."""
        DatabaseFilter = get_database_filter()

        filter_obj = DatabaseFilter(col="created_by_fk", opr="eq", value=123)
        assert filter_obj.col == "created_by_fk"
        assert filter_obj.opr == "eq"
        assert filter_obj.value == 123

    def test_database_filter_accepts_changed_by_fk(self):
        """DatabaseFilter should accept 'changed_by_fk' as a valid column."""
        DatabaseFilter = get_database_filter()

        filter_obj = DatabaseFilter(col="changed_by_fk", opr="eq", value=456)
        assert filter_obj.col == "changed_by_fk"
        assert filter_obj.opr == "eq"
        assert filter_obj.value == 456

    def test_database_filter_multiple_operators(self):
        """DatabaseFilter should work with various operators."""
        DatabaseFilter = get_database_filter()

        # Test with different operators (use 'ne' not 'neq')
        for opr in ["eq", "ne"]:
            for user_id in [1, 42, 999]:
                filter_obj = DatabaseFilter(col="created_by_fk", opr=opr, value=user_id)
                assert filter_obj.col == "created_by_fk"
                assert filter_obj.value == user_id


class TestListDatabasesRequestValidators:
    """Test field validators for ListDatabasesRequest (pass_to_pass)."""

    def test_filters_validator_accepts_json_string(self):
        """ListDatabasesRequest should parse JSON string for filters field."""
        ListDatabasesRequest = get_list_databases_request()

        # JSON string input - this is what MCP clients send
        json_str = '[{"col": "database_name", "opr": "eq", "value": "test_db"}]'

        request = ListDatabasesRequest(filters=json_str)

        assert request.filters is not None
        assert len(request.filters) == 1
        assert request.filters[0].col == "database_name"
        assert request.filters[0].value == "test_db"

    def test_filters_validator_accepts_list_of_dicts(self):
        """ListDatabasesRequest should accept list of dicts for filters field."""
        ListDatabasesRequest = get_list_databases_request()

        filters_list = [{"col": "expose_in_sqllab", "opr": "eq", "value": True}]

        request = ListDatabasesRequest(filters=filters_list)

        assert request.filters is not None
        assert len(request.filters) == 1
        assert request.filters[0].col == "expose_in_sqllab"
        assert request.filters[0].value is True

    def test_select_columns_validator_accepts_json_string(self):
        """ListDatabasesRequest should parse JSON array string for select_columns."""
        ListDatabasesRequest = get_list_databases_request()

        # JSON array string
        json_str = '["id", "database_name", "backend"]'

        request = ListDatabasesRequest(select_columns=json_str)

        assert request.select_columns is not None
        assert request.select_columns == ["id", "database_name", "backend"]

    def test_select_columns_validator_accepts_list(self):
        """ListDatabasesRequest should accept list for select_columns."""
        ListDatabasesRequest = get_list_databases_request()

        columns = ["id", "database_name"]

        request = ListDatabasesRequest(select_columns=columns)

        assert request.select_columns == ["id", "database_name"]


class TestFiltersValidatorWithCreatedByFk:
    """Combined test: validators + filter columns (pass_to_pass)."""

    def test_filters_json_string_with_created_by_fk(self):
        """ListDatabasesRequest should parse JSON string with created_by_fk filter."""
        ListDatabasesRequest = get_list_databases_request()

        json_str = '[{"col": "created_by_fk", "opr": "eq", "value": 42}]'

        request = ListDatabasesRequest(filters=json_str)

        assert request.filters is not None
        assert len(request.filters) == 1
        assert request.filters[0].col == "created_by_fk"
        assert request.filters[0].value == 42


class TestExistingDatabaseFilterColumns:
    """Test that existing DatabaseFilter columns work (pass_to_pass)."""

    def test_database_filter_existing_columns(self):
        """DatabaseFilter should accept existing valid columns."""
        DatabaseFilter = get_database_filter()

        # Use columns that are actually valid in DatabaseFilter
        existing_columns = ["database_name", "expose_in_sqllab", "allow_file_upload"]

        for col in existing_columns:
            filter_obj = DatabaseFilter(col=col, opr="eq", value="test")
            assert filter_obj.col == col


class TestListDatabasesRequestBasicValidation:
    """Test that basic ListDatabasesRequest validation works (pass_to_pass)."""

    def test_list_databases_request_default_values(self):
        """ListDatabasesRequest should work with default values."""
        ListDatabasesRequest = get_list_databases_request()

        request = ListDatabasesRequest()
        assert request.page == 1
        assert request.page_size is not None


class TestDatabaseErrorBasicCreation:
    """Test that DatabaseError basic fields work (pass_to_pass)."""

    def test_database_error_fields(self):
        """DatabaseError should have correct error and error_type fields."""
        DatabaseError = get_database_error()

        error = DatabaseError.create(error="test", error_type="TestType")

        assert error.error == "test"
        assert error.error_type == "TestType"
        assert error.timestamp is not None


# =============================================================================
# Subprocess-based CI tests (pass_to_pass, origin: repo_tests)
# These tests run actual CI commands used by the repo's pre-commit hooks
# =============================================================================
import subprocess


class TestRepoCICommands:
    """Run actual CI commands from the repo's pre-commit config (pass_to_pass)."""

    def test_repo_ruff_lint_schemas(self):
        """Ruff lint check passes on database schemas (pass_to_pass)."""
        # Install ruff and run lint check - matches repo's pre-commit config
        result = subprocess.run(
            ["bash", "-c", "pip install --quiet ruff && ruff check superset/mcp_service/database/schemas.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"Ruff lint failed:\n{result.stdout}\n{result.stderr[-500:]}"

    def test_repo_ruff_format_schemas(self):
        """Ruff format check passes on database schemas (pass_to_pass)."""
        # Install ruff and run format check - matches repo's pre-commit config
        result = subprocess.run(
            ["bash", "-c", "pip install --quiet ruff && ruff format --check superset/mcp_service/database/schemas.py"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr[-500:]}"

    def test_repo_python_syntax_schemas(self):
        """Python syntax check passes on database schemas (pass_to_pass)."""
        # Python compilation check - basic CI validation
        result = subprocess.run(
            ["python", "-m", "py_compile", "superset/mcp_service/database/schemas.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"Python syntax check failed:\n{result.stderr[-500:]}"
