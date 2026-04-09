"""
Task: maui-maps-add-packaged-readme
Repo: dotnet/maui @ 1789d47932dd78983d7c68101f154f372f60e151
PR:   33196

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/maui"
CSPROJ = Path(f"{REPO}/src/Controls/Maps/src/Controls.Maps.csproj")
README = Path(f"{REPO}/src/Controls/Maps/README.md")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_csproj_xml_valid():
    """Controls.Maps.csproj must be valid XML after modifications."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()
    assert root.tag == "Project", f"Root element should be Project, got {root.tag}"


# [static] pass_to_pass
def test_csproj_existing_properties_intact():
    """Existing csproj properties (PackageId, Description) must be preserved."""
    content = CSPROJ.read_text()
    assert "Microsoft.Maui.Controls.Maps" in content, "PackageId must be preserved"
    assert "Maps and mapping support" in content, "Description must be preserved"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — csproj packaging tests (subprocess)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_csproj_references_readme():
    """csproj must declare PackageReadmeFile element pointing to README.md."""
    r = _run_py("""
import xml.etree.ElementTree as ET

tree = ET.parse('/workspace/maui/src/Controls/Maps/src/Controls.Maps.csproj')
root = tree.getroot()
found = False
for elem in root.iter():
    if 'PackageReadmeFile' in elem.tag:
        text = (elem.text or '').strip()
        assert text, 'PackageReadmeFile element exists but is empty'
        assert 'README' in text, f'PackageReadmeFile should reference README, got: {text}'
        found = True
        break
assert found, 'PackageReadmeFile element not found in csproj'
print('PASS')
""")
    assert r.returncode == 0, f"PackageReadmeFile check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_csproj_includes_readme_in_package():
    """csproj must include README.md as a None item with Pack=true for NuGet packaging."""
    r = _run_py("""
import xml.etree.ElementTree as ET

tree = ET.parse('/workspace/maui/src/Controls/Maps/src/Controls.Maps.csproj')
root = tree.getroot()
found = False
for elem in root.iter():
    if 'None' in elem.tag:
        include = elem.get('Include', '')
        pack = elem.get('Pack', '')
        if 'README' in include and pack.lower() == 'true':
            found = True
            break
assert found, 'README.md must be included as <None> item with Pack="true"'
print('PASS')
""")
    assert r.returncode == 0, f"None/Pack check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_readme_file_exists_and_substantial():
    """README.md must exist in the Maps project folder with substantial documentation."""
    r = _run_py("""
from pathlib import Path
readme = Path('/workspace/maui/src/Controls/Maps/README.md')
assert readme.exists(), 'README.md does not exist at src/Controls/Maps/README.md'
content = readme.read_text()
assert len(content.strip()) >= 500, f'README too short ({len(content)} chars), expected substantial documentation'
print('PASS')
""")
    assert r.returncode == 0, f"README existence check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_package_readme_path_resolves():
    """The None Include path in csproj must resolve to the actual README file on disk."""
    r = _run_py("""
import xml.etree.ElementTree as ET
from pathlib import Path

csproj_path = Path('/workspace/maui/src/Controls/Maps/src/Controls.Maps.csproj')
csproj_dir = csproj_path.parent
tree = ET.parse(str(csproj_path))
root = tree.getroot()

# Find the None item that packages the README
none_include = None
for elem in root.iter():
    if 'None' in elem.tag:
        include = elem.get('Include', '')
        if 'README' in include:
            none_include = include
            break
assert none_include, 'No None item referencing README found in csproj'

# Simulate $(MSBuildThisFileDirectory) resolution: strip the property, keep the relative path
# $(MSBuildThisFileDirectory)..\\README.md -> ../README.md relative to csproj dir
rel_path = none_include.replace('$(MSBuildThisFileDirectory)', '')
resolved = (csproj_dir / rel_path).resolve()
assert resolved.exists(), f'None Include path resolves to {resolved} but file does not exist'
assert resolved.name == 'README.md', f'Expected README.md, got {resolved.name}'
print('PASS')
""")
    assert r.returncode == 0, f"Path resolution check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README content tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_readme_has_install_instructions():
    """README must include package installation instructions and package name."""
    content = README.read_text()
    lower = content.lower()
    assert "get started" in lower or "install" in lower or "quickstart" in lower, \
        "README must have a get started / install section"
    assert "dotnet add package" in lower or "nuget" in lower or "package" in lower, \
        "README must mention package installation (dotnet add package / nuget)"
    assert "Microsoft.Maui.Controls.Maps" in content, \
        "README must reference the full package name"


# [pr_diff] fail_to_pass
def test_readme_documents_features():
    """README must document multiple Maps features (pins, shapes, interactions)."""
    content = README.read_text()
    lower = content.lower()
    features_found = sum(1 for kw in ["pin", "polygon", "polyline", "circle",
                                       "mapclicked", "maptype", "isshowinguser"]
                         if kw in lower)
    assert features_found >= 3, \
        f"README must document at least 3 Maps features, found {features_found}"


# [pr_diff] fail_to_pass
def test_readme_has_code_samples():
    """README must include code examples demonstrating Maps usage (XAML or C#)."""
    content = README.read_text()
    has_xaml = "maps:Map" in content or "maps:Pin" in content
    has_csharp = "UseMauiMaps" in content or "MapClickedEventArgs" in content \
                 or "MoveToRegion" in content or "MapSpan" in content
    assert has_xaml or has_csharp, \
        "README must include XAML or C# code examples for Maps usage"


# [pr_diff] fail_to_pass
def test_readme_links_to_docs():
    """README must link to Microsoft Learn documentation for Maps."""
    content = README.read_text()
    assert "learn.microsoft.com" in content, \
        "README must link to Microsoft Learn documentation"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from copilot-instructions.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — .github/copilot-instructions.md:162 @ base
def test_readme_follows_doc_patterns():
    """README follows existing code documentation patterns (section structure, examples).
    Per .github/copilot-instructions.md: 'Follow existing code documentation patterns'
    and 'Update relevant docs in docs/ folder when needed'."""
    content = README.read_text()
    assert content.strip().startswith("#"), \
        "README should start with a markdown heading"
    assert "##" in content, \
        "README should have subsections (## headings)"
    assert "UseMauiMaps" in content or "UseMaui" in content, \
        "README should show MAUI initialization pattern (UseMauiMaps)"
