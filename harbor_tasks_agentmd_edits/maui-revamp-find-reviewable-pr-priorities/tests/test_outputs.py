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
# Fail-to-pass (pr_diff) — PowerShell script changes
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
    """Script defines Write-PREntry, Get-ReadyToReviewPRNumbers, has Assignees and agent labels."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()

# Extract all function definitions
functions = re.findall(r'function\s+([\w-]+)', content)

# Check for Assignees in PSCustomObject blocks
has_assignees = bool(re.search(r'Assignees\s*=', content))

# Check for agent label references
has_agent_reviewed = "s/agent-reviewed" in content
has_agent_approved = "s/agent-approved" in content

print(json.dumps({
    "functions": functions,
    "has_assignees": has_assignees,
    "has_agent_reviewed": has_agent_reviewed,
    "has_agent_approved": has_agent_approved,
}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "Write-PREntry" in data["functions"], \
        f"Must define Write-PREntry function, found: {data['functions']}"
    assert "Get-ReadyToReviewPRNumbers" in data["functions"], \
        f"Must define Get-ReadyToReviewPRNumbers function, found: {data['functions']}"
    assert data["has_assignees"], "Must include 'Assignees =' in PSCustomObject"
    assert data["has_agent_reviewed"], "Must reference 's/agent-reviewed' label"
    assert data["has_agent_approved"], "Must reference 's/agent-approved' label"


def test_script_default_mode_logic():
    """Script implements 'default' mode showing P/0 + milestoned, filtering CHANGES_REQUESTED."""
    r = _run_py(r"""
import re, json

content = open(".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1").read()

# Check for "default" case in switch statement
has_default_case = bool(re.search(r'"default"\s*\{', content))

# Check for $defaultPRs variable (merges P/0 + milestoned in default mode)
has_default_prs_var = bool(re.search(r'\$defaultPRs', content))

# Check for CHANGES_REQUESTED filtering
has_changes_requested_filter = "CHANGES_REQUESTED" in content

print(json.dumps({
    "has_default_case": has_default_case,
    "has_default_prs_var": has_default_prs_var,
    "has_changes_requested_filter": has_changes_requested_filter,
}))
""")
    assert r.returncode == 0, f"Parse failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["has_default_case"], \
        "Script must have 'default' case in category switch"
    assert data["has_default_prs_var"], \
        "Default mode must use $defaultPRs to merge P/0 + milestoned PRs"
    assert data["has_changes_requested_filter"], \
        "Default mode must filter CHANGES_REQUESTED PRs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md documentation
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
