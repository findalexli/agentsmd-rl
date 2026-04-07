"""
Task: maui-revamp-find-reviewable-pr-priorities
Repo: dotnet/maui @ 48dae02e3e04dce551396f747f234bf3e30801ec
PR:   34160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/maui"
SCRIPT = Path(REPO) / ".github/skills/find-reviewable-pr/scripts/query-reviewable-prs.ps1"
SKILL_MD = Path(REPO) / ".github/skills/find-reviewable-pr/SKILL.md"


# ---------------------------------------------------------------------------
# Helper: extract param block from PowerShell script using regex
# ---------------------------------------------------------------------------

def _read_script():
    return SCRIPT.read_text()


def _read_skill_md():
    return SKILL_MD.read_text()


def _extract_param_block(content: str) -> str:
    """Extract the param(...) block from the PowerShell script."""
    match = re.search(r'param\s*\((.*?)\)', content, re.DOTALL)
    assert match, "Could not find param() block in script"
    return match.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_script_file_exists():
    """PowerShell script and SKILL.md must exist."""
    assert SCRIPT.exists(), f"Script not found: {SCRIPT}"
    assert SKILL_MD.exists(), f"SKILL.md not found: {SKILL_MD}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — script parameter changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_script_default_category_is_default():
    """Script -Category default must be 'default', not 'all'."""
    content = _read_script()
    param_block = _extract_param_block(content)
    # Find the Category parameter default value
    cat_match = re.search(
        r'\$Category\s*=\s*"(\w+)"', param_block
    )
    assert cat_match, "Could not find $Category default in param block"
    assert cat_match.group(1) == "default", \
        f"Category default should be 'default', got '{cat_match.group(1)}'"


# [pr_diff] fail_to_pass
def test_script_default_limit_is_100():
    """Script -Limit default must be 100, not 10."""
    content = _read_script()
    param_block = _extract_param_block(content)
    limit_match = re.search(r'\$Limit\s*=\s*(\d+)', param_block)
    assert limit_match, "Could not find $Limit default in param block"
    assert int(limit_match.group(1)) == 100, \
        f"Limit default should be 100, got {limit_match.group(1)}"


# [pr_diff] fail_to_pass
def test_script_validate_set_has_new_categories():
    """Script ValidateSet for Category must include approved, ready-to-review, agent-reviewed, default."""
    content = _read_script()
    # Find the ValidateSet before $Category
    vs_match = re.search(
        r'\[ValidateSet\((.*?)\)\]\s*\n\s*\[string\]\$Category',
        content, re.DOTALL
    )
    assert vs_match, "Could not find ValidateSet for $Category"
    vs_content = vs_match.group(1).lower()
    for cat in ["default", "approved", "ready-to-review", "agent-reviewed"]:
        assert f'"{cat}"' in vs_content, \
            f"ValidateSet missing category '{cat}'"


# [pr_diff] fail_to_pass
def test_script_has_assignees_field():
    """Script must include Assignees in the processed PR objects."""
    content = _read_script()
    assert re.search(r'Assignees\s*=', content), \
        "Script should have 'Assignees =' in PSCustomObject"


# [pr_diff] fail_to_pass
def test_script_queries_agent_reviewed_prs():
    """Script must query for agent-reviewed PRs via label search."""
    content = _read_script()
    assert "s/agent-reviewed" in content, \
        "Script should search for 'label:s/agent-reviewed'"
    assert "s/agent-approved" in content, \
        "Script should search for 'label:s/agent-approved'"


# [pr_diff] fail_to_pass
def test_script_has_write_pr_entry_helper():
    """Script must have a Write-PREntry helper function to avoid repetition."""
    content = _read_script()
    assert re.search(r'function\s+Write-PREntry\b', content), \
        "Script should define Write-PREntry helper function"


# [pr_diff] fail_to_pass
def test_script_has_default_mode_logic():
    """Script must implement 'default' mode that shows only P/0 + milestoned."""
    content = _read_script()
    # Check for the default case in the switch statement
    assert re.search(r'"default"\s*\{', content), \
        "Script should have a 'default' case in the category switch"
    # Verify it filters changes-requested
    assert "CHANGES_REQUESTED" in content, \
        "Default mode should filter out CHANGES_REQUESTED PRs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md documentation updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_nine_categories():
    """SKILL.md Priority Categories must list 9 categories (was 6)."""
    content = _read_skill_md()
    # Find the priority categories section
    cats_match = re.search(
        r'## Priority Categories.*?\n(.*?)(?=\n## )', content, re.DOTALL
    )
    assert cats_match, "Could not find 'Priority Categories' section in SKILL.md"
    cats_text = cats_match.group(1)
    numbered_items = re.findall(r'^\d+\.', cats_text, re.MULTILINE)
    assert len(numbered_items) >= 9, \
        f"Expected 9 priority categories, found {len(numbered_items)}"


# [pr_diff] fail_to_pass
def test_skill_md_documents_approved_category():
    """SKILL.md must document the Approved (Not Merged) category."""
    content = _read_skill_md()
    assert "Approved" in content and "Not Merged" in content, \
        "SKILL.md should document 'Approved (Not Merged)' category"


# [pr_diff] fail_to_pass
def test_skill_md_documents_agent_reviewed():
    """SKILL.md must document the Agent Reviewed category."""
    content = _read_skill_md()
    assert "Agent Reviewed" in content, \
        "SKILL.md should document 'Agent Reviewed' category"


# [pr_diff] fail_to_pass
def test_skill_md_default_category_value():
    """SKILL.md parameter table must show 'default' as the Category default value."""
    content = _read_skill_md()
    # Look in the parameter table for -Category row
    table_match = re.search(
        r'\|\s*`-Category`\s*\|([^|]+)\|([^|]+)\|',
        content
    )
    assert table_match, "Could not find -Category row in parameter table"
    default_val = table_match.group(2).strip()
    assert "default" in default_val.lower(), \
        f"Category default should be 'default', got '{default_val}'"


# [pr_diff] fail_to_pass
def test_skill_md_limit_default_100():
    """SKILL.md parameter table must show Limit default as 100."""
    content = _read_skill_md()
    table_match = re.search(
        r'\|\s*`-Limit`\s*\|([^|]+)\|([^|]+)\|',
        content
    )
    assert table_match, "Could not find -Limit row in parameter table"
    default_val = table_match.group(2).strip()
    assert "100" in default_val, \
        f"Limit default should be '100', got '{default_val}'"


# [pr_diff] fail_to_pass
def test_skill_md_step3_includes_assignees_column():
    """SKILL.md Step 3 table columns must include Assignees."""
    content = _read_skill_md()
    # The column list appears after "Each category table should include columns for:"
    assert "Assignees" in content, \
        "SKILL.md should mention Assignees column in Step 3"
