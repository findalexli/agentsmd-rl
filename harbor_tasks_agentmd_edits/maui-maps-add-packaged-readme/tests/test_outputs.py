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
# Gates (pass_to_pass, static) -- syntax / structural checks
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
# Repo CI Gates (pass_to_pass, static) -- project structure validation
# These are static checks (file reading), not subprocess commands.
# ---------------------------------------------------------------------------


# [static] pass_to_pass -- validate project references resolve
def test_repo_csproj_project_references_valid():
    """All ProjectReference paths in csproj must resolve to existing files (pass_to_pass)."""
    import os

    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()

    # Get all ProjectReference Include paths
    for elem in root.iter():
        if elem.tag.endswith("}ProjectReference") or "ProjectReference" in elem.tag:
            include_path = elem.get("Include", "")
            if include_path:
                # Convert Windows backslashes to forward slashes for cross-platform compatibility
                include_path = include_path.replace("\\", "/")
                # Resolve relative to csproj directory
                resolved = (CSPROJ.parent / include_path).resolve()
                assert resolved.exists(), f"ProjectReference does not exist: {include_path} (resolved: {resolved})"


# [static] pass_to_pass -- validate project file structure matches SDK style
def test_repo_csproj_sdk_style_structure():
    """csproj must follow SDK-style format with proper TargetFrameworks (pass_to_pass)."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()

    # Check SDK attribute on Project element
    sdk = root.get("Sdk", "")
    assert "Microsoft.NET.Sdk" in sdk, f"Project must use Microsoft.NET.Sdk, got: {sdk}"

    # Check required PropertyGroup elements exist
    found_tf = False
    found_assembly = False
    found_package = False

    for prop_group in root.iter():
        if prop_group.tag.endswith("}PropertyGroup") or "PropertyGroup" in prop_group.tag:
            for child in prop_group:
                tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag_name == "TargetFrameworks":
                    found_tf = True
                if tag_name == "AssemblyName":
                    found_assembly = True
                if tag_name == "PackageId":
                    found_package = True

    assert found_tf, "csproj must have TargetFrameworks defined"
    assert found_assembly, "csproj must have AssemblyName defined"
    assert found_package, "csproj must have PackageId defined"


# [static] pass_to_pass -- validate no duplicate item includes
def test_repo_csproj_no_duplicate_includes():
    """csproj must not have duplicate Include entries for the same file (pass_to_pass)."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()

    includes = {}
    for elem in root.iter():
        include_val = elem.get("Include", "")
        if include_val:
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            key = f"{tag_name}:{include_val}"
            assert key not in includes, f"Duplicate Include found: {tag_name}='{include_val}'"
            includes[key] = True


# [static] pass_to_pass -- validate PublicAPI files exist for all target platforms
def test_repo_public_api_files_complete():
    """PublicAPI.Shipped.txt and PublicAPI.Unshipped.txt must exist for all target frameworks (pass_to_pass)."""
    public_api_dir = CSPROJ.parent / "PublicAPI"
    assert public_api_dir.exists(), f"PublicAPI directory does not exist: {public_api_dir}"

    # Expected target framework directories based on csproj TargetFrameworks
    expected_platforms = ["net", "net-android", "net-ios", "net-maccatalyst", "net-tizen", "net-windows", "netstandard"]

    for platform in expected_platforms:
        platform_dir = public_api_dir / platform
        assert platform_dir.exists(), f"PublicAPI platform directory missing: {platform}"

        shipped = platform_dir / "PublicAPI.Shipped.txt"
        unshipped = platform_dir / "PublicAPI.Unshipped.txt"

        assert shipped.exists(), f"PublicAPI.Shipped.txt missing for {platform}"
        assert unshipped.exists(), f"PublicAPI.Unshipped.txt missing for {platform}"

        # Validate files have expected header format
        shipped_content = shipped.read_text()
        unshipped_content = unshipped.read_text()
        assert shipped_content.startswith("#nullable enable"), f"PublicAPI.Shipped.txt for {platform} missing #nullable enable header"


# [static] pass_to_pass -- validate csproj package metadata for NuGet compliance
def test_repo_csproj_package_metadata():
    """csproj must have required NuGet package metadata (IsPackable, PackageId, PackageTags) (pass_to_pass)."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()

    found_is_packable = False
    found_package_id = False
    found_package_tags = False
    found_description = False

    for prop_group in root.iter():
        if prop_group.tag.endswith("}PropertyGroup") or "PropertyGroup" in prop_group.tag:
            for child in prop_group:
                tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag_name == "IsPackable":
                    found_is_packable = True
                    text = (child.text or "").strip()
                    assert text.lower() == "true", f"IsPackable must be 'true', got: {text}"
                if tag_name == "PackageId":
                    found_package_id = True
                    assert "Microsoft.Maui" in (child.text or ""), f"PackageId should be Microsoft.Maui.*, got: {child.text}"
                if tag_name == "PackageTags":
                    found_package_tags = True
                    tags = child.text or ""
                    assert "maps" in tags.lower(), f"PackageTags should include 'maps', got: {tags}"
                if tag_name == "Description":
                    found_description = True
                    desc = child.text or ""
                    assert len(desc) > 10, f"Description too short: {desc}"

    assert found_is_packable, "csproj must have IsPackable set to true"
    assert found_package_id, "csproj must have PackageId defined"
    assert found_package_tags, "csproj must have PackageTags defined"
    assert found_description, "csproj must have Description defined"


# [static] pass_to_pass -- validate project file naming conventions
def test_repo_csproj_file_naming():
    """csproj file name must match expected pattern Controls.Maps.csproj (pass_to_pass)."""
    assert CSPROJ.name == "Controls.Maps.csproj", f"csproj file name mismatch: expected Controls.Maps.csproj, got {CSPROJ.name}"
    assert CSPROJ.exists(), f"csproj file does not exist: {CSPROJ}"


# ---------------------------------------------------------------------------
# Repo CI Gates (pass_to_pass, repo_tests) -- git-based validation
# These use subprocess.run() with actual git commands.
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass -- validate csproj file is tracked by git
def test_repo_csproj_tracked_by_git():
    """csproj file must be tracked by git (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", "src/Controls/Maps/src/Controls.Maps.csproj"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    assert r.stdout.strip(), "csproj file not tracked by git"


# [repo_tests] pass_to_pass -- validate git status is clean on base commit
def test_repo_git_status_clean():
    """Repo must have clean git status at base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Allow untracked files but no modified/staged changes at base commit
    modified_or_staged = [line for line in r.stdout.splitlines() if line and not line.startswith("?")]
    assert not modified_or_staged, f"Repo has unexpected modifications: {modified_or_staged}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- csproj packaging tests (subprocess)
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
# $(MSBuildThisFileDirectory)..\\\\README.md -> ../README.md relative to csproj dir
rel_path = none_include.replace('$(MSBuildThisFileDirectory)', '')
# Convert Windows backslashes to forward slashes for cross-platform compatibility
rel_path = rel_path.replace('\\\\', '/')
resolved = (csproj_dir / rel_path).resolve()
assert resolved.exists(), f'None Include path resolves to {resolved} but file does not exist'
assert resolved.name == 'README.md', f'Expected README.md, got {resolved.name}'
print('PASS')
""")
    assert r.returncode == 0, f"Path resolution check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- README content tests
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
# Config-derived (agent_config) -- rules from copilot-instructions.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass -- .github/copilot-instructions.md:162 @ base
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
