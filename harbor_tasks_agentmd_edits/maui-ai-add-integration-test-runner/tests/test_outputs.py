"""
Task: maui-ai-add-integration-test-runner
Repo: dotnet/maui @ 71e5c2f595d7cc104adc18753a646e9c557c10da
PR:   33654

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
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

for param in ['$SkipBuild', '$SkipInstall', '$AutoProvision']:
    if param not in content:
        print(f"FAIL: Script must have {param} parameter")
        sys.exit(1)

if 'MAUI_PACKAGE_VERSION' not in content:
    print("FAIL: Script must handle MAUI_PACKAGE_VERSION")
    sys.exit(1)

if '$ErrorActionPreference' not in content:
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
