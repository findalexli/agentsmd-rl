"""
Task: maui-ai-add-integration-test-runner
Repo: dotnet/maui @ 71e5c2f595d7cc104adc18753a646e9c557c10da
PR:   33654

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
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
    # Both base and fix have real file operations (File.Copy, File.WriteAllText, etc.)
    file_ops = re.findall(r'File\.(Copy|WriteAllText|ReadAllText|Exists|Delete)\(', src)
    assert len(file_ops) >= 3, \
        f"SetUpNuGetPackages must have real file I/O operations, found {len(file_ops)}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_base_build_test_creates_directory_build_props():
    """BaseBuildTest.cs must create Directory.Build.props to prevent MSBuild inheritance."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    assert 'Directory.Build.props' in src, \
        "BaseBuildTest.cs must reference Directory.Build.props"
    assert re.search(r'File\.WriteAllText\(.*Directory\.Build\.props', src), \
        "BaseBuildTest.cs must use File.WriteAllText to create Directory.Build.props"
    assert '<Project>' in src, \
        "Created Directory.Build.props must contain a <Project> element"
    assert 'stops MSBuild' in src, \
        "Directory.Build.props must comment about stopping MSBuild directory walk"


# [pr_diff] fail_to_pass
def test_base_build_test_creates_directory_build_targets():
    """BaseBuildTest.cs must create Directory.Build.targets to prevent target inheritance."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    assert 'Directory.Build.targets' in src, \
        "BaseBuildTest.cs must reference Directory.Build.targets"
    assert re.search(r'File\.WriteAllText\(.*Directory\.Build\.targets', src), \
        "BaseBuildTest.cs must use File.WriteAllText to create Directory.Build.targets"


# [pr_diff] fail_to_pass
def test_directory_build_xml_is_valid():
    """XML content written by BaseBuildTest.cs must parse as valid XML."""
    src = (Path(REPO) / "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read_text()
    # Extract triple-quoted string contents that contain <Project>
    matches = re.findall(r'"""(.*?)"""', src, re.DOTALL)
    project_xmls = [m.strip() for m in matches if '<Project>' in m]
    assert len(project_xmls) >= 2, \
        f"Expected >= 2 triple-quoted XML strings (props + targets), found {len(project_xmls)}"
    for i, xml_str in enumerate(project_xmls):
        try:
            ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise AssertionError(f"Invalid XML in embedded file #{i + 1}: {e}\nContent:\n{xml_str}")


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
        "copilot-instructions.md should instruct to ALWAYS use this skill for integration tests"
    # Must list test categories
    assert 'WindowsTemplates' in content, \
        "copilot-instructions.md must list WindowsTemplates category"
    assert 'macOSTemplates' in content, \
        "copilot-instructions.md must list macOSTemplates category"


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
    assert 'SkipBuild' in content, \
        "integration-tests.instructions.md should show example commands with -SkipBuild"


# [pr_diff] fail_to_pass
def test_skill_md_exists_with_content():
    """run-integration-tests SKILL.md must exist with frontmatter and test categories."""
    skill_md = Path(REPO) / ".github/skills/run-integration-tests/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist at .github/skills/run-integration-tests/SKILL.md"
    content = skill_md.read_text()
    # Frontmatter
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert 'name: run-integration-tests' in content, \
        "SKILL.md frontmatter must have name: run-integration-tests"
    assert 'description:' in content, \
        "SKILL.md frontmatter must have a description field"
    # Test categories
    for cat in ['Build', 'WindowsTemplates', 'macOSTemplates', 'Blazor',
                'MultiProject', 'Samples', 'AOT', 'RunOnAndroid', 'RunOniOS']:
        assert cat in content, f"SKILL.md must document the '{cat}' test category"
    # Script reference
    assert 'Run-IntegrationTests.ps1' in content, \
        "SKILL.md must reference the Run-IntegrationTests.ps1 script"


# [pr_diff] fail_to_pass
def test_run_script_exists_with_parameters():
    """Run-IntegrationTests.ps1 must exist with proper parameters and validation."""
    script = Path(REPO) / ".github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1"
    assert script.exists(), "Run-IntegrationTests.ps1 must exist"
    content = script.read_text()
    # Parameter validation
    assert 'ValidateSet' in content, "Script must have ValidateSet for Category parameter"
    for cat in ['Build', 'WindowsTemplates', 'macOSTemplates', 'Blazor', 'RunOniOS', 'RunOnAndroid']:
        assert cat in content, f"ValidateSet must include '{cat}'"
    # Key parameters
    assert '$SkipBuild' in content, "Script must have -SkipBuild parameter"
    assert '$SkipInstall' in content, "Script must have -SkipInstall parameter"
    assert '$AutoProvision' in content, "Script must have -AutoProvision parameter"
    # Must set MAUI_PACKAGE_VERSION env var
    assert 'MAUI_PACKAGE_VERSION' in content, "Script must set MAUI_PACKAGE_VERSION"
    # Error handling
    assert '$ErrorActionPreference' in content, "Script must set ErrorActionPreference"


# [pr_diff] fail_to_pass
def test_copilot_instructions_skill_numbering():
    """Skill numbering must be sequential after adding run-integration-tests."""
    content = (Path(REPO) / ".github/copilot-instructions.md").read_text()
    # After the change, run-integration-tests is #8 and try-fix is #9
    # Check that try-fix moved to 9 (was 8 before the change)
    assert re.search(r'9\.\s+\*\*try-fix\*\*', content), \
        "try-fix skill must be renumbered to 9"
    assert re.search(r'8\.\s+\*\*run-integration-tests\*\*', content), \
        "run-integration-tests must be numbered 8"
