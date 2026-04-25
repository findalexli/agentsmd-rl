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

    # Extract the Link element that has href={docsLink}
    # Parse through the source to find the specific Link element
    link_pattern = r'<Link\s+([^>]+)>'
    matches = list(re.finditer(link_pattern, content))

    docs_link = None
    for match in matches:
        attrs = match.group(1)
        # Find the Link that has href={docsLink}
        if 'href={docsLink}' in attrs or 'href={ docsLink }' in attrs:
            docs_link = match.group(0)
            break

    assert docs_link is not None, (
        "Could not find Link element with href={docsLink} in the component"
    )

    # Extract and verify the target attribute value
    target_match = re.search(r'target="([^"]+)"', docs_link)
    assert target_match, (
        "Link with href={docsLink} is missing target attribute. "
        f"Found: {docs_link}"
    )

    target_value = target_match.group(1)
    assert target_value == "_blank", (
        f"Link target should be \"_blank\" (with underscore) but got \"{target_value}\". "
        "Target \"blank\" without underscore is invalid HTML."
    )


def test_link_has_rel_noopener_noreferrer():
    """
    Verify the Link component has rel attribute with both noopener and noreferrer.

    External links opening in new tabs should have rel="noopener noreferrer"
    to prevent the opened page from accessing window.opener.
    The order of noopener and noreferrer in HTML does not matter -
    both are valid as "noopener noreferrer" or "noreferrer noopener".
    (fail_to_pass)
    """
    content = TARGET_FILE.read_text()

    # Find the Link element with href={docsLink}
    link_pattern = r'<Link\s+([^>]+)>'
    matches = list(re.finditer(link_pattern, content))

    docs_link = None
    for match in matches:
        attrs = match.group(1)
        if 'href={docsLink}' in attrs or 'href={ docsLink }' in attrs:
            docs_link = match.group(0)
            break

    assert docs_link is not None, (
        "Could not find Link element with href={docsLink} in the component"
    )

    # Extract and parse the rel attribute
    # HTML allows noopener and noreferrer in any order
    rel_match = re.search(r'rel="([^"]+)"', docs_link)
    assert rel_match, (
        "Link with href={docsLink} is missing rel attribute. "
        "External links opening in new tabs need rel=\"noopener noreferrer\" for security. "
        f"Found: {docs_link}"
    )

    rel_value = rel_match.group(1)
    rel_tokens = set(rel_value.split())

    # Both noopener and noreferrer must be present (order doesn't matter)
    assert "noopener" in rel_tokens and "noreferrer" in rel_tokens, (
        f"Link rel attribute should contain both \"noopener\" and \"noreferrer\". "
        f"Got rel=\"{rel_value}\"."
    )


def test_link_attributes_combined():
    """
    Verify both security attributes are present on the same Link element.

    The external documentation link should have:
    - target="_blank" (to open in new tab)
    - rel with both "noopener" and "noreferrer" (for security)
    (fail_to_pass)
    """
    content = TARGET_FILE.read_text()

    # Find the Link element with href={docsLink}
    link_pattern = r'<Link\s+([^>]+)>'
    matches = list(re.finditer(link_pattern, content))

    docs_link = None
    for match in matches:
        attrs = match.group(1)
        if 'href={docsLink}' in attrs or 'href={ docsLink }' in attrs:
            docs_link = match.group(0)
            break

    assert docs_link is not None, (
        "Could not find Link element with href={docsLink} in the component"
    )

    # Verify target attribute is _blank
    target_match = re.search(r'target="([^"]+)"', docs_link)
    assert target_match, (
        f"External link is missing target attribute. "
        f"Link should open in new tab with target=\"_blank\". "
        f"Found: {docs_link}"
    )
    assert target_match.group(1) == "_blank", (
        f"External link target should be \"_blank\" but got \"{target_match.group(1)}\". "
        f"Found: {docs_link}"
    )

    # Verify rel attribute has both security tokens
    rel_match = re.search(r'rel="([^"]+)"', docs_link)
    assert rel_match, (
        f"External link is missing rel attribute. "
        f"Link needs rel=\"noopener noreferrer\" for security. "
        f"Found: {docs_link}"
    )

    rel_tokens = set(rel_match.group(1).split())
    assert "noopener" in rel_tokens and "noreferrer" in rel_tokens, (
        f"External link rel should contain both \"noopener\" and \"noreferrer\". "
        f"Got rel=\"{rel_match.group(1)}\". "
        f"Found: {docs_link}"
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
