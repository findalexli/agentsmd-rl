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


# [repo_tests] pass_to_pass - validates YAML frontmatter in SKILL.md files
def test_skill_md_yaml_frontmatter():
    """Existing SKILL.md files have valid YAML frontmatter (pass_to_pass)."""
    script = '''
import re
import sys
from pathlib import Path

skill_dirs = [
    ".github/skills/pr-build-status",
    ".github/skills/try-fix",
    ".github/skills/pr-finalize",
]

errors = []
for skill_dir in skill_dirs:
    skill_md = Path(skill_dir) / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{skill_md} does not exist")
        continue

    content = skill_md.read_text()

    # Check for YAML frontmatter
    if not content.startswith("---"):
        errors.append(f"{skill_md}: Missing YAML frontmatter")
        continue

    # Extract frontmatter
    end_idx = content.find("---", 3)
    if end_idx == -1:
        errors.append(f"{skill_md}: Invalid YAML frontmatter (no closing ---)")
        continue

    frontmatter = content[3:end_idx]

    # Check required fields
    if "name:" not in frontmatter:
        errors.append(f"{skill_md}: Missing 'name' field in frontmatter")
    if "description:" not in frontmatter:
        errors.append(f"{skill_md}: Missing 'description' field in frontmatter")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: All SKILL.md files have valid YAML frontmatter")
'''
    script_path = "/tmp/skill_yaml_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SKILL.md YAML validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates copilot-instructions.md structure
def test_copilot_instructions_structure():
    """copilot-instructions.md has valid structure with numbered skills (pass_to_pass)."""
    script = '''
import re
import sys
from pathlib import Path

path = Path(".github/copilot-instructions.md")
if not path.exists():
    print("FAIL: copilot-instructions.md does not exist")
    sys.exit(1)

content = path.read_text()

# Check for required sections
errors = []
if "## Skills" not in content:
    errors.append("Missing '## Skills' section")

# Check that skills are numbered (at least some numbered skills exist)
skill_pattern = r"^\\s*(\\d+)\\.\\s+\\*\\*"
skills_found = re.findall(skill_pattern, content, re.MULTILINE)
if len(skills_found) < 5:
    errors.append(f"Expected at least 5 numbered skills, found {len(skills_found)}")

# Check for consistent skill format (numbered list with bold name)
for i, num in enumerate(skills_found[:5], 1):
    if int(num) != i:
        errors.append(f"Skill numbering should start at 1 and increment, found {num} at position {i}")
        break

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: copilot-instructions.md has valid structure")
'''
    script_path = "/tmp/copilot_structure_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"copilot-instructions structure check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates PowerShell scripts have proper structure
def test_powershell_scripts_structure():
    """Existing PowerShell scripts have proper param() and ErrorActionPreference (pass_to_pass)."""
    script = '''
import re
import sys
from pathlib import Path

# Check existing PowerShell scripts that are in the repo at base commit
ps1_files = [
    ".github/skills/pr-build-status/scripts/Get-PrBuildIds.ps1",
    ".github/skills/pr-build-status/scripts/Get-BuildInfo.ps1",
]

errors = []
for ps1_path in ps1_files:
    path = Path(ps1_path)
    if not path.exists():
        errors.append(f"{ps1_path} does not exist")
        continue

    content = path.read_text()

    # Check for param() block
    if "param(" not in content:
        errors.append(f"{ps1_path}: Missing param() block")

    # Check for ErrorActionPreference
    if "ErrorActionPreference" not in content:
        errors.append(f"{ps1_path}: Missing ErrorActionPreference setting")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: All PowerShell scripts have proper structure")
'''
    script_path = "/tmp/ps1_structure_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PowerShell scripts structure check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates gitattributes has required settings
def test_gitattributes_content():
    """.gitattributes has required settings for line endings and binary files (pass_to_pass)."""
    script = '''
import sys
from pathlib import Path

path = Path(".gitattributes")
if not path.exists():
    print("FAIL: .gitattributes does not exist")
    sys.exit(1)

content = path.read_text()
errors = []

# Check for line ending handling
if "text=auto" not in content and "* text" not in content:
    errors.append("Missing line ending configuration")

# Check for binary file handling (at least one binary pattern)
binary_patterns = ["*.png", "*.jpg", "*.gif", "*.dll", "*.exe", "binary"]
if not any(pattern in content for pattern in binary_patterns):
    errors.append("Missing binary file configuration")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: .gitattributes has required settings")
'''
    script_path = "/tmp/gitattributes_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f".gitattributes content check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates editorconfig has required settings
def test_editorconfig_content():
    """.editorconfig has required settings for C# and other files (pass_to_pass)."""
    script = '''
import sys
from pathlib import Path

path = Path(".editorconfig")
if not path.exists():
    print("FAIL: .editorconfig does not exist")
    sys.exit(1)

content = path.read_text()
errors = []

# Check for root = true
if "root = true" not in content:
    errors.append("Missing 'root = true'")

# Check for C# settings
if "[*.cs]" not in content:
    errors.append("Missing C# (*.cs) settings section")

# Check for indent settings
if "indent" not in content.lower():
    errors.append("Missing indent settings")

if errors:
    print("ERRORS:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: .editorconfig has required settings")
'''
    script_path = "/tmp/editorconfig_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f".editorconfig content check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Additional repo_tests - Real CI Commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - validates NuGet.config XML via Python subprocess
def test_nuget_config_xml_valid():
    """NuGet.config is valid XML with proper structure (pass_to_pass via subprocess)."""
    r = subprocess.run(
        ["python3", "-c",
         "import xml.etree.ElementTree as ET; ET.parse('NuGet.config'); print('VALID XML')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"NuGet.config XML validation failed:\n{r.stderr}"
    assert "VALID XML" in r.stdout


# [repo_tests] pass_to_pass - validates global.json JSON via Python subprocess
def test_global_json_valid_parse():
    """global.json is valid JSON with SDK config (pass_to_pass via subprocess)."""
    r = subprocess.run(
        ["python3", "-c",
         "import json; d=json.load(open('global.json')); assert 'tools' in d; print('VALID JSON')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"global.json JSON validation failed:\n{r.stderr}"
    assert "VALID JSON" in r.stdout


# [repo_tests] pass_to_pass - validates Directory.Build.props XML
def test_directory_build_props_xml_valid():
    """Directory.Build.props is valid XML (pass_to_pass via subprocess)."""
    r = subprocess.run(
        ["python3", "-c",
         "import xml.etree.ElementTree as ET; ET.parse('Directory.Build.props'); print('VALID XML')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Directory.Build.props XML validation failed:\n{r.stderr}"
    assert "VALID XML" in r.stdout


# [repo_tests] pass_to_pass - validates key csproj files XML
def test_key_csproj_files_xml_valid():
    """Key .csproj files are valid XML (pass_to_pass via subprocess)."""
    script = '''
import xml.etree.ElementTree as ET
import sys
from pathlib import Path

key_files = [
    "src/TestUtils/src/Microsoft.Maui.IntegrationTests/Microsoft.Maui.IntegrationTests.csproj",
]

errors = []
for fpath in key_files:
    path = Path(fpath)
    if not path.exists():
        errors.append(f"{fpath}: File not found")
        continue
    try:
        ET.parse(path)
    except ET.ParseError as e:
        errors.append(f"{fpath}: {e}")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print(f"PASS: All {len(key_files)} key .csproj files are valid XML")
'''
    script_path = "/tmp/csproj_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"csproj XML validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates git repository has proper structure
def test_git_repo_structure():
    """Git repository has expected files and structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-tree", "-r", "HEAD", "--name-only"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git ls-tree failed:\n{r.stderr}"

    files = r.stdout.strip().split("\n")
    required_files = [
        "global.json",
        "NuGet.config",
        "Microsoft.Maui.sln",
        ".editorconfig",
        ".gitattributes",
    ]

    missing = [f for f in required_files if f not in files]
    assert not missing, f"Required files missing from git: {missing}"


# [repo_tests] pass_to_pass - validates C# files have balanced braces (lightweight syntax check)
def test_cs_files_balanced_braces():
    """Key C# files have balanced braces (pass_to_pass via subprocess)."""
    script = '''
import sys
from pathlib import Path

key_files = [
    "src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs",
]

errors = []
for fpath in key_files:
    path = Path(fpath)
    if not path.exists():
        errors.append(f"{fpath}: File not found")
        continue

    content = path.read_text()
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_parens = content.count('(')
    close_parens = content.count(')')

    if open_braces != close_braces:
        errors.append(f"{fpath}: Unbalanced braces ({open_braces} open, {close_braces} close)")
    if open_parens != close_parens:
        errors.append(f"{fpath}: Unbalanced parens ({open_parens} open, {close_parens} close)")

if errors:
    for e in errors:
        print(f"ERROR: {e}")
    sys.exit(1)

print(f"PASS: All {len(key_files)} C# files have balanced delimiters")
'''
    script_path = "/tmp/cs_syntax_check.py"
    with open(script_path, "w") as f:
        f.write(script)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"C# syntax check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - validates solution file structure
def test_solution_file_structure():
    """Microsoft.Maui.sln has valid structure (pass_to_pass via subprocess)."""
    r = subprocess.run(
        ["python3", "-c",
         "import re; content=open('Microsoft.Maui.sln').read(); "
         "assert 'Microsoft Visual Studio Solution File' in content; "
         "assert 'Project(' in content; print('VALID SOLUTION')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Solution file validation failed:\n{r.stderr}"
    assert "VALID SOLUTION" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral code tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_msbuild_isolation_files():
    """Simulate C# runtime: extract embedded XML from BaseBuildTest.cs, write to temp files, parse and validate as MSBuild sentinels."""
    script_content = '''
import re
import xml.etree.ElementTree as ET
import sys
import tempfile
import os

src = open("src/TestUtils/src/Microsoft.Maui.IntegrationTests/BaseBuildTest.cs").read()

# The code must use File.WriteAllText to create isolation files for both props and targets
write_calls = re.findall(r'File\\.WriteAllText\\(', src)
if len(write_calls) < 2:
    print(f"FAIL: Expected >=2 File.WriteAllText calls for isolation, found {len(write_calls)}")
    sys.exit(1)

if "Directory.Build.props" not in src:
    print("FAIL: No Directory.Build.props reference in code")
    sys.exit(1)

if "Directory.Build.targets" not in src:
    print("FAIL: No Directory.Build.targets reference in code")
    sys.exit(1)

# Extract C# triple-quoted raw string literals containing <Project>
xml_blocks = re.findall(r'"""(.*?)"""', src, re.DOTALL)
project_xmls = [m.strip() for m in xml_blocks if "<Project>" in m]
if len(project_xmls) < 2:
    print(f"FAIL: Expected >=2 embedded <Project> XML blocks, found {len(project_xmls)}")
    sys.exit(1)

# Simulate runtime behavior: write each XML block to a temp file and parse it,
# just as File.WriteAllText would at C# runtime. This validates the embedded
# XML content actually produces well-formed MSBuild sentinel files.
tmpdir = tempfile.mkdtemp()
filenames = ["Directory.Build.props", "Directory.Build.targets"]
for i, (xml_str, fname) in enumerate(zip(project_xmls, filenames)):
    fpath = os.path.join(tmpdir, fname)
    with open(fpath, "w") as f:
        f.write(xml_str)

    # Parse as XML -- validates the content is well-formed
    tree = ET.parse(fpath)
    root = tree.getroot()
    if root.tag != "Project":
        print(f"FAIL: {fname} root element is '{root.tag}', expected 'Project'")
        sys.exit(1)

    # MSBuild sentinel files must NOT import other targets or define build logic --
    # they should be empty <Project> elements that stop directory traversal
    disallowed = ["Import", "PropertyGroup", "ItemGroup", "Target", "UsingTask"]
    for tag in disallowed:
        if root.find(tag) is not None:
            print(f"FAIL: {fname} contains <{tag}> -- sentinel files must be empty to block inheritance")
            sys.exit(1)

    os.unlink(fpath)

os.rmdir(tmpdir)
print("PASS: MSBuild isolation files are valid empty <Project> sentinels")
'''
    script_path = "/tmp/msbuild_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"MSBuild isolation validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_skill_md_valid():
    """Parse SKILL.md YAML frontmatter and validate required fields and documented categories."""
    script_content = '''
import re
import sys

path = ".github/skills/run-integration-tests/SKILL.md"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: SKILL.md not found at " + path)
    sys.exit(1)

# --- Parse YAML frontmatter ---
if not content.startswith("---"):
    print("FAIL: SKILL.md must start with YAML frontmatter (---)")
    sys.exit(1)

end_idx = content.find("---", 3)
if end_idx == -1:
    print("FAIL: No closing --- for YAML frontmatter")
    sys.exit(1)

frontmatter = content[3:end_idx].strip()

# Parse YAML key-value pairs from frontmatter
yaml_data = {}
for line in frontmatter.split("\\n"):
    line = line.strip()
    if ":" in line:
        key, val = line.split(":", 1)
        yaml_data[key.strip()] = val.strip()

if yaml_data.get("name") != "run-integration-tests":
    print(f"FAIL: Frontmatter 'name' must be 'run-integration-tests', got '{yaml_data.get('name')}'")
    sys.exit(1)

if not yaml_data.get("description"):
    print("FAIL: Frontmatter must contain a non-empty 'description' field")
    sys.exit(1)

# --- Validate categories documented in the body ---
body = content[end_idx + 3:]
required_categories = {"Build", "WindowsTemplates", "macOSTemplates", "Blazor",
                       "MultiProject", "Samples", "AOT", "RunOnAndroid", "RunOniOS"}
missing = {cat for cat in required_categories if cat not in body}
if missing:
    print(f"FAIL: SKILL.md body missing categories: {missing}")
    sys.exit(1)

# --- Validate script reference ---
if "Run-IntegrationTests.ps1" not in body:
    print("FAIL: SKILL.md must reference Run-IntegrationTests.ps1")
    sys.exit(1)

print("PASS: SKILL.md has valid frontmatter and documents all categories")
'''
    script_path = "/tmp/skill_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SKILL.md validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_run_script_valid():
    """Parse Run-IntegrationTests.ps1 structure: extract ValidateSet values, validate param block and parameters."""
    script_content = '''
import re
import sys

path = ".github/skills/run-integration-tests/scripts/Run-IntegrationTests.ps1"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: Run-IntegrationTests.ps1 not found at " + path)
    sys.exit(1)

# --- Must start with a comment block ---
stripped = content.lstrip()
if not (stripped.startswith("#") or stripped.startswith("<#")):
    print("FAIL: Script must start with a comment block")
    sys.exit(1)

# --- Extract and validate [CmdletBinding()] ---
if not re.search(r'\\[CmdletBinding\\(\\)\\]', content):
    print("FAIL: Script must have [CmdletBinding()] attribute")
    sys.exit(1)

# --- Extract and validate param() block ---
if not re.search(r'param\\s*\\(', content):
    print("FAIL: Script must have a param() block")
    sys.exit(1)

# --- Extract ValidateSet values and compare against required categories ---
vs_match = re.search(r'\\[ValidateSet\\(([^)]+)\\)\\]', content)
if not vs_match:
    print("FAIL: Script must have [ValidateSet()] attribute")
    sys.exit(1)

raw_values = vs_match.group(1)
extracted = set(v.strip().strip('"').strip("'") for v in raw_values.split(","))

required_categories = {"Build", "WindowsTemplates", "macOSTemplates", "Blazor",
                       "MultiProject", "Samples", "AOT", "RunOnAndroid", "RunOniOS"}
missing = required_categories - extracted
if missing:
    print(f"FAIL: ValidateSet missing categories: {missing}")
    sys.exit(1)

# --- Validate required switch/string parameters exist in param block ---
required_params = ["SkipBuild", "SkipInstall", "AutoProvision", "MAUI_PACKAGE_VERSION"]
for param in required_params:
    if param not in content:
        print(f"FAIL: Script must have {param} parameter")
        sys.exit(1)

# --- Validate ErrorActionPreference is set to Stop ---
ea_lines = [l for l in content.split("\\n") if "ErrorActionPreference" in l]
if not ea_lines:
    print("FAIL: Script must set ErrorActionPreference")
    sys.exit(1)
if not any("Stop" in l for l in ea_lines):
    print("FAIL: ErrorActionPreference must be set to Stop")
    sys.exit(1)

print("PASS: PowerShell script has valid parameter block with all required categories")
'''
    script_path = "/tmp/script_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PowerShell script validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation update tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_copilot_instructions_lists_integration_skill():
    """Parse copilot-instructions.md: extract numbered skill list and validate run-integration-tests entry."""
    script_content = '''
import re
import sys

content = open(".github/copilot-instructions.md").read()

# --- Parse numbered skill entries: N. **name** (path) ---
entries = re.findall(r'(\\d+)\\.\\s+\\*\\*([^*]+)\\*\\*\\s*\\(([^)]+)\\)', content)
skill_names = [name for _, name, _ in entries]

if "run-integration-tests" not in skill_names:
    print(f"FAIL: run-integration-tests not found in numbered skill list. Found: {skill_names}")
    sys.exit(1)

# Find the entry and validate its path
rit_entries = [(num, name, path) for num, name, path in entries if name == "run-integration-tests"]
_, _, rit_path = rit_entries[0]
if ".github/skills/run-integration-tests/SKILL.md" not in rit_path:
    print(f"FAIL: run-integration-tests path must reference SKILL.md, got: {rit_path}")
    sys.exit(1)

# Validate "ALWAYS use this skill" directive
if "ALWAYS use this skill" not in content:
    print("FAIL: Must include 'ALWAYS use this skill' directive")
    sys.exit(1)

print("PASS: copilot-instructions.md has valid run-integration-tests skill entry")
'''
    script_path = "/tmp/copilot_skill_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"copilot-instructions skill validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_integration_instructions_references_skill():
    """Validate integration-tests.instructions.md references the run-integration-tests skill and script."""
    script_content = '''
import sys

content = open(".github/instructions/integration-tests.instructions.md").read()

if "run-integration-tests" not in content:
    print("FAIL: Must reference run-integration-tests skill")
    sys.exit(1)

if "Run-IntegrationTests.ps1" not in content:
    print("FAIL: Must reference Run-IntegrationTests.ps1")
    sys.exit(1)

if "ALWAYS" not in content:
    print("FAIL: Must instruct to ALWAYS use the skill")
    sys.exit(1)

print("PASS: integration-tests.instructions.md references skill correctly")
'''
    script_path = "/tmp/integration_ref_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"integration-tests.instructions validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_copilot_instructions_skill_numbering():
    """Parse skill numbering: run-integration-tests must be numbered and appear before try-fix."""
    script_content = '''
import re
import sys

content = open(".github/copilot-instructions.md").read()

# Extract all numbered skill entries with their numbers
entries = re.findall(r'(\\d+)\\.\\s+\\*\\*([^*]+)\\*\\*', content)
skill_map = {name: int(num) for num, name in entries}

if "run-integration-tests" not in skill_map:
    print(f"FAIL: run-integration-tests not in numbered list. Found: {list(skill_map.keys())}")
    sys.exit(1)

if "try-fix" not in skill_map:
    print(f"FAIL: try-fix not in numbered list. Found: {list(skill_map.keys())}")
    sys.exit(1)

rit_num = skill_map["run-integration-tests"]
tf_num = skill_map["try-fix"]

if rit_num >= tf_num:
    print(f"FAIL: run-integration-tests (#{rit_num}) must be numbered before try-fix (#{tf_num})")
    sys.exit(1)

# Verify run-integration-tests appears before try-fix in file order
rit_pos = content.find("run-integration-tests")
tf_pos = content.find("try-fix")
if rit_pos >= tf_pos:
    print("FAIL: run-integration-tests must appear before try-fix in the file")
    sys.exit(1)

print(f"PASS: Skill numbering valid (run-integration-tests=#{rit_num}, try-fix=#{tf_num})")
'''
    script_path = "/tmp/skill_numbering_check.py"
    with open(script_path, "w") as f:
        f.write(script_content)

    r = subprocess.run(
        ["python3", script_path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Skill numbering validation failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
