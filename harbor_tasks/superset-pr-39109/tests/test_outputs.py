"""
Benchmark tests for apache/superset PR #39109
Tests 4 MCP service bug fixes:
1. serialize_chart_object returns form_data=null
2. serialize_dataset_object returns relative URL
3. ASCII preview crashes with empty columns
4. update_chart requires config for rename
"""

import json
import sys
import unittest
from unittest.mock import MagicMock, patch
import subprocess
import os

REPO = "/workspace/superset"


class TestSerializeChartFormData(unittest.TestCase):
    """Tests for form_data serialization in serialize_chart_object (fail_to_pass)."""

    def test_form_data_populated_from_json_params(self):
        """form_data should be parsed from chart.params JSON string."""
        # Read the source file directly and check for the fix
        schemas_path = os.path.join(REPO, "superset/mcp_service/chart/schemas.py")
        with open(schemas_path, 'r') as f:
            content = f.read()

        # Bug: In base commit, form_data is not populated from params
        # Fix: Should parse chart_params and set chart_form_data
        self.assertIn("chart_form_data", content,
                      "serialize_chart_object should define chart_form_data variable")
        self.assertIn("utils_json.loads(chart_params)", content,
                      "Should parse params JSON to populate form_data")
        self.assertIn("form_data=chart_form_data", content,
                      "ChartInfo should include form_data=chart_form_data")

    def test_form_data_handles_dict_params(self):
        """form_data should work when chart.params is already a dict."""
        schemas_path = os.path.join(REPO, "superset/mcp_service/chart/schemas.py")
        with open(schemas_path, 'r') as f:
            content = f.read()

        # Should handle dict params directly
        self.assertIn("isinstance(chart_params, dict)", content,
                      "Should handle dict params without JSON parsing")


class TestSerializeDatasetUrl(unittest.TestCase):
    """Tests for absolute URL in serialize_dataset_object (fail_to_pass)."""

    def test_dataset_url_is_absolute(self):
        """Dataset URL should be absolute, not relative."""
        schemas_path = os.path.join(REPO, "superset/mcp_service/dataset/schemas.py")
        with open(schemas_path, 'r') as f:
            content = f.read()

        # Bug: URL was relative (just `getattr(dataset, "url", None)`)
        # Fix: Should construct absolute URL using get_superset_base_url()
        self.assertIn("get_superset_base_url", content,
                      "serialize_dataset_object should use get_superset_base_url for URL")
        self.assertIn("/tablemodelview/edit/", content,
                      "URL should include the edit path")


class TestUpdateChartRequestConfigOptional(unittest.TestCase):
    """Tests for UpdateChartRequest.config being optional (fail_to_pass)."""

    def test_config_field_is_optional(self):
        """UpdateChartRequest.config should be Optional (not required)."""
        schemas_path = os.path.join(REPO, "superset/mcp_service/chart/schemas.py")
        with open(schemas_path, 'r') as f:
            content = f.read()

        # Find the UpdateChartRequest class
        # Bug: config: ChartConfig (required)
        # Fix: config: ChartConfig | None = Field(None, ...)
        self.assertIn("config: ChartConfig | None", content,
                      "UpdateChartRequest.config should be Optional (ChartConfig | None)")

    def test_config_has_default_none(self):
        """UpdateChartRequest.config should default to None."""
        schemas_path = os.path.join(REPO, "superset/mcp_service/chart/schemas.py")
        with open(schemas_path, 'r') as f:
            content = f.read()

        # Check config has Field(None, ...)
        # Look for pattern like: config: ChartConfig | None = Field(\n        None,
        self.assertIn("config: ChartConfig | None = Field(", content,
                      "config should use Field with default")


class TestBuildUpdatePayloadHelper(unittest.TestCase):
    """Tests for _build_update_payload helper function (fail_to_pass)."""

    def test_build_update_payload_exists(self):
        """_build_update_payload helper should exist after the fix."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Bug: This function doesn't exist in base commit
        # Fix: Should extract this helper function
        self.assertIn("def _build_update_payload(", content,
                      "_build_update_payload helper function should exist")

    def test_build_update_payload_returns_name_only(self):
        """_build_update_payload should support name-only updates."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Should return dict with just slice_name for name-only updates
        self.assertIn('return {"slice_name": request.chart_name}', content,
                      "Should return name-only payload when no config")

    def test_build_update_payload_handles_validation_error(self):
        """_build_update_payload should return error when neither config nor name."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Should return ValidationError when neither provided
        self.assertIn("ValidationError", content,
                      "Should return ValidationError when neither config nor chart_name")
        self.assertIn("Either 'config' or 'chart_name' must be provided", content,
                      "Error message should explain the requirement")


class TestFindChartHelper(unittest.TestCase):
    """Tests for _find_chart helper function (fail_to_pass)."""

    def test_find_chart_function_exists(self):
        """_find_chart helper should exist after the fix."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Bug: This function doesn't exist in base commit
        # Fix: Should extract this helper function
        self.assertIn("def _find_chart(", content,
                      "_find_chart helper function should exist")

    def test_find_chart_handles_numeric_id(self):
        """_find_chart should handle numeric IDs."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Should handle numeric identifiers
        self.assertIn("identifier.isdigit()", content,
                      "Should check if identifier is numeric string")
        self.assertIn("int(identifier)", content,
                      "Should convert string digits to int")

    def test_find_chart_handles_uuid(self):
        """_find_chart should handle UUID strings."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Should use id_column="uuid" for non-numeric identifiers
        self.assertIn('id_column="uuid"', content,
                      "Should look up by uuid column for non-numeric identifiers")


class TestErrorResponseStructure(unittest.TestCase):
    """Tests for structured error responses (fail_to_pass)."""

    def test_error_uses_structured_format(self):
        """Errors should use structured ChartGenerationError format."""
        update_chart_path = os.path.join(REPO, "superset/mcp_service/chart/tool/update_chart.py")
        with open(update_chart_path, 'r') as f:
            content = f.read()

        # Bug: Errors were simple strings
        # Fix: Should use structured error dicts with error_type, message, details
        self.assertIn('"error_type":', content,
                      "Errors should include error_type field")
        self.assertIn('"message":', content,
                      "Errors should include message field")
        self.assertIn('"details":', content,
                      "Errors should include details field")


class TestRuffLintPasses(unittest.TestCase):
    """Pass-to-pass test: ruff linting should pass on changed files."""

    def test_ruff_check_mcp_service_schemas(self):
        """Ruff check should pass on MCP service schema files."""
        result = subprocess.run(
            ["python", "-m", "ruff", "check",
             "superset/mcp_service/chart/schemas.py",
             "superset/mcp_service/dataset/schemas.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        self.assertEqual(
            result.returncode, 0,
            f"Ruff check failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_ruff_check_update_chart(self):
        """Ruff check should pass on update_chart.py."""
        result = subprocess.run(
            ["python", "-m", "ruff", "check",
             "superset/mcp_service/chart/tool/update_chart.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        self.assertEqual(
            result.returncode, 0,
            f"Ruff check failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_ruff_check_get_chart_preview(self):
        """Ruff check should pass on get_chart_preview.py (pass_to_pass)."""
        result = subprocess.run(
            ["python", "-m", "ruff", "check",
             "superset/mcp_service/chart/tool/get_chart_preview.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        self.assertEqual(
            result.returncode, 0,
            f"Ruff check failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_ruff_format_modified_files(self):
        """Ruff format check should pass on all modified files (pass_to_pass)."""
        result = subprocess.run(
            ["python", "-m", "ruff", "format", "--check",
             "superset/mcp_service/chart/schemas.py",
             "superset/mcp_service/dataset/schemas.py",
             "superset/mcp_service/chart/tool/update_chart.py",
             "superset/mcp_service/chart/tool/get_chart_preview.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        self.assertEqual(
            result.returncode, 0,
            f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"
        )


class TestPythonSyntax(unittest.TestCase):
    """Pass-to-pass test: Python syntax should be valid."""

    def test_chart_schemas_syntax(self):
        """chart/schemas.py should have valid Python syntax."""
        result = subprocess.run(
            ["python", "-m", "py_compile",
             "superset/mcp_service/chart/schemas.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        self.assertEqual(
            result.returncode, 0,
            f"Syntax error in chart/schemas.py:\n{result.stderr}"
        )

    def test_dataset_schemas_syntax(self):
        """dataset/schemas.py should have valid Python syntax."""
        result = subprocess.run(
            ["python", "-m", "py_compile",
             "superset/mcp_service/dataset/schemas.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        self.assertEqual(
            result.returncode, 0,
            f"Syntax error in dataset/schemas.py:\n{result.stderr}"
        )

    def test_update_chart_syntax(self):
        """update_chart.py should have valid Python syntax."""
        result = subprocess.run(
            ["python", "-m", "py_compile",
             "superset/mcp_service/chart/tool/update_chart.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        self.assertEqual(
            result.returncode, 0,
            f"Syntax error in update_chart.py:\n{result.stderr}"
        )

    def test_get_chart_preview_syntax(self):
        """get_chart_preview.py should have valid Python syntax (pass_to_pass)."""
        result = subprocess.run(
            ["python", "-m", "py_compile",
             "superset/mcp_service/chart/tool/get_chart_preview.py"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        self.assertEqual(
            result.returncode, 0,
            f"Syntax error in get_chart_preview.py:\n{result.stderr}"
        )


class TestGetChartPreviewErrorHandling(unittest.TestCase):
    """Tests for ASCII preview error handling (fail_to_pass)."""

    def test_unsupported_chart_error_exists(self):
        """get_chart_preview should return UnsupportedChart error for empty columns."""
        preview_path = os.path.join(REPO, "superset/mcp_service/chart/tool/get_chart_preview.py")
        with open(preview_path, 'r') as f:
            content = f.read()

        # Bug: Crashes with "Columns missing" when no columns
        # Fix: Should return graceful UnsupportedChart error
        self.assertIn("UnsupportedChart", content,
                      "Should return UnsupportedChart error type")
        self.assertIn("not columns and not metrics", content,
                      "Should check for empty columns and metrics")

    def test_preview_error_message_is_helpful(self):
        """Preview error should explain why it failed."""
        preview_path = os.path.join(REPO, "superset/mcp_service/chart/tool/get_chart_preview.py")
        with open(preview_path, 'r') as f:
            content = f.read()

        # Error message should be helpful
        self.assertIn("Cannot generate ASCII preview", content,
                      "Error message should explain the issue")


if __name__ == "__main__":
    unittest.main()
