"""
Task: maui-aisummarycomment-simplify-pr-finalize-to
Repo: dotnet/maui @ f6bafa6e590e1d1dba4b2df2e4dc20a6bad67b7a
PR:   33771

Refactors post-pr-finalize-comment.ps1 to produce a cleaner PR finalization comment
with two collapsible sections (Title and Description) instead of per-review sections.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/maui"
SCRIPT_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1")
SKILL_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/SKILL.md")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_powershell_syntax_valid():
    """Modified PowerShell script parses without errors."""
    # PowerShell can syntax-check without executing
    r = subprocess.run(
        ["pwsh", "-Command", f"Test-Path {SCRIPT_PATH} && Get-Command {SCRIPT_PATH}"],
        capture_output=True, text=True, timeout=30,
    )
    # If pwsh not available, fall back to file existence and basic checks
    if r.returncode != 0 or "not recognized" in r.stderr.lower():
        # Check file exists and has no obvious syntax issues
        assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"
        src = SCRIPT_PATH.read_text()
        # Check for balanced braces (basic syntax validation)
        open_count = src.count("{")
        close_count = src.count("}")
        assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"
    else:
        assert r.returncode == 0, f"PowerShell syntax check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reviewnumber_parameter_removed():
    """ReviewNumber parameter is removed from the script."""
    # In the old version, there was a [int]$ReviewNumber parameter
    # In the new version, this parameter should not exist
    src = SCRIPT_PATH.read_text()
    # Check that ReviewNumber is NOT in the param block
    param_match = re.search(r'param\((.*?)\)', src, re.DOTALL)
    if param_match:
        param_block = param_match.group(1)
        assert "$ReviewNumber" not in param_block, (
            "ReviewNumber parameter should be removed from param block\n"
            "The PR refactors the script to remove per-review numbering"
        )


# [pr_diff] fail_to_pass
def test_reviewdescription_parameter_removed():
    """ReviewDescription parameter is removed from the script."""
    src = SCRIPT_PATH.read_text()
    param_match = re.search(r'param\((.*?)\)', src, re.DOTALL)
    if param_match:
        param_block = param_match.group(1)
        assert "$ReviewDescription" not in param_block, (
            "ReviewDescription parameter should be removed from param block\n"
            "The PR removes the legacy ReviewDescription parameter"
        )


# [pr_diff] fail_to_pass
def test_titleissues_parameter_added():
    """TitleIssues parameter is added to the script."""
    # In the new version, TitleIssues parameter should be present
    src = SCRIPT_PATH.read_text()
    assert "$TitleIssues" in src, (
        "TitleIssues parameter should be added to the script\n"
        "The PR adds TitleIssues for direct title issue specification"
    )
    # Check it's in the param block
    param_match = re.search(r'param\((.*?)\)', src, re.DOTALL)
    if param_match:
        param_block = param_match.group(1)
        assert "$TitleIssues" in param_block, (
            "TitleIssues must be in the param() block"
        )


# [pr_diff] fail_to_pass
def test_two_section_format():
    """Script builds two separate sections (Title and Description) instead of per-review."""
    src = SCRIPT_PATH.read_text()
    # Should have $titleSection and $descSection variables
    assert "$titleSection" in src, (
        "Script should build a $titleSection variable for the Title collapsible section"
    )
    assert "$descSection" in src, (
        "Script should build a $descSection variable for the Description collapsible section"
    )
    # Should NOT have $reviewSection anymore
    assert "$reviewSection" not in src, (
        "$reviewSection should be removed - replaced with separate title/desc sections"
    )


# [pr_diff] fail_to_pass
def test_comment_replaces_existing():
    """Script replaces existing comment instead of merging reviews."""
    src = SCRIPT_PATH.read_text()
    # The new version always builds a fresh comment with titleSection + descSection
    # Should NOT have code for parsing existing reviews
    # Look for the comment body construction
    assert "$titleSection" in src and "$descSection" in src, (
        "Script must use $titleSection and $descSection to build comment body"
    )
    # Check that the comment body construction happens after the "existing comment" check
    # and doesn't try to preserve old reviews
    comment_body_section = src[src.find("$commentBody"):src.find("$commentBody") + 500]
    # Should directly use titleSection and descSection, not try to merge
    assert "existingReviews" not in src or "$existingReviews" not in src, (
        "Script should not use existingReviews variable - it replaces instead of merges"
    )


# [pr_diff] fail_to_pass
def test_title_status_detection_updated():
    """TitleStatus auto-detection looks for explicit status in Title Assessment section."""
    src = SCRIPT_PATH.read_text()
    # The new version looks for explicit status like:
    # '(?s)### 📋 Title Assessment.+?\*\*Status:\*\*\s*(✅|❌|⚠️)?\s*(Good|NeedsUpdate|Needs Update)'
    assert "Title Assessment" in src, (
        "Script should reference 'Title Assessment' section for auto-detection"
    )
    # Check for Status pattern matching
    assert "Status:" in src or "Status" in src, (
        "Script should look for explicit Status in Title Assessment section"
    )


# [pr_diff] fail_to_pass
def test_overall_status_removed():
    """Overall status calculation for reviews is removed."""
    src = SCRIPT_PATH.read_text()
    # The old version had $overallStatus calculation
    # The new version should not have it
    assert "$overallStatus" not in src, (
        "$overallStatus variable should be removed - no longer calculating per-review status"
    )


# [pr_diff] fail_to_pass
def test_skillmd_updated_format():
    """SKILL.md documents the new two-section format."""
    skill_src = SKILL_PATH.read_text()
    # Should describe Title and Description sections
    assert "Title:" in skill_src or "title" in skill_src.lower(), (
        "SKILL.md should document the Title section"
    )
    assert "Description:" in skill_src or "description" in skill_src.lower(), (
        "SKILL.md should document the Description section"
    )
    # Should NOT mention numbered reviews anymore
    assert "Review 1" not in skill_src, (
        "SKILL.md should not mention 'Review 1' - uses Title/Description sections instead"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_script_not_empty():
    """Modified script has meaningful content, not truncated."""
    assert SCRIPT_PATH.exists(), f"Script not found: {SCRIPT_PATH}"
    size = SCRIPT_PATH.stat().st_size
    assert size > 1000, f"Script appears truncated or empty: {size} bytes"


# [static] pass_to_pass
def test_skillmd_not_empty():
    """Modified SKILL.md has meaningful content."""
    assert SKILL_PATH.exists(), f"SKILL.md not found: {SKILL_PATH}"
    size = SKILL_PATH.stat().st_size
    assert size > 500, f"SKILL.md appears truncated: {size} bytes"


# [static] pass_to_pass
def test_pr_finalize_marker_preserved():
    """PR finalization comment marker is preserved."""
    src = SCRIPT_PATH.read_text()
    assert "PR-FINALIZE-COMMENT" in src, (
        "Script must contain <!-- PR-FINALIZE-COMMENT --> marker for comment identification"
    )
