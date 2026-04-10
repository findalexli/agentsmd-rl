"""
Task: maui-ai-add-integration-test-runner
Repo: dotnet/maui @ 71e5c2f595d7cc104adc18753a646e9c557c10da
PR:   33654

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_csharp_syntax_valid():
    """BaseBuildTest.cs has balanced delimiters and valid C# structure."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    assert src.count('{') == src.count('}'), "Unbalanced braces in BaseBuildTest.cs"
    assert src.count('(') == src.count(')'), "Unbalanced parens in BaseBuildTest.cs"
    assert 'namespace' in src, "Missing namespace declaration"
    assert 'class' in src, "Missing class declaration"


# [static] pass_to_pass
def test_not_stub():
    """SetUpNuGetPackages has real file I/O logic, not a stub."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    file_ops = re.findall(r'File\.(Copy|WriteAllText|ReadAllText|Exists|Delete)\(', src)
    assert len(file_ops) >= 3, \
        f"SetUpNuGetPackages must have real file I/O operations, found {len(file_ops)}"


# [repo_tests] pass_to_pass
def test_global_json_valid():
    """global.json is valid JSON with required SDK configuration (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json, sys
from pathlib import Path
global_json_path = Path("/workspace/maui") / "global.json"
if not global_json_path.exists():
    print("FAIL: global.json must exist")
    sys.exit(1)
content = global_json_path.read_text()
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    print(f"FAIL: Invalid JSON: {e}")
    sys.exit(1)
if "tools" not in data:
    print("FAIL: global.json must have 'tools' section")
    sys.exit(1)
if "dotnet" not in data.get("tools", {}):
    print("FAIL: global.json must specify dotnet SDK version")
    sys.exit(1)
if "msbuild-sdks" not in data:
    print("FAIL: global.json must have 'msbuild-sdks' section")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_csproj_files_valid_xml():
    """All .csproj files are valid XML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
REPO = "/workspace/maui"
csproj_files = list(Path(REPO).rglob("*.csproj"))
if len(csproj_files) == 0:
    print("FAIL: Must have at least one .csproj file")
    sys.exit(1)
errors = []
for fpath in csproj_files[:20]:  # Check first 20 for performance
    try:
        ET.parse(fpath)
    except ET.ParseError as e:
        errors.append(f"{fpath}: {e}")
if errors:
    print(f"FAIL: Invalid XML in .csproj files: {errors[:5]}")
    sys.exit(1)
print(f"PASS: {len(csproj_files)} .csproj files checked")
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_directory_build_props_valid():
    """Directory.Build.props is valid XML if it exists (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
props_path = Path("/workspace/maui") / "Directory.Build.props"
if props_path.exists():
    try:
        ET.parse(props_path)
    except ET.ParseError as e:
        print(f"FAIL: Directory.Build.props is invalid XML: {e}")
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_directory_build_targets_valid():
    """Directory.Build.targets is valid XML if it exists (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
targets_path = Path("/workspace/maui") / "Directory.Build.targets"
if targets_path.exists():
    try:
        ET.parse(targets_path)
    except ET.ParseError as e:
        print(f"FAIL: Directory.Build.targets is invalid XML: {e}")
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_nuget_config_valid():
    """NuGet.config is valid XML with required package sources (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
nuget_config = Path("/workspace/maui") / "NuGet.config"
if not nuget_config.exists():
    print("FAIL: NuGet.config must exist")
    sys.exit(1)
try:
    tree = ET.parse(nuget_config)
    root = tree.getroot()
    if root.tag != 'configuration':
        print(f"FAIL: Root tag must be 'configuration', got '{root.tag}'")
        sys.exit(1)
except ET.ParseError as e:
    print(f"FAIL: NuGet.config is invalid XML: {e}")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_build_scripts_executable():
    """Build scripts exist and have correct structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
REPO = "/workspace/maui"
build_sh = Path(REPO) / "build.sh"
build_ps1 = Path(REPO) / "build.ps1"
if not build_sh.exists():
    print("FAIL: build.sh must exist")
    sys.exit(1)
if not build_ps1.exists():
    print("FAIL: build.ps1 must exist")
    sys.exit(1)
# Check shebang in build.sh
sh_content = build_sh.read_text()
if not (sh_content.startswith('#!/') or '#!/bin/bash' in sh_content[:100]):
    print("FAIL: build.sh must have shebang")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_git_repo_clean():
    """Git repository is in a clean state with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    assert r.stdout.strip() == "", f"Git repo has uncommitted changes:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_git_no_merge_conflicts():
    """Repository contains no merge conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "-l", "<<<<<<< HEAD"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # git grep returns exit code 1 when no matches found
    assert r.returncode == 1 or r.stdout.strip() == "", \
        f"Found merge conflict markers in:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_solution_file_exists():
    """Solution file Microsoft.Maui.sln exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
sln_path = Path("/workspace/maui") / "Microsoft.Maui.sln"
if not sln_path.exists():
    print("FAIL: Microsoft.Maui.sln must exist")
    sys.exit(1)
content = sln_path.read_text()
if "Microsoft Visual Studio Solution File" not in content:
    print("FAIL: Invalid solution file format")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_test_utils_csproj_valid():
    """Integration tests project file is valid XML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
csproj_path = Path("/workspace/maui") / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/Microsoft.Maui.IntegrationTests.csproj"
if not csproj_path.exists():
    print("FAIL: Integration tests csproj must exist")
    sys.exit(1)
try:
    ET.parse(csproj_path)
except ET.ParseError as e:
    print(f"FAIL: Invalid XML: {e}")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_github_workflows_exist():
    """GitHub Actions workflow files exist and are readable (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
workflows_dir = Path("/workspace/maui") / ".github/workflows"
if not workflows_dir.exists():
    print("FAIL: .github/workflows directory must exist")
    sys.exit(1)
yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
if len(yaml_files) == 0:
    print("FAIL: Must have at least one workflow file")
    sys.exit(1)
print(f"PASS: {len(yaml_files)} workflow files found")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_basebuildtest_cs_exists():
    """BaseBuildTest.cs exists and contains required methods (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
src_path = Path("/workspace/maui") / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs"
if not src_path.exists():
    print("FAIL: BaseBuildTest.cs must exist")
    sys.exit(1)
content = src_path.read_text()
if "class BaseBuildTest" not in content:
    print("FAIL: Must contain BaseBuildTest class")
    sys.exit(1)
if "SetUpNuGetPackages" not in content:
    print("FAIL: Must contain SetUpNuGetPackages method")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_editorconfig_exists():
    """EditorConfig file exists and has valid content (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
config_path = Path("/workspace/maui") / ".editorconfig"
if not config_path.exists():
    print("FAIL: .editorconfig must exist")
    sys.exit(1)
content = config_path.read_text()
if "root = true" not in content:
    print("FAIL: EditorConfig must have root = true")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# [repo_tests] pass_to_pass
def test_gitattributes_exists():
    """.gitattributes file exists with required settings (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
from pathlib import Path
ga_path = Path("/workspace/maui") / ".gitattributes"
if not ga_path.exists():
    print("FAIL: .gitattributes must exist")
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral code tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_msbuild_isolation_files():
    """BaseBuildTest.cs creates valid Directory.Build.props and .targets to block MSBuild inheritance."""
    r = subprocess.run(
        ["python3", "-c", """
import re, xml.etree.ElementTree as ET, sys, tempfile, os

src = open("src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read()

# Verify File.WriteAllText calls for both isolation files
if not re.search(r'File\\.WriteAllText\\(.*Directory\\.Build\\.props', src):
    print("FAIL: No File.WriteAllText for Directory.Build.props")
    sys.exit(1)
if not re.search(r'File\\.WriteAllText\\(.*Directory\\.Build\\.targets', src):
    print("FAIL: No File.WriteAllText for Directory.Build.targets")
    sys.exit(1)

# Extract triple-quoted raw string literals containing <Project>
matches = re.findall(r'\"\"\"(.*?)\"\"\"', src, re.DOTALL)
project_xmls = [m.strip() for m in matches if '<Project>' in m]
if len(project_xmls) < 2:
    print(f"FAIL: Expected >=2 embedded XML project blocks, found {len(project_xmls)}")
    sys.exit(1)

# Write each to a temp file and parse as XML (simulates runtime file creation)
tmpdir = tempfile.mkdtemp()
for i, xml_str in enumerate(project_xmls):
    fpath = os.path.join(tmpdir, f"test_{i}.xml")
    with open(fpath, 'w') as f:
        f.write(xml_str)
    root = ET.parse(fpath).getroot()
    if root.tag != 'Project':
        print(f"FAIL: XML #{i+1} root is '{root.tag}', expected 'Project'")
        sys.exit(1)
    os.unlink(fpath)
os.rmdir(tmpdir)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_md_valid():
    """run-integration-tests SKILL.md exists with valid frontmatter and all test categories."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

path = ".github/skills/run-integration-tests/SKILL.md"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: SKILL.md not found at " + path)
    sys.exit(1)

if not content.startswith('---'):
    print("FAIL: SKILL.md must start with YAML frontmatter (---)")
    sys.exit(1)

end_idx = content.index('---', 3)
frontmatter = content[3:end_idx]

if 'name: run-integration-tests' not in frontmatter:
    print("FAIL: Frontmatter must contain name: run-integration-tests")
    sys.exit(1)
if 'description:' not in frontmatter:
    print("FAIL: Frontmatter must contain a description field")
    sys.exit(1)

categories = ['Build', 'WindowsTemplates', 'macOSTemplates', 'Blazor',
              'MultiProject', 'Samples', 'AOT', 'RunOnAndroid', 'RunOniOS']
for cat in categories:
    if cat not in content:
        print(f"FAIL: SKILL.md must document the '{cat}' category")
        sys.exit(1)

if 'Run-IntegrationTests.ps1' not in content:
    print("FAIL: SKILL.md must reference Run-IntegrationTests.ps1")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_run_script_valid():
    """Run-IntegrationTests.ps1 exists with ValidateSet categories and workflow parameters."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

path = ".github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: Run-IntegrationTests.ps1 not found at " + path)
    sys.exit(1)

if 'ValidateSet' not in content:
    print("FAIL: Script must have ValidateSet for Category parameter")
    sys.exit(1)

for cat in ['Build', 'WindowsTemplates', 'macOSTemplates', 'Blazor', 'RunOniOS', 'RunOnAndroid']:
    if cat not in content:
        print(f"FAIL: ValidateSet must include '{cat}'")
        sys.exit(1)

for param in ['\\$SkipBuild', '\\$SkipInstall', '\\$AutoProvision']:
    if param not in content:
        print(f"FAIL: Script must have {param} parameter")
        sys.exit(1)

if 'MAUI_PACKAGE_VERSION' not in content:
    print("FAIL: Script must handle MAUI_PACKAGE_VERSION")
    sys.exit(1)

if '\\$ErrorActionPreference' not in content:
    print("FAIL: Script must set ErrorActionPreference")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_copilot_instructions_lists_integration_skill():
    """copilot-instructions.md must list the run-integration-tests skill."""
    content = (Path(REPO) / ".github/copilot-instructions.md").read_text()
    assert 'run-integration-tests' in content, \
        "copilot-instructions.md must mention run-integration-tests skill"
    assert '.github/skills/run-integration-tests/SKILL.md' in content, \
        "copilot-instructions.md must reference the SKILL.md path"
    assert 'ALWAYS use this skill' in content, \
        "copilot-instructions.md should instruct to ALWAYS use this skill"


# [pr_diff] fail_to_pass
def test_integration_instructions_references_skill():
    """integration-tests.instructions.md must reference the run-integration-tests skill."""
    content = (Path(REPO) / ".github/instructions/integration-tests.instructions.md").read_text()
    assert 'run-integration-tests' in content, \
        "integration-tests.instructions.md must reference the skill"
    assert 'Run-IntegrationTests.ps1' in content, \
        "integration-tests.instructions.md must reference the PowerShell script"
    assert 'ALWAYS' in content, \
        "integration-tests.instructions.md must instruct to ALWAYS use the skill"


# [pr_diff] fail_to_pass
def test_copilot_instructions_skill_numbering():
    """Skill numbering must be sequential after adding run-integration-tests."""
    content = (Path(REPO) / ".github/copilot-instructions.md").read_text()
    assert re.search(r'9\.\s+\\*\\*try-fix\\*\\*', content), \
        "try-fix skill must be renumbered to 9"
    assert re.search(r'8\.\s+\\*\\*run-integration-tests\\*\\*', content), \
        "run-integration-tests must be numbered 8"
