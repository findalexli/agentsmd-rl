"""
Task: tuist-fixcli-prevent-xcstrings-stale-extraction
Repo: tuist/tuist @ 48207131f1e248413d59a0dab0044fd3c2dbb48a
PR:   9907

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/tuist"
MAPPER_FILE = Path(REPO) / "cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift"
EXAMPLE_DIR = Path(REPO) / "examples/xcode/generated_ios_app_with_static_framework_with_xcstrings"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified Swift file exists and has balanced braces."""
    content = MAPPER_FILE.read_text()
    assert len(content) > 100, "ResourcesProjectMapper.swift is too short or empty"
    assert content.count("{") == content.count("}"), \
        "Unbalanced braces in ResourcesProjectMapper.swift"


def test_xcassets_still_code_generating():
    """xcassets must still be in codeGeneratingResourceExtensions."""
    content = MAPPER_FILE.read_text()
    match = re.search(
        r'let\s+codeGeneratingResourceExtensions[^=]*=\s*\[([^\]]*)\]', content
    )
    assert match, "Could not find codeGeneratingResourceExtensions definition"
    extensions_value = match.group(1)
    assert "xcassets" in extensions_value, \
        "xcassets should still be in codeGeneratingResourceExtensions"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_xcstrings_not_in_code_generating_extensions():
    """codeGeneratingResourceExtensions must NOT contain xcstrings.

    On the base commit the set is ["xcassets", "xcstrings"]. After the fix,
    xcstrings must be removed so Xcode does not add them to the Sources build
    phase, which triggers stale string extraction.
    """
    content = MAPPER_FILE.read_text()
    match = re.search(
        r'let\s+codeGeneratingResourceExtensions[^=]*=\s*\[([^\]]*)\]', content
    )
    assert match, "Could not find codeGeneratingResourceExtensions definition"
    extensions_value = match.group(1)
    assert "xcstrings" not in extensions_value, \
        "xcstrings should NOT be in codeGeneratingResourceExtensions — " \
        "adding xcstrings to the Sources phase causes Xcode to mark strings as stale"



    On the base commit the line is: modifiedTarget.resources.resources = []
    After the fix, xcstrings must be preserved (e.g. via a filter) so Xcode's
    string catalog editor can associate string references with the catalog.
    """
    content = MAPPER_FILE.read_text()
    lines = [line.strip() for line in content.split("\n")]

    # The base commit has exactly: modifiedTarget.resources.resources = []
    # A valid fix must either remove this line or replace it with something
    # that retains xcstrings.
    if "modifiedTarget.resources.resources = []" in lines:
        raise AssertionError(
            "modifiedTarget.resources.resources is set to [] — "
            "xcstrings files should be retained in the main target resources"
        )

    # Verify there is SOME assignment to modifiedTarget.resources.resources
    # that references xcstrings filtering/retention
    has_resource_assignment = any(
        "modifiedTarget.resources.resources" in line and "=" in line
        for line in lines
    )
    assert has_resource_assignment, \
        "Expected an assignment to modifiedTarget.resources.resources " \
        "that retains xcstrings"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README for new example fixture
# ---------------------------------------------------------------------------


    The README should explain that this example demonstrates an iOS app with
    a static framework that uses xcstrings (string catalogs) and that it
    verifies Xcode does not mark strings as stale during build.
    """
    readme_path = EXAMPLE_DIR / "README.md"
    assert readme_path.exists(), \
        f"README.md missing at {readme_path}"
    content = readme_path.read_text().lower()

    assert "xcstrings" in content or "string catalog" in content, \
        "README should mention xcstrings or string catalogs"
    assert "static" in content, \
        "README should mention the static framework context"
    assert ("stale" in content or "companion" in content
            or "bundle" in content or "resource" in content), \
        "README should explain the stale extraction or companion bundle scenario"
