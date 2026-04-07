"""
Task: maui-maps-add-packaged-readme
Repo: dotnet/maui @ 1789d47932dd78983d7c68101f154f372f60e151
PR:   33196

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/maui"
CSPROJ = Path(f"{REPO}/src/Controls/Maps/src/Controls.Maps.csproj")
README = Path(f"{REPO}/src/Controls/Maps/README.md")


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
# Fail-to-pass (pr_diff) — csproj packaging tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_csproj_references_readme():
    """csproj must declare PackageReadmeFile element pointing to README.md."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()
    found = False
    for elem in root.iter():
        if "PackageReadmeFile" in elem.tag:
            text = (elem.text or "").strip()
            assert text != "", "PackageReadmeFile element exists but is empty"
            assert "README" in text, f"PackageReadmeFile should reference README, got: {text}"
            found = True
    assert found, "PackageReadmeFile element not found in csproj"


# [pr_diff] fail_to_pass
def test_csproj_includes_readme_in_package():
    """csproj must include README.md as a None item with Pack=true for NuGet packaging."""
    tree = ET.parse(str(CSPROJ))
    root = tree.getroot()
    found = False
    for elem in root.iter():
        if "None" in elem.tag:
            include = elem.get("Include", "")
            pack = elem.get("Pack", "")
            if "README" in include and pack.lower() == "true":
                found = True
                break
    assert found, "README.md must be included as <None> item with Pack=\"true\""


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
        f"README must document at least 3 Maps features, found {features_found} (keywords: pin, polygon, polyline, circle, mapclicked, maptype, isshowinguser)"


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
    # Check structural patterns consistent with MAUI docs
    assert content.strip().startswith("#"), \
        "README should start with a markdown heading"
    assert "##" in content, \
        "README should have subsections (## headings)"
    # Must reference UseMauiMaps (the initialization API) — consistent with how
    # other MAUI docs show initialization in MauiProgram.cs
    assert "UseMauiMaps" in content or "UseMaui" in content, \
        "README should show MAUI initialization pattern (UseMauiMaps)"
