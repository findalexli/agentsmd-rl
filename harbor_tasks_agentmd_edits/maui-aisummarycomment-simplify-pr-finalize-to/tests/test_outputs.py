"""
Task: maui-aisummarycomment-simplify-pr-finalize-to
Repo: dotnet/maui @ fce7eca39b449e508cc76873c213a6fb79564f33
PR:   33771

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"
SCRIPT = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1"
SKILL_MD = Path(REPO) / ".github/skills/ai-summary-comment/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests on the script
# ---------------------------------------------------------------------------

def test_review_number_param_removed():
    """ReviewNumber and ReviewDescription parameters must be removed."""
    content = SCRIPT.read_text()
    # The param block should NOT contain ReviewNumber or ReviewDescription
    # Match the parameter declarations (not just any mention in comments)
    param_block_match = re.search(r'(?s)param\s*\((.*?)\)', content)
    assert param_block_match, "Could not find param() block in script"
    param_block = param_block_match.group(1)
    assert "ReviewNumber" not in param_block, \
        "ReviewNumber parameter should be removed from param block"
    assert "ReviewDescription" not in param_block, \
        "ReviewDescription parameter should be removed from param block"


def test_title_issues_param_added():
    """New TitleIssues parameter must be declared."""
    content = SCRIPT.read_text()
    param_block_match = re.search(r'(?s)param\s*\((.*?)\)', content)
    assert param_block_match, "Could not find param() block in script"
    param_block = param_block_match.group(1)
    assert "TitleIssues" in param_block, \
        "TitleIssues parameter should be added to param block"


def test_two_section_format():
    """Comment body must use separate Title and Description collapsible sections."""
    content = SCRIPT.read_text()
    # Should NOT build a single $reviewSection anymore
    assert "$reviewSection" not in content, \
        "Script should not use single $reviewSection variable"
    # The summary lines should show "Title:" and "Description:" not "Review N:"
    assert re.search(r'<summary><b>Title:', content), \
        "Title section should have <summary><b>Title: header"
    assert re.search(r'<summary><b>Description:', content), \
        "Description section should have <summary><b>Description: header"


def test_no_review_numbered_sections():
    """Old Review N: numbered section pattern must be removed."""
    content = SCRIPT.read_text()
    # Should NOT have "Review $ReviewNumber" or "Review (\d+):" in the output-building code
    # Exclude comment blocks (.DESCRIPTION, .EXAMPLE) — check only the code body
    # Find where param() block ends and code begins
    param_end = content.find("param(")
    if param_end != -1:
        # Find the matching close paren — rough heuristic: find code after the big param block
        code_section = content[content.find("\n)", param_end):]
    else:
        code_section = content
    # The review-merging regex pattern should be gone
    assert "Review (\\d+):" not in code_section and \
           "'(?s)<details>\\s*<summary><b>Review" not in code_section, \
        "Old review-merging regex pattern should be removed"


def test_overall_status_removed():
    """The $overallStatus variable computation must be removed."""
    content = SCRIPT.read_text()
    # Should not compute or use $overallStatus
    assert "$overallStatus" not in content, \
        "$overallStatus variable should be removed from script"






# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md documentation update
# ---------------------------------------------------------------------------


    # Must mention Title and Description as the two sections
    assert "Title" in finalize_section and "Description" in finalize_section, \
        "SKILL.md finalization section should mention both Title and Description sections"
    # Must NOT still describe numbered reviews
    assert "Review 1" not in finalize_section and "Review 2" not in finalize_section, \
        "SKILL.md should not reference numbered reviews (Review 1, Review 2)"
    # Should mention replacement behavior
    assert "replaced" in finalize_section.lower() or "replace" in finalize_section.lower(), \
        "SKILL.md should document that existing finalize comment is replaced"




# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural sanity
# ---------------------------------------------------------------------------

def test_script_has_param_block():
    """Script must still have a valid param() declaration block."""
    content = SCRIPT.read_text()
    assert re.search(r'param\s*\(', content), "Script must have param() block"
    # Must still have core params
    assert "PRNumber" in content, "PRNumber param must still exist"
    assert "SummaryFile" in content, "SummaryFile param must still exist"
    assert "TitleStatus" in content, "TitleStatus param must still exist"
    assert "DescriptionStatus" in content, "DescriptionStatus param must still exist"
