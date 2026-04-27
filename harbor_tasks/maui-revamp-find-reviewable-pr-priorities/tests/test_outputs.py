"""
Task: maui-revamp-find-reviewable-pr-priorities
Repo: dotnet/maui @ 48dae02e3e04dce551396f747f234bf3e30801ec
PR:   34160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/maui"
SCRIPT = Path(REPO) / ".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1"
SKILL_MD = Path(REPO) / ".github/skills/find-reviewable-pr/SKILL.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script via subprocess in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_script_file_exists():
    """PowerShell script and SKILL.md must exist."""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"
    assert SKILL_MD.exists(), f"SKILL.md not found: {SKILL_MD}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - structural validation of repo files
# ---------------------------------------------------------------------------

def test_repo_powershell_script_structure():
    """PowerShell script has valid structure with param block and required functions (pass_to_pass)."""
    r = _run_py(r"""
import re
import sys

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()
errors = []

# Check for param block
if not re.search(r'param\s*\(', content):
    errors.append("Missing param() block")

# Check for required functions
required_funcs = ["Invoke-GitHubWithRetry", "Add-UniquePRs", "Get-ReviewStatus",
                  "Get-ProjectStatus", "Get-PRCategory", "Get-PRComplexity"]
found_funcs = re.findall(r'function\s+([\w-]+)', content)
for func in required_funcs:
    if func not in found_funcs:
        errors.append(f"Missing required function: {func}")

# Check for ValidateSet in param block (indicates proper parameter validation)
if "[ValidateSet(" not in content:
    errors.append("Missing ValidateSet parameter validation")

# Check for ErrorActionPreference
if "$ErrorActionPreference" not in content:
    errors.append("Missing ErrorActionPreference setting")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("PowerShell script structure valid")
""")
    assert r.returncode == 0, f"PowerShell script structure validation failed:\n{r.stdout}{r.stderr}"


def test_repo_skill_md_structure():
    """SKILL.md has valid documentation structure (pass_to_pass)."""
    r = _run_py(r"""
import re
import sys

content = open(".github/skills/find-reviewable-pr/SKILL.md").read()
errors = []

# Check for required sections
required_sections = ["## Priority Categories", "## Quick Start", "## Script Parameters"]
for section in required_sections:
    if section not in content:
        errors.append(f"Missing section: {section}")

# Check for parameter table structure
if "| Parameter |" not in content:
    errors.append("Missing parameter table")

# Check for example bash commands (indicates usage documentation)
if "```bash" not in content:
    errors.append("Missing bash example blocks")

# Check for proper category listings
if "P/0" not in content and "Priority" not in content:
    errors.append("Missing P/0 priority category documentation")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("SKILL.md structure valid")
""")
    assert r.returncode == 0, f"SKILL.md structure validation failed:\n{r.stdout}{r.stderr}"


def test_repo_powershell_no_syntax_errors():
    """PowerShell script has no obvious syntax errors (pass_to_pass)."""
    r = _run_py(r"""
import re
import sys

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()
errors = []

# Check for balanced braces/parens in param block
param_match = re.search(r'param\s*\((.*?)\n\)', content, re.DOTALL)
if param_match:
    param_block = param_match.group(1)
    open_parens = param_block.count('(')
    close_parens = param_block.count(')')
    open_braces = param_block.count('{')
    close_braces = param_block.count('}')
    if open_parens != close_parens:
        errors.append(f"Unbalanced parentheses in param block: {open_parens} vs {close_parens}")

# Check for unclosed comment blocks
open_comments = content.count('<#')
close_comments = content.count('#>')
if open_comments != close_comments:
    errors.append(f"Unbalanced comment blocks: <#={open_comments}, #>={close_comments}")

# Check for unclosed strings (odd number of unescaped quotes on key lines)
lines = content.split('\n')
for i, line in enumerate(lines[:100], 1):  # Check first 100 lines
    # Skip comment lines
    if line.strip().startswith('#'):
        continue
    # Count quotes (rough check for even pairs)
    quotes = line.count('"') - line.count('\""')  # Subtract escaped quotes
    if quotes % 2 != 0 and 'Write-Host' in line:
        errors.append(f"Line {i} may have unclosed string: {line[:60]}")

if errors:
    print("\n".join(errors[:10]))  # Limit errors
    sys.exit(1)
print("No obvious PowerShell syntax errors detected")
""")
    assert r.returncode == 0, f"PowerShell syntax check failed:\n{r.stdout}{r.stderr}"


def test_repo_files_encoding_and_size():
    """Repo files are valid (readable, non-empty) (pass_to_pass)."""
    r = _run_py(r"""
import sys
from pathlib import Path

script = Path(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1")
skill = Path(".github/skills/find-reviewable-pr/SKILL.md")

errors = []

# Check script
if not script.exists():
    errors.append("Script file does not exist")
else:
    content = script.read_text(encoding='utf-8')
    if len(content) < 1000:
        errors.append(f"Script too small ({len(content)} chars)")
    if '\x00' in content:
        errors.append("Script contains null bytes (binary file?)")

# Check SKILL.md
if not skill.exists():
    errors.append("SKILL.md does not exist")
else:
    content = skill.read_text(encoding='utf-8')
    if len(content) < 500:
        errors.append(f"SKILL.md too small ({len(content)} chars)")
    if '# ' not in content:
        errors.append("SKILL.md missing header")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("Files encoding and size valid")
""")
    assert r.returncode == 0, f"File validation failed:\n{r.stdout}{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - PowerShell script changes
# ---------------------------------------------------------------------------

def test_script_param_defaults():
    """Parse param block and verify Category='default' and Limit=100."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()

# Extract param(...) block
param_match = re.search(r'param\s*\((.*?)^\)', content, re.DOTALL | re.MULTILINE)
assert param_match, "No param() block found"
param_block = param_match.group(1)

# $Category default
cat_match = re.search(r'\$Category\s*=\s*"([\w-]+)"', param_block)
assert cat_match, "No $Category default in param block"

# $Limit default
limit_match = re.search(r'\$Limit\s*=\s*(\d+)', param_block)
assert limit_match, "No $Limit default in param block"

print(json.dumps({"category": cat_match.group(1), "limit": int(limit_match.group(1))}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["category"] == "default", \
        f"Category default should be 'default', got '{data['category']}'"
    assert data["limit"] == 100, \
        f"Limit default should be 100, got {data['limit']}"


def test_script_validate_set_has_new_categories():
    """ValidateSet for Category must include default, approved, ready-to-review, agent-reviewed."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()

# Find ValidateSet before $Category
vs_match = re.search(
    r'\[ValidateSet\((.*?)\)\].*?\$Category',
    content, re.DOTALL
)
assert vs_match, "No ValidateSet for $Category found"

# Extract all quoted values
categories = re.findall(r'"([\w-]+)"', vs_match.group(1))
print(json.dumps({"categories": categories}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    cats = [c.lower() for c in data["categories"]]
    for required in ["default", "approved", "ready-to-review", "agent-reviewed"]:
        assert required in cats, \
            f"ValidateSet missing '{required}', found: {cats}"


def test_script_new_functions_and_fields():
    """Script includes Assignees field in PR objects, project board GraphQL query, and agent labels."""
    # Use subprocess to structurally validate that PSCustomObject blocks contain Assignees
    r = subprocess.run(
        ["python3", "-c",
         "import re, sys; c = open(sys.argv[1]).read(); "
         "objs = re.findall(r'\\[PSCustomObject\\]@\\{(.*?)\\}', c, re.DOTALL); "
         "print('FOUND' if any('Assignees' in o for o in objs) else 'MISSING')",
         str(SCRIPT)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Assignees check failed: {r.stderr}"
    assert "FOUND" in r.stdout, \
        "Must include 'Assignees' field in PSCustomObject PR entries"

    content = SCRIPT.read_text()

    # Script must query GitHub ProjectV2 API for project board integration
    assert "ProjectV2" in content, \
        "Must have GraphQL ProjectV2 query for Ready To Review project board feature"

    # Script must reference agent review labels
    assert "s/agent-reviewed" in content, "Must reference 's/agent-reviewed' label"
    assert "s/agent-approved" in content, "Must reference 's/agent-approved' label"


def test_script_default_mode_logic():
    """Script implements 'default' category case that combines P/0 + milestoned and filters CHANGES_REQUESTED."""
    # Use subprocess to parse the switch block and verify 'default' case exists
    r = subprocess.run(
        ["python3", "-c",
         "import re, json, sys; c = open(sys.argv[1]).read(); "
         "has_default = bool(re.search(r'\"default\"\\s*\\{', c)); "
         "has_filter = 'CHANGES_REQUESTED' in c; "
         "print(json.dumps({'default_case': has_default, 'changes_filter': has_filter}))",
         str(SCRIPT)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["default_case"], \
        "Script must have a '\"default\"' case in category switch handling"
    assert data["changes_filter"], \
        "Script must filter CHANGES_REQUESTED PRs in default mode"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - SKILL.md documentation
# ---------------------------------------------------------------------------

def test_skill_md_priority_categories():
    """SKILL.md Priority Categories section must list 9 categories."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/SKILL.md").read()

# Find Priority Categories section
cats_match = re.search(
    r'## Priority Categories.*?\n(.*?)(?=\n## )',
    content, re.DOTALL
)
assert cats_match, "No 'Priority Categories' section found"
cats_text = cats_match.group(1)

# Count numbered items
numbered = re.findall(r'^\d+\.', cats_text, re.MULTILINE)

# Check for key new categories in that section
has_approved = "Approved" in cats_text and "Not Merged" in cats_text
has_agent = "Agent Reviewed" in cats_text
has_ready = "Ready To Review" in cats_text

print(json.dumps({
    "count": len(numbered),
    "has_approved": has_approved,
    "has_agent": has_agent,
    "has_ready": has_ready,
}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] >= 9, \
        f"Expected >= 9 priority categories, found {data['count']}"
    assert data["has_approved"], "Must list 'Approved (Not Merged)' category"
    assert data["has_agent"], "Must list 'Agent Reviewed' category"
    assert data["has_ready"], "Must list 'Ready To Review' category"


def test_skill_md_param_table_defaults():
    """SKILL.md parameter table shows Category='default' and Limit=100."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/SKILL.md").read()

# Extract -Category row
cat_row = re.search(r'\|\s*`-Category`\s*\|([^|]+)\|([^|]+)\|', content)
assert cat_row, "No -Category row in parameter table"

# Extract -Limit row
limit_row = re.search(r'\|\s*`-Limit`\s*\|([^|]+)\|([^|]+)\|', content)
assert limit_row, "No -Limit row in parameter table"

print(json.dumps({
    "cat_default": cat_row.group(2).strip(),
    "limit_default": limit_row.group(2).strip(),
}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "default" in data["cat_default"].lower(), \
        f"Category default should be 'default', got '{data['cat_default']}'"
    assert "100" in data["limit_default"], \
        f"Limit default should be '100', got '{data['limit_default']}'"


def test_skill_md_new_category_docs():
    """SKILL.md documents Approved, Agent Reviewed, Ready To Review, and Assignees column."""
    r = _run_py(r"""
import json

content = open(".github/skills/find-reviewable-pr/SKILL.md").read()

print(json.dumps({
    "has_approved": "Approved" in content and "Not Merged" in content,
    "has_agent_reviewed": "Agent Reviewed" in content,
    "has_ready_to_review": "Ready To Review" in content,
    "has_assignees": "Assignees" in content,
}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_approved"], "Must document 'Approved (Not Merged)' category"
    assert data["has_agent_reviewed"], "Must document 'Agent Reviewed' category"
    assert data["has_ready_to_review"], "Must document 'Ready To Review' category"
    assert data["has_assignees"], "Must mention Assignees column"
