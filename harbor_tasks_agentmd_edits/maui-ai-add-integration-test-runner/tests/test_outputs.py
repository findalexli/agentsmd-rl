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
# Gates (pass_to_pass, static) — file read / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_csharp_syntax_valid():
    """BaseBuildTest.cs has balanced delimiters and valid C# structure."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    assert src.count("{") == src.count("}"), "Unbalanced braces in BaseBuildTest.cs"
    assert src.count("(") == src.count(")"), "Unbalanced parens in BaseBuildTest.cs"
    assert "namespace" in src, "Missing namespace declaration"
    assert "class" in src, "Missing class declaration"


# [static] pass_to_pass
def test_not_stub():
    """SetUpNuGetPackages has real file I/O logic, not a stub."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    file_ops = re.findall(r"File\.(Copy|WriteAllText|ReadAllText|Exists|Delete)\(", src)
    assert len(file_ops) >= 3, \
        f"SetUpNuGetPackages must have real file I/O operations, found {len(file_ops)}"


# [static] pass_to_pass
def test_global_json_valid():
    """global.json is valid JSON with required SDK configuration (pass_to_pass)."""
    global_json_path = Path(REPO) / "global.json"
    assert global_json_path.exists(), "global.json must exist"
    content = global_json_path.read_text()
    data = json.loads(content)
    assert "tools" in data, "global.json must have 'tools' section"
    assert "dotnet" in data.get("tools", {}), "global.json must specify dotnet SDK version"
    assert "msbuild-sdks" in data, "global.json must have 'msbuild-sdks' section"


# [static] pass_to_pass
def test_csproj_files_valid_xml():
    """All .csproj files are valid XML (pass_to_pass)."""
    csproj_files = list(Path(REPO).rglob("*.csproj"))
    assert len(csproj_files) > 0, "Must have at least one .csproj file"
    errors = []
    for fpath in csproj_files[:20]:  # Check first 20 for performance
        try:
            ET.parse(fpath)
        except ET.ParseError as e:
            errors.append(f"{fpath}: {e}")
    assert not errors, f"Invalid XML in .csproj files: {errors[:5]}"


# [static] pass_to_pass
def test_directory_build_props_valid():
    """Directory.Build.props is valid XML if it exists (pass_to_pass)."""
    props_path = Path(REPO) / "Directory.Build.props"
    if props_path.exists():
        try:
            ET.parse(props_path)
        except ET.ParseError as e:
            raise AssertionError(f"Directory.Build.props is invalid XML: {e}")


# [static] pass_to_pass
def test_directory_build_targets_valid():
    """Directory.Build.targets is valid XML if it exists (pass_to_pass)."""
    targets_path = Path(REPO) / "Directory.Build.targets"
    if targets_path.exists():
        try:
            ET.parse(targets_path)
        except ET.ParseError as e:
            raise AssertionError(f"Directory.Build.targets is invalid XML: {e}")


# [static] pass_to_pass
def test_nuget_config_valid():
    """NuGet.config is valid XML with required package sources (pass_to_pass)."""
    nuget_config = Path(REPO) / "NuGet.config"
    assert nuget_config.exists(), "NuGet.config must exist"
    tree = ET.parse(nuget_config)
    root = tree.getroot()
    assert root.tag == "configuration", f"Root tag must be 'configuration', got '{root.tag}'"


# [static] pass_to_pass
def test_build_scripts_executable():
    """Build scripts exist and have correct structure (pass_to_pass)."""
    build_sh = Path(REPO) / "build.sh"
    build_ps1 = Path(REPO) / "build.ps1"
    assert build_sh.exists(), "build.sh must exist"
    assert build_ps1.exists(), "build.ps1 must exist"
    # Check shebang in build.sh
    sh_content = build_sh.read_text()
    assert sh_content.startswith("#!/") or "#!/bin/bash" in sh_content[:100], \
        "build.sh must have shebang"


# [static] pass_to_pass
def test_solution_file_exists():
    """Solution file Microsoft.Maui.sln exists and is readable (pass_to_pass)."""
    sln_path = Path(REPO) / "Microsoft.Maui.sln"
    assert sln_path.exists(), "Microsoft.Maui.sln must exist"
    content = sln_path.read_text()
    assert "Microsoft Visual Studio Solution File" in content, "Invalid solution file format"


# [static] pass_to_pass
def test_test_utils_csproj_valid():
    """Integration tests project file is valid XML (pass_to_pass)."""
    csproj_path = Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/Microsoft.Maui.IntegrationTests.csproj"
    assert csproj_path.exists(), "Integration tests csproj must exist"
    try:
        ET.parse(csproj_path)
    except ET.ParseError as e:
        raise AssertionError(f"Invalid XML: {e}")


# [static] pass_to_pass
def test_github_workflows_exist():
    """GitHub Actions workflow files exist and are readable (pass_to_pass)."""
    workflows_dir = Path(REPO) / ".github/workflows"
    assert workflows_dir.exists(), ".github/workflows directory must exist"
    yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    assert len(yaml_files) > 0, "Must have at least one workflow file"


# [static] pass_to_pass
def test_basebuildtest_cs_exists():
    """BaseBuildTest.cs exists and contains required methods (pass_to_pass)."""
    src_path = Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs"
    assert src_path.exists(), "BaseBuildTest.cs must exist"
    content = src_path.read_text()
    assert "class BaseBuildTest" in content, "Must contain BaseBuildTest class"
    assert "SetUpNuGetPackages" in content, "Must contain SetUpNuGetPackages method"


# [static] pass_to_pass
def test_editorconfig_exists():
    """EditorConfig file exists and has valid content (pass_to_pass)."""
    config_path = Path(REPO) / ".editorconfig"
    assert config_path.exists(), ".editorconfig must exist"
    content = config_path.read_text()
    assert "root = true" in content, "EditorConfig must have root = true"


# [static] pass_to_pass
def test_gitattributes_exists():
    """.gitattributes file exists with required settings (pass_to_pass)."""
    ga_path = Path(REPO) / ".gitattributes"
    assert ga_path.exists(), ".gitattributes must exist"


# [static] pass_to_pass
def test_powershell_script_valid():
    """Run-IntegrationTests.ps1 has valid PowerShell syntax structure (pass_to_pass)."""
    ps1_path = Path(REPO) / ".github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1"
    assert ps1_path.exists(), "Run-IntegrationTests.ps1 must exist"
    content = ps1_path.read_text()
    # Check for valid PowerShell structure
    assert content.startswith("#") or content.startswith("<#"), \
        "PowerShell script should start with comment block"
    assert "param(" in content, "PowerShell script must have param() block"
    assert "ValidateSet" in content, "PowerShell script must have ValidateSet"
    assert r"\$ErrorActionPreference" in content or "ErrorActionPreference" in content, \
        "PowerShell script must set ErrorActionPreference"


# [static] pass_to_pass
def test_copilot_instructions_valid():
    """copilot-instructions.md exists and has valid structure (pass_to_pass)."""
    path = Path(REPO) / ".github/copilot-instructions.md"
    assert path.exists(), "copilot-instructions.md must exist"
    content = path.read_text()
    assert "---" in content[:10], "Must have YAML frontmatter"
    assert "## " in content, "Must have markdown sections"
    assert "Skills" in content or "skills" in content, "Must reference skills"


# [static] pass_to_pass
def test_integration_instructions_valid():
    """integration-tests.instructions.md exists and has valid content (pass_to_pass)."""
    path = Path(REPO) / ".github/instructions/integration-tests.instructions.md"
    assert path.exists(), "integration-tests.instructions.md must exist"
    content = path.read_text()
    assert "## " in content, "Must have markdown sections"
    assert "Integration" in content or "integration" in content.lower(), "Must reference integration tests"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — real CI commands via subprocess.run()
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - uses git command
def test_git_repo_clean():
    """Git repository is in a clean state with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    assert r.stdout.strip() == "", f"Git repo has uncommitted changes:\n{r.stdout}"


# [repo_tests] pass_to_pass - uses git grep command
def test_git_no_merge_conflicts():
    """Repository contains no merge conflict markers via git grep (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "-l", "<<<<<<< HEAD"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # git grep returns exit code 1 when no matches found (which is what we want)
    assert r.returncode == 1 or r.stdout.strip() == "", \
        f"Found merge conflict markers in:\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral code tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_msbuild_isolation_files():
    """BaseBuildTest.cs creates valid Directory.Build.props and .targets to block MSBuild inheritance."""
    # Use a Python script file instead of inline to avoid escaping issues
    script_content = '''
import re
import xml.etree.ElementTree as ET
import sys
import tempfile
import os

src = open("src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read()

# Verify File.WriteAllText calls for both isolation files
if not re.search(r"File\\.WriteAllText\\(.*Directory\\.Build\\.props", src):
    print("FAIL: No File.WriteAllText for Directory.Build.props")
    sys.exit(1)
if not re.search(r"File\\.WriteAllText\\(.*Directory\\.Build\\.targets", src):
    print("FAIL: No File.WriteAllText for Directory.Build.targets")
    sys.exit(1)

# Extract triple-quoted raw string literals containing <Project>
matches = re.findall(r"\"\"\"(.*?)\"\"\"", src, re.DOTALL)
project_xmls = [m.strip() for m in matches if "<Project>" in m]
if len(project_xmls) < 2:
    print(f"FAIL: Expected >=2 embedded XML project blocks, found {len(project_xmls)}")
    sys.exit(1)

# Write each to a temp file and parse as XML (simulates runtime file creation)
tmpdir = tempfile.mkdtemp()
for i, xml_str in enumerate(project_xmls):
    fpath = os.path.join(tmpdir, f"test_{i}.xml")
    with open(fpath, "w") as f:
        f.write(xml_str)
    root = ET.parse(fpath).getroot()
    if root.tag != "Project":
        print(f"FAIL: XML #{i+1} root is '{root.tag}', expected 'Project'")
        sys.exit(1)
    os.unlink(fpath)
os.rmdir(tmpdir)

print("PASS")
'''
    # Write script to temp file and execute
    script_path = "/tmp/msbuild_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_md_valid():
    """run-integration-tests SKILL.md exists with valid frontmatter and all test categories."""
    script_content = '''
import sys

path = ".github/skills/run-integration-tests/SKILL.md"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: SKILL.md not found at " + path)
    sys.exit(1)

if not content.startswith("---"):
    print("FAIL: SKILL.md must start with YAML frontmatter (---)")
    sys.exit(1)

end_idx = content.index("---", 3)
frontmatter = content[3:end_idx]

if "name: run-integration-tests" not in frontmatter:
    print("FAIL: Frontmatter must contain name: run-integration-tests")
    sys.exit(1)
if "description:" not in frontmatter:
    print("FAIL: Frontmatter must contain a description field")
    sys.exit(1)

categories = ["Build", "WindowsTemplates", "macOSTemplates", "Blazor",
              "MultiProject", "Samples", "AOT", "RunOnAndroid", "RunOniOS"]
for cat in categories:
    if cat not in content:
        print(f"FAIL: SKILL.md must document the '{cat}' category")
        sys.exit(1)

if "Run-IntegrationTests.ps1" not in content:
    print("FAIL: SKILL.md must reference Run-IntegrationTests.ps1")
    sys.exit(1)

print("PASS")
'''
    script_path = "/tmp/skill_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_run_script_valid():
    """Run-IntegrationTests.ps1 exists with ValidateSet categories and workflow parameters."""
    script_content = '''
import sys

path = ".github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: Run-IntegrationTests.ps1 not found at " + path)
    sys.exit(1)

if "ValidateSet" not in content:
    print("FAIL: Script must have ValidateSet for Category parameter")
    sys.exit(1)

for cat in ["Build", "WindowsTemplates", "macOSTemplates", "Blazor", "RunOniOS", "RunOnAndroid"]:
    if cat not in content:
        print(f"FAIL: ValidateSet must include '{cat}'")
        sys.exit(1)

for param in ["SkipBuild", "SkipInstall", "AutoProvision"]:
    if param not in content:
        print(f"FAIL: Script must have ${param} parameter")
        sys.exit(1)

if "MAUI_PACKAGE_VERSION" not in content:
    print("FAIL: Script must handle MAUI_PACKAGE_VERSION")
    sys.exit(1)

if "ErrorActionPreference" not in content:
    print("FAIL: Script must set ErrorActionPreference")
    sys.exit(1)

print("PASS")
'''
    script_path = "/tmp/script_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)
    
    r = subprocess.run(
        ["python3", script_path],
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
    assert "run-integration-tests" in content, \
        "copilot-instructions.md must mention run-integration-tests skill"
    assert ".github/skills/run-integration-tests/SKILL.md" in content, \
        "copilot-instructions.md must reference the SKILL.md path"
    assert "ALWAYS use this skill" in content, \
        "copilot-instructions.md should instruct to ALWAYS use this skill"


# [pr_diff] fail_to_pass
def test_integration_instructions_references_skill():
    """integration-tests.instructions.md must reference the run-integration-tests skill."""
    content = (Path(REPO) / ".github/instructions/integration-tests.instructions.md").read_text()
    assert "run-integration-tests" in content, \
        "integration-tests.instructions.md must reference the skill"
    assert "Run-IntegrationTests.ps1" in content, \
        "integration-tests.instructions.md must reference the PowerShell script"
    assert "ALWAYS" in content, \
        "integration-tests.instructions.md must instruct to ALWAYS use the skill"


# [pr_diff] fail_to_pass
def test_copilot_instructions_skill_numbering():
    """Skill numbering must be sequential after adding run-integration-tests."""
    content = (Path(REPO) / ".github/copilot-instructions.md").read_text()
    assert re.search(r"9\.\\s+\\*\\*try-fix\\*\\*", content), \
        "try-fix skill must be renumbered to 9"
    assert re.search(r"8\.\\s+\\*\\*run-integration-tests\\*\\*", content), \
        "run-integration-tests must be numbered 8"
