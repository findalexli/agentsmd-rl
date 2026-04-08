"""
Task: runtime-add-cdacslnx-solution-file-for
Repo: dotnet/runtime @ 0f8072851a62a1e1cbb90f0372a20961ce8991f0
PR:   125614

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/runtime"
CDAC = Path(REPO) / "src" / "native" / "managed" / "cdac"
SLNX = CDAC / "cdac.slnx"
README = CDAC / "README.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioural: solution file is valid XML and
# every referenced .csproj actually exists on disk
# ---------------------------------------------------------------------------

def test_slnx_valid_and_projects_resolve():
    """cdac.slnx must be valid XML and every Project path must resolve to a real file."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET, sys, pathlib

cdac = pathlib.Path("/workspace/runtime/src/native/managed/cdac")
slnx = cdac / "cdac.slnx"
if not slnx.exists():
    print(f"FAIL: {slnx} does not exist")
    sys.exit(1)

tree = ET.parse(slnx)
root = tree.getroot()
if root.tag != "Solution":
    print(f"FAIL: root element is '{root.tag}', expected 'Solution'")
    sys.exit(1)

projects = [p.get("Path") for p in root.iter("Project")]
if not projects:
    print("FAIL: no <Project> elements found")
    sys.exit(1)

missing = []
for p in projects:
    full = cdac / p
    if not full.exists():
        missing.append(p)

if missing:
    print(f"FAIL: projects not found on disk: {missing}")
    sys.exit(1)

print(f"PASS: {len(projects)} projects, all resolve")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioural: solution includes Legacy and
# DumpTests projects (both missing from old README template)
# ---------------------------------------------------------------------------

def test_slnx_includes_legacy_and_dumptests():
    """Solution must include Legacy library and DumpTests (both missing from old template)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET, sys, pathlib

cdac = pathlib.Path("/workspace/runtime/src/native/managed/cdac")
slnx = cdac / "cdac.slnx"
if not slnx.exists():
    print("FAIL: cdac.slnx does not exist")
    sys.exit(1)

tree = ET.parse(slnx)
paths = [p.get("Path") for p in tree.getroot().iter("Project")]

# These two were missing from the old manually-created template
required = {
    "Legacy": "Microsoft.Diagnostics.DataContractReader.Legacy/Microsoft.Diagnostics.DataContractReader.Legacy.csproj",
    "DumpTests": "tests/DumpTests/Microsoft.Diagnostics.DataContractReader.DumpTests.csproj",
}

missing = []
for label, expected in required.items():
    if expected not in paths:
        missing.append(label)

if missing:
    print(f"FAIL: solution missing projects: {missing}")
    sys.exit(1)

# Verify these projects actually exist on disk
for label, rel in required.items():
    full = cdac / rel
    if not full.exists():
        print(f"FAIL: {label} csproj not found on disk at {full}")
        sys.exit(1)

print(f"PASS: Legacy and DumpTests both present and resolve")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioural: solution organises into library
# and test folders, and paths are relative (not repo-root)
# ---------------------------------------------------------------------------

def test_slnx_folder_organisation():
    """Solution must have separate Folder elements for libraries and tests, with relative paths."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET, sys, pathlib

slnx = pathlib.Path("/workspace/runtime/src/native/managed/cdac/cdac.slnx")
if not slnx.exists():
    print("FAIL: cdac.slnx does not exist")
    sys.exit(1)

tree = ET.parse(slnx)
root = tree.getroot()

folders = {f.get("Name"): f for f in root.findall("Folder")}
if len(folders) < 2:
    print(f"FAIL: expected >=2 Folder elements, got {len(folders)}")
    sys.exit(1)

# Check test folder exists
test_folder = None
for name, f in folders.items():
    if "test" in name.lower():
        test_folder = f
        break
if test_folder is None:
    print("FAIL: no folder with 'test' in its name")
    sys.exit(1)

# Check all project paths are relative (not starting with src/)
for proj in root.iter("Project"):
    path = proj.get("Path", "")
    if path.startswith("src/"):
        print(f"FAIL: path '{path}' is repo-root-relative, must be relative to cdac dir")
        sys.exit(1)
    if ".csproj" not in path:
        print(f"FAIL: path '{path}' does not reference a .csproj")
        sys.exit(1)

print("PASS: folder organisation and relative paths OK")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README no longer has manual setup instructions
# ---------------------------------------------------------------------------

def test_readme_no_manual_slnx_setup():
    """README must not contain the old manual 'Setting up a solution' section."""
    content = README.read_text()
    assert "### Setting up a solution" not in content, \
        "README still has the old manual setup section"
    assert "create a file `cdac.slnx` in the runtime repo root" not in content, \
        "README still instructs manual creation of cdac.slnx"


def test_readme_references_checked_in_file():
    """README must reference the checked-in cdac.slnx file."""
    content = README.read_text()
    assert "cdac.slnx" in content, \
        "README does not mention cdac.slnx at all"
    assert "Opening the solution" in content or "opening the solution" in content, \
        "README missing 'Opening the solution' heading"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — copilot-instructions.md: no trailing whitespace
# ---------------------------------------------------------------------------

def test_no_trailing_whitespace_in_readme():
    """Markdown files must have no trailing whitespace (copilot-instructions.md line 40)."""
    for i, line in enumerate(README.read_text().splitlines(), 1):
        assert line == line.rstrip(), \
            f"README.md line {i} has trailing whitespace"


def test_no_trailing_whitespace_in_slnx():
    """cdac.slnx should have no trailing whitespace."""
    if not SLNX.exists():
        return  # slnx existence is checked by other tests
    for i, line in enumerate(SLNX.read_text().splitlines(), 1):
        assert line == line.rstrip(), \
            f"cdac.slnx line {i} has trailing whitespace"
