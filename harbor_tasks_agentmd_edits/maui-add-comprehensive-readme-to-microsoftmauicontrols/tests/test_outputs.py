"""
Task: maui-add-comprehensive-readme-to-microsoftmauicontrols
Repo: dotnet/maui @ d2e5dfa5d0b19e4c306e9f4cef62f72c845ef726
PR:   32835

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

REPO = "/workspace/maui"
CSPROJ = REPO + "/src/Controls/src/NuGet/Controls.NuGet.csproj"
README = REPO + "/src/Controls/src/NuGet/README.md"


def _run_py(code, timeout=15):
    """Run a Python snippet via subprocess, return CompletedProcess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_file_exists():
    """README.md must exist at src/Controls/src/NuGet/README.md."""
    r = subprocess.run(
        ["python3", "-c",
         'from pathlib import Path; '
         'p = Path("' + README + '"); '
         'assert p.exists(), "README.md not found"; '
         'assert p.stat().st_size > 0, "README.md is empty"; '
         'print("PASS")'],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, "README check failed: " + r.stderr
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_csproj_package_readme_property():
    """Controls.NuGet.csproj must declare <PackageReadmeFile>README.md</PackageReadmeFile>."""
    tree = ET.parse(CSPROJ)
    root = tree.getroot()
    found = False
    for pg in root.iter():
        tag = pg.tag.split('}')[-1] if '}' in pg.tag else pg.tag
        if tag == 'PropertyGroup':
            for child in pg:
                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if child_tag == 'PackageReadmeFile' and child.text and 'README.md' in child.text:
                    found = True
                    break
        if found:
            break
    assert found, "PackageReadmeFile element not found"


# [pr_diff] fail_to_pass
def test_csproj_packs_readme():
    """Controls.NuGet.csproj must include README.md in the NuGet package via <None> item."""
    tree = ET.parse(CSPROJ)
    root = tree.getroot()
    found = False
    for none_elem in root.iter():
        tag = none_elem.tag.split('}')[-1] if '}' in none_elem.tag else none_elem.tag
        if tag == 'None':
            include = none_elem.get('Include', '')
            if 'README.md' in include:
                pack = none_elem.get('Pack', '')
                assert pack.lower() == 'true', 'Pack attr not true'
                found = True
                break
    assert found, 'No None element for README.md found'


# [pr_diff] fail_to_pass
def test_readme_has_required_sections():
    """README.md must contain key sections: title, getting started, supported platforms."""
    content = Path(README).read_text()
    required = ['.NET MAUI', 'Getting Started', 'Supported Platforms', 'Microsoft.Maui.Controls', 'NuGet']
    missing = [p for p in required if p not in content]
    assert not missing, f'Missing sections: {missing}'


# [pr_diff] fail_to_pass
def test_nuget_package_contains_readme():
    """Running dotnet pack produces a nupkg that contains README.md at the root.
    
    NOTE: This test requires .NET 10 SDK, but the environment has .NET 8.
    The actual configuration is verified by test_csproj_package_readme_property
    and test_csproj_packs_readme which check the csproj is correctly configured.
    This test is a best-effort verification that will skip if dotnet pack fails.
    """
    import tempfile

    # Create temp directory for package output
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run dotnet pack with the README-containing project
        r = subprocess.run(
            ["dotnet", "pack", CSPROJ,
             "-o", tmpdir,
             "-p:NoWarn=NU1701",
             "-p:TreatWarningsAsErrors=false",
             "--verbosity", "quiet"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )

        # If pack fails (e.g., due to .NET SDK version mismatch), skip this test
        # The csproj configuration is already verified by other tests
        if r.returncode != 0:
            err_combined = (r.stdout + r.stderr).lower()
            # Skip for various environment/build issues
            skip_indicators = [
                "msb4236",  # SDK resolution error
                "project",  # Project reference issues
                "msb1006",  # Property error
                "could not execute",  # SDK not found
                "sdk",  # SDK version issues
                "net10.0",  # .NET 10.0 not available
                "download",  # SDK download suggestion
            ]
            if any(ind in err_combined for ind in skip_indicators):
                import pytest
                pytest.skip(f"Cannot pack due to environment/SDK limitations: {r.stderr[:200]}")

        assert r.returncode == 0, f"dotnet pack failed: {r.stderr[:500]}"

        # Find the generated nupkg
        nupkgs = list(Path(tmpdir).glob("*.nupkg"))
        assert len(nupkgs) > 0, "No .nupkg file was produced"

        # Extract and verify README.md is at the root of the package
        pkg = nupkgs[0]
        with zipfile.ZipFile(pkg, 'r') as zf:
            files = zf.namelist()
            readme_in_root = any(
                f.lower() == "readme.md" or f.endswith("/readme.md") or f.endswith("\\readme.md")
                for f in files
            )
            assert readme_in_root, f"README.md not found in package. Files: {files[:20]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural / regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_csproj_well_formed_xml():
    """Controls.NuGet.csproj must be well-formed XML."""
    tree = ET.parse(CSPROJ)
    root = tree.getroot()
    assert root is not None, "Root element is None"


# [static] pass_to_pass
def test_readme_valid_markdown():
    """README.md must be non-trivial markdown with multiple sections."""
    content = Path(README).read_text()
    lines = content.strip().splitlines()
    assert len(lines) > 50, "README too short: " + str(len(lines)) + " lines"
    h2_count = sum(1 for line in lines if line.startswith("## "))
    assert h2_count >= 5, "Only " + str(h2_count) + " ## headings, expected >= 5"


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_csproj_msbuild_parseable():
    """Repo's Controls.NuGet.csproj is parseable by MSBuild CLI (pass_to_pass).

    Uses dotnet msbuild to verify the project file can be parsed and evaluated.
    This is a real CI command that validates MSBuild syntax without requiring
    the full .NET 10 SDK or workloads.
    """
    r = subprocess.run(
        ["dotnet", "msbuild", CSPROJ, "-getProperty:IsPackable,PackageId"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MSBuild failed to parse .csproj:\n{r.stderr[-500:]}"
    # Verify valid JSON output with expected properties
    assert '"IsPackable"' in r.stdout or "IsPackable" in r.stdout, \
        "MSBuild output missing IsPackable property"


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_project_references_msbuild():
    """Repo's Controls.NuGet.csproj has valid project references per MSBuild (pass_to_pass).

    Uses dotnet msbuild -getItem to retrieve evaluated ProjectReference items.
    This validates the project references are correctly specified.
    """
    r = subprocess.run(
        ["dotnet", "msbuild", CSPROJ, "-getItem:ProjectReference"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MSBuild failed to get ProjectReferences:\n{r.stderr[-500:]}"
    # Verify we have project references
    assert '"ProjectReference"' in r.stdout or "ProjectReference" in r.stdout, \
        "No ProjectReference items found in .csproj"


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_nuget_properties_msbuild():
    """Repo's Controls.NuGet.csproj has required NuGet metadata via MSBuild (pass_to_pass).

    Uses dotnet msbuild to verify essential NuGet packaging properties are defined.
    This is a real CI command equivalent to checking package configuration.
    """
    r = subprocess.run(
        ["dotnet", "msbuild", CSPROJ, "-getProperty:IsPackable,PackageId,Description"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MSBuild failed to get NuGet properties:\n{r.stderr[-500:]}"
    # Verify properties are present and non-empty
    assert '"IsPackable"' in r.stdout, "IsPackable property not found"
    assert '"PackageId"' in r.stdout, "PackageId property not found"
    assert '"Description"' in r.stdout, "Description property not found"


# [repo_tests] pass_to_pass - CI/CD gate
def test_repo_csproj_preprocess_valid():
    """Repo's Controls.NuGet.csproj preprocesses without errors (pass_to_pass).

    Uses dotnet msbuild -preprocess to fully expand the project file.
    This validates all imports, SDK references, and property evaluations work correctly.
    """
    r = subprocess.run(
        ["dotnet", "msbuild", CSPROJ, "-preprocess", "-nologo"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"MSBuild preprocess failed:\n{r.stderr[-500:]}"
    # Verify output contains essential elements of a valid preprocessed project
    assert "<Project" in r.stdout, "Preprocessed output missing <Project> element"
    assert "</Project>" in r.stdout, "Preprocessed output missing closing </Project>"
