"""
Test suite for verifying the MCP dashboard draft state fix.
"""

import sys
import os
import subprocess
import re
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

# Path to the schema file
SCHEMA_FILE = Path("/workspace/superset/superset/mcp_service/dashboard/schemas.py")


def get_published_default_from_source():
    """Parse the schema file to get the published field default value."""
    content = SCHEMA_FILE.read_text()
    
    # Pattern to find published: bool = Field(default=X, ...)
    pattern = r"published:\s*bool\s*=\s*Field\s*\([^)]*default=(True|False)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1) == "True"
    
    raise ValueError("Could not find published field default in schema file")


# Create a minimal Pydantic model that mirrors the actual GenerateDashboardRequest
class MinimalGenerateDashboardRequest(BaseModel):
    """Minimal replica of GenerateDashboardRequest for testing."""
    chart_ids: list[int] = Field(..., description="List of chart IDs", min_length=1)
    dashboard_title: str | None = Field(None, description="Title for the dashboard")
    description: str | None = Field(None, description="Description for the dashboard")
    published: bool = Field(
        default=get_published_default_from_source(),
        description="Whether to publish the dashboard"
    )


def test_generate_dashboard_request_defaults_to_draft():
    """Fail-to-pass test: Verify that GenerateDashboardRequest defaults to published=False."""
    request = MinimalGenerateDashboardRequest(
        chart_ids=[1],
        dashboard_title="Test Dashboard"
    )
    assert request.published is False, (
        f"Expected published to default to False (draft), but got {request.published}."
    )


def test_generate_dashboard_request_explicit_published_true():
    """Pass-to-pass test: Verify that explicit published=True still works."""
    request = MinimalGenerateDashboardRequest(
        chart_ids=[1],
        dashboard_title="Test Dashboard",
        published=True
    )
    assert request.published is True


def test_generate_dashboard_request_explicit_published_false():
    """Pass-to-pass test: Verify that explicit published=False works."""
    request = MinimalGenerateDashboardRequest(
        chart_ids=[1],
        dashboard_title="Test Dashboard",
        published=False
    )
    assert request.published is False


def test_generate_dashboard_request_multiple_chart_ids():
    """Fail-to-pass test: Verify default draft behavior with multiple chart IDs."""
    test_cases = [
        ([1, 2, 3], "Multi Chart Dashboard"),
        ([42], "Single Chart Dashboard"),
        ([100, 200, 300, 400], "Many Charts Dashboard"),
    ]

    for chart_ids, title in test_cases:
        request = MinimalGenerateDashboardRequest(
            chart_ids=chart_ids,
            dashboard_title=title
        )
        assert request.published is False


def test_schema_field_configuration():
    """Structural verification: Verify the Field configuration is correct."""
    field_info = MinimalGenerateDashboardRequest.model_fields.get("published")
    assert field_info is not None
    assert field_info.default is False
    assert "publish" in field_info.description.lower()


def test_source_file_has_correct_default():
    """Direct source verification: Check that the source file has default=False."""
    default_value = get_published_default_from_source()
    assert default_value is False


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD tests
# =============================================================================

REPO_ROOT = Path("/workspace/superset")


def _check_import_works():
    """Check if we can import superset without errors."""
    try:
        import superset
        return True
    except ImportError as e:
        return False


def test_repo_mcp_dashboard_schemas():
    """Pass-to-pass test: Run the repo's MCP dashboard schema unit tests."""
    # Check if we can import superset
    if not _check_import_works():
        pytest.skip("Superset dependencies not fully installed, skipping repo tests")
    
    test_file = REPO_ROOT / "tests/unit_tests/mcp_service/dashboard/test_dashboard_schemas.py"
    if not test_file.exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    r = subprocess.run(
        ["pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"MCP dashboard schema tests failed: {r.stderr[-500:]}"


def test_repo_mcp_dashboard_generation():
    """Pass-to-pass test: Run the repo's MCP dashboard generation tool tests."""
    # Check if we can import superset
    if not _check_import_works():
        pytest.skip("Superset dependencies not fully installed, skipping repo tests")
    
    test_file = REPO_ROOT / "tests/unit_tests/mcp_service/dashboard/tool/test_dashboard_generation.py"
    if not test_file.exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    r = subprocess.run(
        ["pytest", str(test_file), "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"MCP dashboard generation tests failed: {r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
