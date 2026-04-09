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
    global_json_path = Path(REPO) / "global.json"
    assert global_json_path.exists(), "global.json must exist"
    content = global_json_path.read_text()
    data = json.loads(content)
    assert "tools" in data, "global.json must have 'tools' section"
    assert "dotnet" in data["tools"], "global.json must specify dotnet SDK version"
    assert "msbuild-sdks" in data, "global.json must have 'msbuild-sdks' section"


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_directory_build_props_valid():
    """Directory.Build.props is valid XML if it exists (pass_to_pass)."""
    props_path = Path(REPO) / "Directory.Build.props"
    if props_path.exists():
        try:
            ET.parse(props_path)
        except ET.ParseError as e:
            assert False, f"Directory.Build.props is invalid XML: {e}"


# [repo_tests] pass_to_pass
def test_directory_build_targets_valid():
    """Directory.Build.targets is valid XML if it exists (pass_to_pass)."""
    targets_path = Path(REPO) / "Directory.Build.targets"
    if targets_path.exists():
        try:
            ET.parse(targets_path)
        except ET.ParseError as e:
            assert False, f"Directory.Build.targets is invalid XML: {e}"


# [repo_tests] pass_to_pass
def test_github_workflows_valid_yaml():
    """GitHub workflow files have valid YAML syntax (pass_to_pass)."""
    workflows_dir = Path(REPO) / ".github/workflows"
    if not workflows_dir.exists():
        return
    yaml_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    assert len(yaml_files) > 0, "Must have at least one workflow file"
    errors = []
    for fpath in yaml_files:
        content = fpath.read_text()
        # Basic YAML validation - check for balanced braces and indentation
        try:
            # Python's json module can parse YAML-like structures for basic validation
            # Or just check basic structure
            lines = content.split('\n')
            indent_stack = [0]
            for i, line in enumerate(lines, 1):
                if not line.strip() or line.strip().startswith('#'):
                    continue
                indent = len(line) - len(line.lstrip())
                if indent > indent_stack[-1]:
                    indent_stack.append(indent)
                elif indent < indent_stack[-1]:
                    while indent_stack and indent < indent_stack[-1]:
                        indent_stack.pop()
                    if indent != indent_stack[-1]:
                        errors.append(f"{fpath.name}:{i}: inconsistent indentation")
                        break
        except Exception as e:
            errors.append(f"{fpath.name}: {e}")
    assert not errors, f"YAML syntax errors: {errors[:5]}"


# [repo_tests] pass_to_pass
def test_build_scripts_executable():
    """Build scripts exist and have correct structure (pass_to_pass)."""
    build_sh = Path(REPO) / "build.sh"
    build_ps1 = Path(REPO) / "build.ps1"
    assert build_sh.exists(), "build.sh must exist"
    assert build_ps1.exists(), "build.ps1 must exist"
    # Check shebang in build.sh
    sh_content = build_sh.read_text()
    assert sh_content.startswith('#!/') or '#!/bin/bash' in sh_content[:100], \
        "build.sh must have shebang"


# [repo_tests] pass_to_pass
def test_nuget_config_valid():
    """NuGet.config is valid XML with required package sources (pass_to_pass)."""
    nuget_config = Path(REPO) / "NuGet.config"
    assert nuget_config.exists(), "NuGet.config must exist"
    try:
        tree = ET.parse(nuget_config)
        root = tree.getroot()
        assert root.tag == 'configuration', f"Root tag must be 'configuration', got '{root.tag}'"
    except ET.ParseError as e:
        assert False, f"NuGet.config is invalid XML: {e}"


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

for param in ['\$SkipBuild', '\$SkipInstall', '\$AutoProvision']:
    if param not in content:
        print(f"FAIL: Script must have {param} parameter")
        sys.exit(1)

if 'MAUI_PACKAGE_VERSION' not in content:
    print("FAIL: Script must handle MAUI_PACKAGE_VERSION")
    sys.exit(1)

if '\$ErrorActionPreference' not in content:
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
    assert re.search(r'9\.\s+\*\*try-fix\*\*', content), \
        "try-fix skill must be renumbered to 9"
    assert re.search(r'8\.\s+\*\*run-integration-tests\*\*', content), \
        "run-integration-tests must be numbered 8"
