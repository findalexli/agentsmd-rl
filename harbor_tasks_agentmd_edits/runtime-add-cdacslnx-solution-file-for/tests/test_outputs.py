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

test_folder = None
for name, f in folders.items():
    if "test" in name.lower():
        test_folder = f
        break
if test_folder is None:
    print("FAIL: no folder with 'test' in its name")
    sys.exit(1)

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


def test_no_trailing_whitespace_in_readme():
    """Markdown files must have no trailing whitespace (copilot-instructions.md line 40)."""
    for i, line in enumerate(README.read_text().splitlines(), 1):
        assert line == line.rstrip(), \
            f"README.md line {i} has trailing whitespace"


def test_no_trailing_whitespace_in_slnx():
    """cdac.slnx should have no trailing whitespace."""
    if not SLNX.exists():
        return
    for i, line in enumerate(SLNX.read_text().splitlines(), 1):
        assert line == line.rstrip(), \
            f"cdac.slnx line {i} has trailing whitespace"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI tests that exercise repo tooling
# ---------------------------------------------------------------------------

def test_repo_slnx_schema():
    """cdac.slnx follows expected solution file schema (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
import pathlib

slnx = pathlib.Path('/workspace/runtime/src/native/managed/cdac/cdac.slnx')
if not slnx.exists():
    print('SKIP: cdac.slnx does not exist yet')
    sys.exit(0)

try:
    tree = ET.parse(slnx)
    root = tree.getroot()
except ET.ParseError as e:
    print(f'FAIL: Invalid XML: {e}')
    sys.exit(1)

if root.tag != 'Solution':
    print(f"FAIL: Root element is '{root.tag}', expected 'Solution'")
    sys.exit(1)

configs = root.find('Configurations')
if configs is None:
    print('FAIL: Missing Configurations element')
    sys.exit(1)

platforms = configs.findall('Platform')
if len(platforms) == 0:
    print('FAIL: No Platform elements found in Configurations')
    sys.exit(1)

folders = root.findall('Folder')
if len(folders) == 0:
    print('FAIL: No Folder elements found')
    sys.exit(1)

projects = list(root.iter('Project'))
if len(projects) == 0:
    print('FAIL: No Project elements found')
    sys.exit(1)

print(f'PASS: Valid slnx with {len(folders)} folders, {len(projects)} projects, {len(platforms)} platforms')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"slnx schema validation failed:\n{r.stdout}{r.stderr}"


def test_repo_csproj_exist():
    """All .csproj files referenced in slnx exist and are valid MSBuild XML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
import pathlib

cdac = pathlib.Path('/workspace/runtime/src/native/managed/cdac')
slnx = cdac / 'cdac.slnx'

if not slnx.exists():
    print('SKIP: cdac.slnx does not exist yet')
    sys.exit(0)

try:
    tree = ET.parse(slnx)
    root = tree.getroot()
except ET.ParseError as e:
    print(f'FAIL: Invalid slnx XML: {e}')
    sys.exit(1)

project_paths = [p.get('Path') for p in root.iter('Project') if p.get('Path')]
if not project_paths:
    print('FAIL: No Project paths found in slnx')
    sys.exit(1)

missing = []
invalid_xml = []
for rel_path in project_paths:
    full_path = cdac / rel_path
    if not full_path.exists():
        missing.append(rel_path)
        continue
    try:
        ET.parse(full_path)
    except ET.ParseError as e:
        invalid_xml.append(f'{rel_path}: {e}')

if missing:
    print(f'FAIL: Missing csproj files: {missing}')
    sys.exit(1)

if invalid_xml:
    print(f'FAIL: Invalid csproj XML: {invalid_xml}')
    sys.exit(1)

print(f'PASS: All {len(project_paths)} csproj files exist and are valid XML')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"csproj validation failed:\n{r.stdout}{r.stderr}"


def test_repo_readme_structure():
    """README.md has expected structure with proper headings (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
import pathlib

readme = pathlib.Path('/workspace/runtime/src/native/managed/cdac/README.md')
if not readme.exists():
    print('FAIL: README.md does not exist')
    sys.exit(1)

content = readme.read_text()

required_sections = ['# cDAC', '## Architecture', '## Project structure']
missing = []
for section in required_sections:
    if section not in content:
        missing.append(section)

if missing:
    print(f'FAIL: Missing required sections: {missing}')
    sys.exit(1)

lines = content.splitlines()
has_h1 = any(line.startswith('# ') for line in lines)
if not has_h1:
    print('FAIL: No H1 heading found')
    sys.exit(1)

backticks = content.count('```')
if backticks % 2 != 0:
    print('FAIL: Unmatched code block backticks')
    sys.exit(1)

print('PASS: README.md has valid structure')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"README structure validation failed:\n{r.stdout}{r.stderr}"
