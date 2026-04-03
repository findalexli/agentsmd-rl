"""
Task: runtime-add-cdacslnx-solution-file-for
Repo: dotnet/runtime @ 0f8072851a62a1e1cbb90f0372a20961ce8991f0
PR:   125614

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/runtime"
CDAC = Path(REPO) / "src" / "native" / "managed" / "cdac"
SLNX = CDAC / "cdac.slnx"
README = CDAC / "README.md"

# The five library projects that must be in the solution
LIBRARY_PROJECTS = [
    "Microsoft.Diagnostics.DataContractReader.Abstractions",
    "Microsoft.Diagnostics.DataContractReader.Contracts",
    "Microsoft.Diagnostics.DataContractReader",
    "Microsoft.Diagnostics.DataContractReader.Legacy",
    "mscordaccore_universal",
]

# The two test projects that must be in the solution
TEST_PROJECTS = [
    "Microsoft.Diagnostics.DataContractReader.Tests",
    "Microsoft.Diagnostics.DataContractReader.DumpTests",
]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — solution file exists and is valid
# ---------------------------------------------------------------------------

def test_slnx_valid_xml():
    """The cdac.slnx file must exist and be valid XML with a Solution root."""
    assert SLNX.exists(), f"Solution file not found at {SLNX}"
    tree = ET.parse(SLNX)
    root = tree.getroot()
    assert root.tag == "Solution", f"Root element should be 'Solution', got '{root.tag}'"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — solution file content
# ---------------------------------------------------------------------------

def test_slnx_includes_all_library_projects():
    """Solution must include all five cDAC library projects."""
    content = SLNX.read_text()
    for proj in LIBRARY_PROJECTS:
        assert proj in content, \
            f"Solution file missing library project: {proj}"


def test_slnx_includes_legacy_project():
    """Solution must include the Legacy project (missing from old README template)."""
    content = SLNX.read_text()
    assert "Legacy" in content, \
        "Solution must include Microsoft.Diagnostics.DataContractReader.Legacy"
    assert ".Legacy/" in content or "Legacy\\" in content, \
        "Legacy project path must reference the Legacy subdirectory"


def test_slnx_includes_both_test_projects():
    """Solution must include both test projects (unit tests and dump tests)."""
    content = SLNX.read_text()
    for proj in TEST_PROJECTS:
        assert proj in content, \
            f"Solution file missing test project: {proj}"


def test_slnx_uses_relative_paths():
    """Project paths in cdac.slnx must be relative to the cdac directory, not repo root."""
    tree = ET.parse(SLNX)
    root = tree.getroot()
    for project in root.iter("Project"):
        path = project.get("Path", "")
        assert not path.startswith("src/"), \
            f"Project path '{path}' uses repo-root-relative path; should be relative to cdac dir"
        assert ".csproj" in path, \
            f"Project path '{path}' doesn't reference a .csproj file"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README.md update
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — copilot-instructions.md rule
# ---------------------------------------------------------------------------

