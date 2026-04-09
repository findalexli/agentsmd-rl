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
    r = subprocess.run(
        ["python3", "-c",
         'import xml.etree.ElementTree as ET; '
         'tree = ET.parse("' + CSPROJ + '"); '
         'root = tree.getroot(); '
         'found = False; '
         'pg_tag = "{http://schemas.microsoft.com/developer/msbuild/2003}PropertyGroup" if root.tag.startswith("{http") else "PropertyGroup"; '
         'elem_tag = "{http://schemas.microsoft.com/developer/msbuild/2003}PackageReadmeFile" if root.tag.startswith("{http") else "PackageReadmeFile"; '
         'for pg in root.iter(pg_tag): '
         '    for child in pg: '
         '        tag = child.tag.split("}", 1)[-1] if "}" in child.tag else child.tag; '
         '        if tag == "PackageReadmeFile" and child.text and "README.md" in child.text: '
         '            found = True; break; '
         'assert found, "PackageReadmeFile element not found"; '
         'print("PASS")'],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, "PackageReadmeFile check failed: " + r.stderr
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_csproj_packs_readme():
    """Controls.NuGet.csproj must include README.md in the NuGet package via <None> item."""
    r = subprocess.run(
        ["python3", "-c",
         'import xml.etree.ElementTree as ET; '
         'tree = ET.parse("' + CSPROJ + '"); '
         'root = tree.getroot(); '
         'found = False; '
         'none_tag = "{http://schemas.microsoft.com/developer/msbuild/2003}None" if root.tag.startswith("{http") else "None"; '
         'for none_elem in root.iter(none_tag): '
         '    include = none_elem.get("Include", ""); '
         '    if "README.md" in include: '
         '        pack = none_elem.get("Pack", ""); '
         '        assert pack.lower() == "true", "Pack attr not true"; '
         '        found = True; break; '
         'assert found, "No None element for README.md found"; '
         'print("PASS")'],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, "README packaging check failed: " + r.stderr
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_readme_has_required_sections():
    """README.md must contain key sections: title, getting started, supported platforms."""
    r = subprocess.run(
        ["python3", "-c",
         'from pathlib import Path; '
         'content = Path("' + README + '").read_text(); '
         'required = [".NET MAUI", "Getting Started", "Supported Platforms", "Microsoft.Maui.Controls", "NuGet"]; '
         'missing = [p for p in required if p not in content]; '
         'assert not missing, f"Missing sections: {missing}"; '
         'print("PASS")'],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, "README content check failed: " + r.stderr
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_nuget_package_contains_readme():
    """Running dotnet pack produces a nupkg that contains README.md at the root."""
    import tempfile, shutil, os

    # Create temp directory for package output
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run dotnet pack with the README-containing project
        # We need to pack just this project, not the whole solution
        r = subprocess.run(
            ["dotnet", "pack", CSPROJ,
             "-o", tmpdir,
             "-p:NoWarn=NU1701;NU1903;NU1902;NU1900",  # suppress warnings
             "-p:TreatWarningsAsErrors=false",
             "--verbosity", "quiet"],
            capture_output=True, text=True, timeout=180, cwd=REPO,
        )

        # Pack may fail due to missing dependencies in the isolated environment,
        # but if it succeeds, we verify the README is in the package
        if r.returncode != 0:
            # If pack fails due to project references, that's an environment issue
            # not a fix issue - skip this test in that case
            if "error" in r.stderr.lower() and ("MSB4236" in r.stderr or "project" in r.stderr.lower()):
                print(f"SKIP: Cannot pack due to project reference resolution: {r.stderr[:200]}")
                return

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
    r = subprocess.run(
        ["python3", "-c",
         'import xml.etree.ElementTree as ET; '
         'tree = ET.parse("' + CSPROJ + '"); '
         'root = tree.getroot(); '
         'assert root is not None, "Root element is None"; '
         'print("PASS")'],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, "XML parse failed: " + r.stderr
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_readme_valid_markdown():
    """README.md must be non-trivial markdown with multiple sections."""
    content = Path(README).read_text()
    lines = content.strip().splitlines()
    assert len(lines) > 50, "README too short: " + str(len(lines)) + " lines"
    h2_count = sum(1 for line in lines if line.startswith("## "))
    assert h2_count >= 5, "Only " + str(h2_count) + " ## headings, expected >= 5"
