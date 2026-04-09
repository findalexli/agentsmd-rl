"""
Task: maui-enhance-prfinalize-skill-with-code
Repo: dotnet/maui @ 64d90e3ca4e83cf44a7a75c5ffa95a3e7c3147b7
PR:   33861

Enhances pr-finalize skill with code review phase and safety rules.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/maui"
REVIEW_PR_PATH = Path(f"{REPO}/.github/scripts/Review-PR.ps1")
POST_FINALIZE_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1")
SKILL_AI_PATH = Path(f"{REPO}/.github/skills/ai-summary-comment/SKILL.md")
SKILL_FINALIZE_PATH = Path(f"{REPO}/.github/skills/pr-finalize/SKILL.md")
COPILOT_INSTRUCTIONS_PATH = Path(f"{REPO}/.github/copilot-instructions.md")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_powershell_syntax_valid():
    """Modified PowerShell scripts parse without errors."""
    # Check that PowerShell files exist and have valid syntax
    assert REVIEW_PR_PATH.exists(), f"Review-PR.ps1 not found: {REVIEW_PR_PATH}"
    assert POST_FINALIZE_PATH.exists(), f"post-pr-finalize-comment.ps1 not found: {POST_FINALIZE_PATH}"

    # Basic syntax validation: check for balanced braces
    for path in [REVIEW_PR_PATH, POST_FINALIZE_PATH]:
        src = path.read_text()
        open_count = src.count("{")
        close_count = src.count("}")
        assert open_count == close_count, f"Unbalanced braces in {path}: {open_count} open, {close_count} close"


# [static] pass_to_pass
def test_files_not_empty():
    """Modified files have meaningful content, not truncated."""
    paths = [REVIEW_PR_PATH, POST_FINALIZE_PATH, SKILL_AI_PATH, SKILL_FINALIZE_PATH, COPILOT_INSTRUCTIONS_PATH]
    for path in paths:
        assert path.exists(), f"File not found: {path}"
        size = path.stat().st_size
        assert size > 500, f"File appears truncated: {path} ({size} bytes)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interactive_parameter_added():
    """Review-PR.ps1 has -Interactive parameter replacing -NoInteractive."""
    src = REVIEW_PR_PATH.read_text()

    # Should have -Interactive parameter
    assert "[switch]$Interactive" in src, (
        "-Interactive parameter not found. The PR inverts the default behavior: "
        "default is now non-interactive, -Interactive enables interactive mode."
    )

    # Should NOT have -NoInteractive parameter
    assert "[switch]$NoInteractive" not in src, (
        "-NoInteractive parameter should be removed and replaced with -Interactive. "
        "The logic is inverted: default is now non-interactive."
    )


# [pr_diff] fail_to_pass
def test_new_phase_parameters_added():
    """Review-PR.ps1 has -RunFinalize and -PostSummaryComment switches."""
    src = REVIEW_PR_PATH.read_text()

    assert "[switch]$RunFinalize" in src, (
        "-RunFinalize parameter not found. This enables Phase 2 (pr-finalize skill) "
        "after the main PR agent review completes."
    )

    assert "[switch]$PostSummaryComment" in src, (
        "-PostSummaryComment parameter not found. This enables Phase 3 (ai-summary-comment skill) "
        "to post combined results after all phases."
    )


# [pr_diff] fail_to_pass
def test_safety_rules_added():
    """Review-PR.ps1 has safety rules about git operations."""
    src = REVIEW_PR_PATH.read_text()

    # Should have CRITICAL git safety rules
    assert "NEVER run ``git checkout``" in src, (
        "Missing CRITICAL safety rule: 'NEVER run git checkout'. "
        "The PR adds safety rules to prevent AI agents from modifying git state."
    )

    assert "NEVER run ``git push``" in src, (
        "Missing CRITICAL safety rule: 'NEVER run git push'. "
        "AI agents must not have permission to push changes."
    )

    # Check for the full safety block
    assert "CRITICAL - NEVER MODIFY GIT STATE" in src, (
        "Missing CRITICAL - NEVER MODIFY GIT STATE header. "
        "This safety warning is required per the PR."
    )


# [pr_diff] fail_to_pass
def test_phase_1_header_updated():
    """Review-PR.ps1 shows 'PHASE 1: PR AGENT REVIEW' instead of 'LAUNCHING COPILOT CLI'."""
    src = REVIEW_PR_PATH.read_text()

    assert "PHASE 1: PR AGENT REVIEW" in src, (
        "Header should show 'PHASE 1: PR AGENT REVIEW' instead of 'LAUNCHING COPILOT CLI'. "
        "This reflects the multi-phase workflow introduced by the PR."
    )

    assert "LAUNCHING COPILOT CLI" not in src, (
        "Old header 'LAUNCHING COPILOT CLI' should be replaced with 'PHASE 1: PR AGENT REVIEW'."
    )


# [pr_diff] fail_to_pass
def test_workflow_display_added():
    """Review-PR.ps1 displays workflow phases when optional switches are enabled."""
    src = REVIEW_PR_PATH.read_text()

    # Should show workflow information
    assert "Workflow:" in src, (
        "Missing 'Workflow:' display section. "
        "The PR adds a workflow summary showing which phases are queued."
    )

    # Should reference the phases
    assert "PR Agent Review (this phase)" in src, (
        "Should reference 'PR Agent Review (this phase)' in workflow display."
    )

    assert "pr-finalize skill (queued)" in src, (
        "Should reference 'pr-finalize skill (queued)' when -RunFinalize is used."
    )

    assert "ai-summary-comment skill (queued)" in src, (
        "Should reference 'ai-summary-comment skill (queued)' when -PostSummaryComment is used."
    )


# [pr_diff] fail_to_pass
def test_mode_logic_inverted():
    """Review-PR.ps1 logic correctly inverts interactive mode default."""
    src = REVIEW_PR_PATH.read_text()

    # Check that the mode display logic is inverted
    # Old: if ($NoInteractive) { 'Non-interactive' } else { 'Interactive' }
    # New: if ($Interactive) { 'Interactive' } else { 'Non-interactive' }

    # Should use $Interactive variable for mode display
    mode_line = re.search(r'Write-Host\s+"MODE:[^"]+"\s+-ForegroundColor White', src)
    if mode_line:
        # Check the context around MODE display
        context_start = max(0, src.find(mode_line.group(0)) - 200)
        context_end = min(len(src), src.find(mode_line.group(0)) + 50)
        context = src[context_start:context_end]

        assert "$Interactive" in context, (
            "MODE display should use $Interactive variable (inverted logic). "
            "The PR inverts the default: non-interactive is now default."
        )

    # Check session file logic is also inverted
    assert "if (-not $Interactive)" in src, (
        "Session markdown logic should use 'if (-not $Interactive)' instead of 'if ($NoInteractive)'. "
        "Session files are created in non-interactive mode (the new default)."
    )


# [pr_diff] fail_to_pass
def test_phase_2_implementation_added():
    """Review-PR.ps1 implements Phase 2: PR-FINALIZE SKILL block."""
    src = REVIEW_PR_PATH.read_text()

    # Should have Phase 2 header
    assert "PHASE 2: PR-FINALIZE SKILL" in src, (
        "Missing 'PHASE 2: PR-FINALIZE SKILL' block. "
        "The PR adds this phase to run pr-finalize skill when -RunFinalize is specified."
    )

    # Should run pr-finalize skill
    assert "pr-finalize skill for PR" in src, (
        "Should include pr-finalize skill invocation in Phase 2."
    )


# [pr_diff] fail_to_pass
def test_phase_3_implementation_added():
    """Review-PR.ps1 implements Phase 3: POST SUMMARY COMMENT block."""
    src = REVIEW_PR_PATH.read_text()

    # Should have Phase 3 header
    assert "PHASE 3: POST SUMMARY COMMENT" in src, (
        "Missing 'PHASE 3: POST SUMMARY COMMENT' block. "
        "The PR adds this phase to run ai-summary-comment skill when -PostSummaryComment is specified."
    )

    # Should use ai-summary-comment skill
    assert "ai-summary-comment skill to post a comment" in src, (
        "Should include ai-summary-comment skill invocation in Phase 3."
    )


# [pr_diff] fail_to_pass
def test_copilot_instructions_updated():
    """copilot-instructions.md has updated pr-finalize skill description."""
    src = COPILOT_INSTRUCTIONS_PATH.read_text()

    # Should have updated purpose mentioning code review
    assert "performs code review for best practices before merge" in src, (
        "copilot-instructions.md should mention that pr-finalize now performs code review. "
        "The PR adds code review phase to the skill."
    )

    # Should have safety rule about approval
    assert "NEVER use `--approve` or `--request-changes`" in src, (
        "Missing CRITICAL safety rule in copilot-instructions.md: NEVER use --approve or --request-changes. "
        "AI agents must not approve or block PRs - only post comments."
    )


# [pr_diff] fail_to_pass
def test_codereview_parameters_added():
    """post-pr-finalize-comment.ps1 has CodeReviewStatus and CodeReviewFindings parameters."""
    src = POST_FINALIZE_PATH.read_text()

    # Should have CodeReviewStatus parameter with ValidateSet
    assert "CodeReviewStatus" in src, (
        "Missing CodeReviewStatus parameter. "
        "The PR adds this parameter with values: Passed, IssuesFound, Skipped."
    )

    assert "CodeReviewFindings" in src, (
        "Missing CodeReviewFindings parameter. "
        "The PR adds this parameter for code review content."
    )

    # Should have ValidateSet for CodeReviewStatus
    assert '[ValidateSet("Passed", "IssuesFound", "Skipped", "")]' in src, (
        "CodeReviewStatus should have ValidateSet with 'Passed', 'IssuesFound', 'Skipped'."
    )


# [pr_diff] fail_to_pass
def test_codereview_section_added():
    """post-pr-finalize-comment.ps1 includes code review collapsible section."""
    src = POST_FINALIZE_PATH.read_text()

    # Should build code review section
    assert "$codeReviewSection" in src, (
        "Missing $codeReviewSection variable. "
        "The PR adds a third collapsible section for code review."
    )

    # Should include code review in final output
    assert "Code Review:" in src or "codeReviewSection" in src, (
        "Script should include Code Review section in the posted comment."
    )

    # Should have code review emoji mappings
    assert '"Passed" { "✅" }' in src or '"IssuesFound" { "⚠️" }' in src, (
        "Should have emoji mappings for CodeReviewStatus values."
    )


# [pr_diff] fail_to_pass
def test_skill_finalize_has_code_review_phase():
    """pr-finalize/SKILL.md has code review phase documentation."""
    src = SKILL_FINALIZE_PATH.read_text()

    # Should mention code review
    assert "Code Review" in src, (
        "pr-finalize/SKILL.md should document the code review phase. "
        "The PR adds a second phase for code review."
    )

    # Should have safety rules
    assert "NEVER Approve or Request Changes" in src or "NEVER use `--approve`" in src, (
        "SKILL.md should have CRITICAL safety rules about approval."
    )

    # Should describe two-phase workflow
    assert "Two-Phase Workflow" in src or "Phase 1" in src and "Phase 2" in src, (
        "SKILL.md should describe the two-phase workflow (Title/Description + Code Review)."
    )


# [pr_diff] fail_to_pass
def test_skill_ai_has_codereview_docs():
    """ai-summary-comment/SKILL.md documents Code Review section parameters."""
    src = SKILL_AI_PATH.read_text()

    # Should document CodeReviewStatus parameter
    assert "CodeReviewStatus" in src, (
        "ai-summary-comment/SKILL.md should document CodeReviewStatus parameter."
    )

    # Should document CodeReviewFindings parameter
    assert "CodeReviewFindings" in src, (
        "ai-summary-comment/SKILL.md should document CodeReviewFindings parameter."
    )

    # Should mention three sections (Title, Description, Code Review)
    three_sections = (
        ("Title" in src and "Description" in src and "Code Review" in src) or
        "three sections" in src.lower() or
        "three collapsible sections" in src.lower()
    )
    assert three_sections, (
        "SKILL.md should mention that comments now have three sections: Title, Description, and Code Review."
    )


# [pr_diff] fail_to_pass
def test_extract_codereview_from_file():
    """post-pr-finalize-comment.ps1 extracts code review from code-review.md file."""
    src = POST_FINALIZE_PATH.read_text()

    # Should look for code-review.md file
    assert 'code-review.md' in src, (
        "Script should look for code-review.md file to auto-load code review content. "
        "The PR adds support for loading code review from a separate file."
    )

    # Should extract from summary file as fallback
    assert "Code Review Findings" in src or "### 🔍 Code Review" in src, (
        "Script should extract code review from summary file when code-review.md is not present."
    )


# [pr_diff] fail_to_pass
def test_warnings_for_missing_recommendations():
    """post-pr-finalize-comment.ps1 warns when recommended title/description missing."""
    src = POST_FINALIZE_PATH.read_text()

    # Should warn about missing recommended title
    assert "Warning: TitleStatus is 'NeedsUpdate' but no RecommendedTitle provided" in src, (
        "Script should warn when TitleStatus is NeedsUpdate but no RecommendedTitle provided."
    )

    # Should warn about missing recommended description
    assert "Warning: DescriptionStatus is" in src and "RecommendedDescription provided" in src, (
        "Script should warn when DescriptionStatus indicates update needed but no RecommendedDescription provided."
    )


# [pr_diff] fail_to_pass
def test_recommendedtitle_extraction_order_fixed():
    """post-pr-finalize-comment.ps1 extracts RecommendedTitle before TitleStatus detection."""
    src = POST_FINALIZE_PATH.read_text()

    # Find the extraction logic order
    recommended_title_pos = src.find("Extract Recommended Title FIRST")
    title_status_pos = src.find("Extract Title assessment")

    if recommended_title_pos != -1 and title_status_pos != -1:
        assert recommended_title_pos < title_status_pos, (
            "RecommendedTitle should be extracted BEFORE TitleStatus detection. "
            "The PR fixes a bug where TitleStatus was detected before RecommendedTitle was extracted."
        )


# [pr_diff] fail_to_pass
def test_autodetection_needsupdate_from_recommendedtitle():
    """post-pr-finalize-comment.ps1 auto-detects NeedsUpdate if RecommendedTitle exists."""
    src = POST_FINALIZE_PATH.read_text()

    # Should auto-detect NeedsUpdate when RecommendedTitle exists
    assert 'if (-not [string]::IsNullOrWhiteSpace($RecommendedTitle))' in src and 'NeedsUpdate' in src, (
        "Script should auto-detect TitleStatus as NeedsUpdate when RecommendedTitle exists. "
        "The PR adds this auto-detection logic."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_pr_finalize_marker_preserved():
    """PR finalization comment marker is preserved."""
    src = POST_FINALIZE_PATH.read_text()
    assert "PR-FINALIZE-COMMENT" in src, (
        "Script must contain <!-- PR-FINALIZE-COMMENT --> marker for comment identification."
    )


# [static] pass_to_pass
def test_examples_updated_in_review_pr():
    """Review-PR.ps1 examples reflect new interactive default."""
    src = REVIEW_PR_PATH.read_text()

    # Default example should show non-interactive
    assert "non-interactive mode (default)" in src, (
        "Examples should mention that non-interactive is now the default."
    )

    # Interactive example should use -Interactive
    assert "-Interactive" in src and "interactive mode" in src, (
        "Examples should show -Interactive for interactive mode."
    )
