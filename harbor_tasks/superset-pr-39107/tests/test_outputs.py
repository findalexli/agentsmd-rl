"""
Tests for superset-mcp-truncation task.

This tests the dynamic response truncation functionality added in apache/superset#39107.
The PR adds progressive truncation for MCP info tool responses that exceed token limits.
"""

import sys
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")


class TestTruncationFunctionsExist:
    """Test that the new truncation functions exist and are importable (fail_to_pass)."""

    def test_info_tools_constant_exists(self):
        """INFO_TOOLS constant should be defined in token_utils."""
        # This import will fail on base commit since INFO_TOOLS doesn't exist
        from superset.mcp_service.utils.token_utils import INFO_TOOLS

        assert isinstance(INFO_TOOLS, frozenset), "INFO_TOOLS should be a frozenset"
        assert len(INFO_TOOLS) == 4, f"INFO_TOOLS should have 4 tools, got {len(INFO_TOOLS)}"
        assert "get_chart_info" in INFO_TOOLS
        assert "get_dataset_info" in INFO_TOOLS
        assert "get_dashboard_info" in INFO_TOOLS
        assert "get_instance_info" in INFO_TOOLS

    def test_truncate_oversized_response_exists(self):
        """truncate_oversized_response function should be importable."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        assert callable(truncate_oversized_response)


class TestTruncateStrings:
    """Test _truncate_strings helper function (fail_to_pass)."""

    def test_truncates_long_strings(self):
        """Should truncate strings exceeding max_chars."""
        from superset.mcp_service.utils.token_utils import _truncate_strings

        data = {"description": "x" * 1000, "name": "short"}
        notes = []
        changed = _truncate_strings(data, notes, max_chars=500)

        assert changed is True, "Should return True when truncation occurs"
        assert len(data["description"]) < 1000, "Description should be truncated"
        assert "[truncated from 1000 chars]" in data["description"]
        assert data["name"] == "short", "Short strings should be unchanged"
        assert len(notes) == 1, "Should have one note"

    def test_does_not_truncate_short_strings(self):
        """Should not truncate strings within limit."""
        from superset.mcp_service.utils.token_utils import _truncate_strings

        data = {"name": "hello", "id": 123}
        notes = []
        changed = _truncate_strings(data, notes, max_chars=500)

        assert changed is False, "Should return False when no truncation"
        assert data["name"] == "hello"
        assert len(notes) == 0

    def test_truncates_multiple_fields(self):
        """Should truncate multiple long string fields."""
        from superset.mcp_service.utils.token_utils import _truncate_strings

        data = {
            "description": "a" * 800,
            "css": "b" * 900,
            "json_metadata": "c" * 1000,
            "short_field": "ok"
        }
        notes = []
        changed = _truncate_strings(data, notes, max_chars=500)

        assert changed is True
        assert len(notes) == 3, "Should have notes for all truncated fields"
        assert "[truncated" in data["description"]
        assert "[truncated" in data["css"]
        assert "[truncated" in data["json_metadata"]
        assert data["short_field"] == "ok"


class TestTruncateStringsRecursive:
    """Test _truncate_strings_recursive helper function (fail_to_pass)."""

    def test_truncates_nested_strings_in_list_items(self):
        """Should truncate strings inside list items."""
        from superset.mcp_service.utils.token_utils import _truncate_strings_recursive

        data = {
            "id": 1,
            "charts": [
                {"id": 1, "description": "x" * 1000},
                {"id": 2, "description": "short"},
            ],
        }
        notes = []
        changed = _truncate_strings_recursive(data, notes, max_chars=500)

        assert changed is True
        assert "[truncated" in data["charts"][0]["description"]
        assert data["charts"][1]["description"] == "short"
        assert len(notes) == 1
        assert "charts[0].description" in notes[0]

    def test_truncates_nested_strings_in_dicts(self):
        """Should truncate strings inside nested dicts."""
        from superset.mcp_service.utils.token_utils import _truncate_strings_recursive

        data = {
            "filter_state": {
                "dataMask": {"some_filter": "y" * 2000},
            },
        }
        notes = []
        changed = _truncate_strings_recursive(data, notes, max_chars=500)

        assert changed is True
        assert "[truncated" in data["filter_state"]["dataMask"]["some_filter"]

    def test_respects_depth_limit(self):
        """Should stop recursing at depth 10."""
        from superset.mcp_service.utils.token_utils import _truncate_strings_recursive

        # Build a deeply nested structure (15 levels)
        data = {"level": "x" * 1000}
        current = data
        for _ in range(15):
            current["nested"] = {"level": "x" * 1000}
            current = current["nested"]
        notes = []
        _truncate_strings_recursive(data, notes, max_chars=500)

        # Should truncate levels 0-10 but stop before 15
        assert len(notes) <= 11, f"Should respect depth limit, got {len(notes)} notes"

    def test_handles_empty_structures(self):
        """Should handle empty dicts and lists gracefully."""
        from superset.mcp_service.utils.token_utils import _truncate_strings_recursive

        data = {"items": [], "meta": {}, "name": "ok"}
        notes = []
        changed = _truncate_strings_recursive(data, notes, max_chars=500)

        assert changed is False


class TestTruncateLists:
    """Test _truncate_lists helper function (fail_to_pass)."""

    def test_truncates_long_lists(self):
        """Should truncate lists exceeding max_items without inline markers."""
        from superset.mcp_service.utils.token_utils import _truncate_lists

        data = {
            "columns": [{"name": f"col_{i}"} for i in range(50)],
            "tags": [1, 2],
        }
        notes = []
        changed = _truncate_lists(data, notes, max_items=10)

        assert changed is True
        assert len(data["columns"]) == 10, "Should truncate to 10 items"
        # Verify all items are still dicts (no marker object appended)
        assert all(isinstance(c, dict) and "name" in c for c in data["columns"])
        assert data["tags"] == [1, 2], "Short list should be unchanged"
        assert len(notes) == 1
        assert "50" in notes[0]

    def test_does_not_truncate_short_lists(self):
        """Should not truncate lists within limit."""
        from superset.mcp_service.utils.token_utils import _truncate_lists

        data = {"items": [1, 2, 3]}
        notes = []
        changed = _truncate_lists(data, notes, max_items=10)

        assert changed is False
        assert data["items"] == [1, 2, 3]


class TestSummarizeLargeDicts:
    """Test _summarize_large_dicts helper function (fail_to_pass)."""

    def test_summarizes_large_dicts(self):
        """Should replace large dicts with key summaries."""
        from superset.mcp_service.utils.token_utils import _summarize_large_dicts

        big_dict = {f"key_{i}": f"value_{i}" for i in range(30)}
        data = {"form_data": big_dict, "id": 1}
        notes = []
        changed = _summarize_large_dicts(data, notes, max_keys=20)

        assert changed is True
        assert data["form_data"]["_truncated"] is True
        assert "30 keys" in data["form_data"]["_message"]
        assert data["id"] == 1

    def test_does_not_summarize_small_dicts(self):
        """Should not summarize dicts within limit."""
        from superset.mcp_service.utils.token_utils import _summarize_large_dicts

        data = {"params": {"a": 1, "b": 2}}
        notes = []
        changed = _summarize_large_dicts(data, notes, max_keys=20)

        assert changed is False
        assert data["params"] == {"a": 1, "b": 2}


class TestReplaceCollectionsWithSummaries:
    """Test _replace_collections_with_summaries helper function (fail_to_pass)."""

    def test_replaces_lists_and_dicts(self):
        """Should clear non-empty collections to reduce size."""
        from superset.mcp_service.utils.token_utils import _replace_collections_with_summaries

        data = {
            "columns": [1, 2, 3],
            "params": {"a": 1},
            "name": "test",
            "empty": [],
        }
        notes = []
        changed = _replace_collections_with_summaries(data, notes)

        assert changed is True
        assert data["columns"] == [], "Lists should become empty lists"
        assert data["params"] == {}, "Dicts should become empty dicts"
        assert data["name"] == "test", "Scalars unchanged"
        assert data["empty"] == [], "Already empty stays empty"
        assert len(notes) == 2


class TestTruncateOversizedResponse:
    """Test truncate_oversized_response main function (fail_to_pass)."""

    def test_no_truncation_needed(self):
        """Should return original data when under limit."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        response = {"id": 1, "name": "test"}
        result, was_truncated, notes = truncate_oversized_response(response, 10000)

        assert was_truncated is False
        assert notes == []

    def test_truncates_large_string_fields(self):
        """Should truncate long strings to fit."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        response = {
            "id": 1,
            "description": "x" * 50000,
        }
        result, was_truncated, notes = truncate_oversized_response(response, 500)

        assert was_truncated is True
        assert isinstance(result, dict)
        assert "[truncated" in result["description"]
        assert any("description" in n for n in notes)

    def test_truncates_large_lists(self):
        """Should truncate lists when strings alone are not enough."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        response = {
            "id": 1,
            "columns": [{"name": f"col_{i}", "type": "VARCHAR"} for i in range(200)],
        }
        result, was_truncated, notes = truncate_oversized_response(response, 500)

        assert was_truncated is True
        assert isinstance(result, dict)
        assert len(result["columns"]) < 200

    def test_returns_non_dict_unchanged(self):
        """Should return non-dict/model responses unchanged."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        result, was_truncated, notes = truncate_oversized_response("just a string", 100)

        assert was_truncated is False
        assert result == "just a string"

    def test_progressive_truncation_phases(self):
        """Should progressively apply truncation phases."""
        from superset.mcp_service.utils.token_utils import truncate_oversized_response

        # Build a response that's quite large requiring multiple phases
        response = {
            "id": 1,
            "description": "x" * 2000,
            "css": "y" * 2000,
            "columns": [{"name": f"col_{i}"} for i in range(100)],
            "form_data": {f"key_{i}": f"val_{i}" for i in range(50)},
        }
        result, was_truncated, notes = truncate_oversized_response(response, 300)

        assert was_truncated is True
        assert isinstance(result, dict)
        assert result["id"] == 1, "Scalar fields should be preserved"
        assert len(notes) > 0, "Should have truncation notes"


class TestInfoToolsContent:
    """Test INFO_TOOLS contains correct tools and excludes non-info tools (fail_to_pass)."""

    def test_info_tools_excludes_list_tools(self):
        """INFO_TOOLS should not contain list or write tools."""
        from superset.mcp_service.utils.token_utils import INFO_TOOLS

        # These should NOT be in INFO_TOOLS
        assert "list_charts" not in INFO_TOOLS
        assert "list_dashboards" not in INFO_TOOLS
        assert "list_datasets" not in INFO_TOOLS
        assert "execute_sql" not in INFO_TOOLS
        assert "generate_chart" not in INFO_TOOLS
        assert "get_chart_data" not in INFO_TOOLS

    def test_info_tools_is_immutable(self):
        """INFO_TOOLS should be a frozenset (immutable)."""
        from superset.mcp_service.utils.token_utils import INFO_TOOLS

        assert type(INFO_TOOLS).__name__ == "frozenset"
        # Verify we can't modify it
        try:
            INFO_TOOLS.add("test")  # type: ignore
            assert False, "Should not be able to add to frozenset"
        except AttributeError:
            pass  # Expected


class TestDashboardEdgeCase:
    """Test edge case with dashboard containing many charts (fail_to_pass)."""

    def test_dashboard_with_many_charts(self):
        """Simulate a dashboard with 30 charts each having long descriptions."""
        from superset.mcp_service.utils.token_utils import _truncate_strings_recursive

        data = {
            "id": 1,
            "dashboard_title": "Big Dashboard",
            "charts": [
                {"id": i, "slice_name": f"Chart {i}", "description": "d" * 2000}
                for i in range(30)
            ],
        }
        notes = []
        changed = _truncate_strings_recursive(data, notes, max_chars=500)

        assert changed is True
        # All 30 chart descriptions should be truncated
        assert len(notes) == 30, f"Expected 30 notes, got {len(notes)}"
        for chart in data["charts"]:
            assert len(chart["description"]) < 2000
            assert "[truncated" in chart["description"]


class TestPythonSyntax:
    """Test that the modified files have valid Python syntax (pass_to_pass)."""

    def test_token_utils_syntax(self):
        """token_utils.py should have valid Python syntax."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile",
             str(REPO / "superset/mcp_service/utils/token_utils.py")],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Syntax error in token_utils.py:\n{result.stderr}"

    def test_middleware_syntax(self):
        """middleware.py should have valid Python syntax."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile",
             str(REPO / "superset/mcp_service/middleware.py")],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Syntax error in middleware.py:\n{result.stderr}"


class TestRuffLinting:
    """Test ruff linting passes on modified files (pass_to_pass)."""

    @classmethod
    def setup_class(cls):
        """Install ruff if not already available."""
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "--quiet"],
            capture_output=True,
            timeout=120
        )

    def test_ruff_check_token_utils(self):
        """ruff check passes on token_utils.py (pass_to_pass)."""
        result = subprocess.run(
            ["ruff", "check", str(REPO / "superset/mcp_service/utils/token_utils.py")],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_check_middleware(self):
        """ruff check passes on middleware.py (pass_to_pass)."""
        result = subprocess.run(
            ["ruff", "check", str(REPO / "superset/mcp_service/middleware.py")],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_format_token_utils(self):
        """ruff format check passes on token_utils.py (pass_to_pass)."""
        result = subprocess.run(
            ["ruff", "format", "--check", str(REPO / "superset/mcp_service/utils/token_utils.py")],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_format_middleware(self):
        """ruff format check passes on middleware.py (pass_to_pass)."""
        result = subprocess.run(
            ["ruff", "format", "--check", str(REPO / "superset/mcp_service/middleware.py")],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"


class TestTokenUtilsImportAndBaseFunctionality:
    """Test that token_utils module imports and base functions work (pass_to_pass)."""

    def test_token_utils_module_imports(self):
        """token_utils module should import successfully (pass_to_pass)."""
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.utils.token_utils import "
             "estimate_token_count, estimate_response_tokens, CHARS_PER_TOKEN; "
             "print('Import successful')"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
            env={**subprocess.os.environ, "PYTHONPATH": str(REPO)}
        )
        assert result.returncode == 0, f"Import failed:\n{result.stderr}"
        assert "Import successful" in result.stdout

    def test_estimate_token_count_works(self):
        """estimate_token_count function works correctly (pass_to_pass)."""
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.utils.token_utils import estimate_token_count, CHARS_PER_TOKEN; "
             "text = 'Hello world'; "
             "expected = int(len(text) / CHARS_PER_TOKEN); "
             "result = estimate_token_count(text); "
             "assert result == expected, f'Expected {expected}, got {result}'; "
             "print('Test passed')"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
            env={**subprocess.os.environ, "PYTHONPATH": str(REPO)}
        )
        assert result.returncode == 0, f"Test failed:\n{result.stderr}"
        assert "Test passed" in result.stdout

    def test_estimate_response_tokens_works(self):
        """estimate_response_tokens function works correctly (pass_to_pass)."""
        result = subprocess.run(
            [sys.executable, "-c",
             "from superset.mcp_service.utils.token_utils import estimate_response_tokens; "
             "response = {'name': 'test', 'value': 42}; "
             "result = estimate_response_tokens(response); "
             "assert result > 0, f'Expected > 0, got {result}'; "
             "print('Test passed')"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
            env={**subprocess.os.environ, "PYTHONPATH": str(REPO)}
        )
        assert result.returncode == 0, f"Test failed:\n{result.stderr}"
        assert "Test passed" in result.stdout
