#!/usr/bin/env python3
"""
Tests for airflow-external-link-security task.

This task verifies the fix for apache/airflow#64772:
- Fix external link target attribute (target="blank" -> target="_blank")
- Add rel="noopener noreferrer" for security
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/airflow")
UI_DIR = REPO / "airflow-core" / "src" / "airflow" / "ui"
TARGET_FILE = UI_DIR / "src" / "pages" / "Connections" / "NothingFoundInfo.tsx"


def test_link_has_correct_target_attribute():
    """
    Verify the Link component uses target="_blank" (not target="blank").

    The original code had target="blank" which is incorrect HTML -
    it should be target="_blank" to open links in a new tab.
    (fail_to_pass)
    """
    content = TARGET_FILE.read_text()

    # Check that the Link component has the correct target="_blank"
    # The pattern should match: <Link ... target="_blank" ...>
    link_pattern = r'<Link[^>]*\starget="_blank"[^>]*>'

    assert re.search(link_pattern, content), (
        f"Link component should have target=\"_blank\" but found incorrect target attribute. "
        f"The attribute target=\"blank\" (without underscore) is invalid HTML."
    )

    # Also verify the incorrect pattern is NOT present
    incorrect_pattern = r'<Link[^>]*\starget="blank"[^>]*>'
    assert not re.search(incorrect_pattern, content), (
        "Found incorrect target=\"blank\" (missing underscore). "
        "Should be target=\"_blank\"."
    )


def test_link_has_rel_noopener_noreferrer():
    """
    Verify the Link component has rel="noopener noreferrer" for security.

    External links opening in new tabs should have rel="noopener noreferrer"
    to prevent the opened page from accessing window.opener.
    (fail_to_pass)
    """
    content = TARGET_FILE.read_text()

    # Check for rel="noopener noreferrer" on the Link
    rel_pattern = r'<Link[^>]*\srel="noopener noreferrer"[^>]*>'

    assert re.search(rel_pattern, content), (
        "Link component should have rel=\"noopener noreferrer\" for security. "
        "This prevents the opened page from accessing window.opener."
    )


def test_link_attributes_combined():
    """
    Verify both security attributes are present on the same Link element.

    Tests multiple variations of link attribute values.
    (fail_to_pass)
    """
    content = TARGET_FILE.read_text()

    # Find all Link elements in the file
    link_elements = re.findall(r'<Link[^>]+>', content)

    assert len(link_elements) > 0, "No Link elements found in the component"

    # Find the Link with href={docsLink}
    docs_link = None
    for link in link_elements:
        if 'docsLink' in link or 'href=' in link:
            docs_link = link
            break

    assert docs_link is not None, "Could not find the external documentation Link"

    # Check both attributes are on this link
    assert 'target="_blank"' in docs_link, (
        f"External link missing target=\"_blank\": {docs_link}"
    )
    assert 'rel="noopener noreferrer"' in docs_link, (
        f"External link missing rel=\"noopener noreferrer\": {docs_link}"
    )


def test_lint_passes():
    """
    Verify lint (ESLint + TypeScript) passes.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Lint should pass (eslint + tsc)
    assert result.returncode == 0, (
        f"Lint failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_repo_unit_tests():
    """
    Run Airflow UI unit tests via vitest.

    The CI workflow runs 'pnpm test' which executes vitest.
    This ensures existing UI functionality is not broken.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "run", "test"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=600
    )

    assert result.returncode == 0, (
        f"Unit tests failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_repo_format_check():
    """
    Verify code formatting with Prettier.

    The codebase uses Prettier for consistent formatting.
    This ensures the fix follows the project's style guidelines.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "."],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Formatting check failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
    )


def test_component_file_exists():
    """
    Verify the target component file exists.
    (pass_to_pass)
    """
    assert TARGET_FILE.exists(), f"Component file not found: {TARGET_FILE}"
    content = TARGET_FILE.read_text()
    assert len(content) > 100, "Component file appears to be empty or too small"
    assert "NothingFoundInfo" in content, "Component name not found in file"
