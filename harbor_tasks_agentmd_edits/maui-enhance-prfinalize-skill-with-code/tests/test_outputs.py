"""
Task: maui-enhance-prfinalize-skill-with-code
Repo: dotnet/maui @ 64d90e3ca4e83cf44a7a75c5ffa95a3e7c3147b7
PR:   33861

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified PowerShell and Markdown files exist and are non-empty."""
    files = [
        ".github/scripts/Review-PR.ps1",
        ".github/skills/pr-finalize/SKILL.md",
        ".github/copilot-instructions.md",
        ".github/skills/ai-summary-comment/SKILL.md",
        ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 100, f"{f} is too small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_review_pr_run_finalize_param():
    """Review-PR.ps1 must have a -RunFinalize switch parameter."""
    script = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    # Check the param block declares RunFinalize
    assert re.search(r'\$RunFinalize', script), \
        "Review-PR.ps1 should declare a RunFinalize parameter"
    # Verify it's used in the script body for conditional execution
    assert re.search(r'if\s*\(\s*\$RunFinalize\s*\)', script), \
        "Review-PR.ps1 should conditionally execute pr-finalize based on RunFinalize"


# [pr_diff] fail_to_pass
def test_review_pr_post_summary_comment_param():
    """Review-PR.ps1 must have a -PostSummaryComment switch parameter."""
    script = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    assert re.search(r'\$PostSummaryComment', script), \
        "Review-PR.ps1 should declare a PostSummaryComment parameter"
    assert re.search(r'if\s*\(\s*\$PostSummaryComment\s*\)', script), \
        "Review-PR.ps1 should conditionally execute ai-summary-comment based on PostSummaryComment"


# [pr_diff] fail_to_pass
def test_review_pr_default_non_interactive():
    """Review-PR.ps1 must default to non-interactive mode (Interactive is opt-in)."""
    script = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    # The script should have $Interactive as a switch (opt-in),
    # NOT $NoInteractive (which was the old opt-out approach)
    assert re.search(r'\[switch\]\s*\$Interactive', script), \
        "Review-PR.ps1 should have [switch]$Interactive (non-interactive is default)"
    # Should NOT have the old NoInteractive parameter
    assert not re.search(r'\$NoInteractive', script), \
        "Review-PR.ps1 should not have the old NoInteractive parameter"


# [pr_diff] fail_to_pass
def test_review_pr_git_safety_rules():
    """Review-PR.ps1 must include git safety rules in the agent prompt."""
    script = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    # Must have a dedicated safety block that warns against multiple git commands
    # Check that at least 3 dangerous git commands are mentioned near each other
    dangerous_cmds = ["git checkout", "git switch", "git push", "git reset", "git fetch", "git stash"]
    found = [cmd for cmd in dangerous_cmds if cmd in script]
    assert len(found) >= 3, \
        f"Review-PR.ps1 should warn against multiple git commands, found only: {found}"
    # The warnings must use strong language (NEVER/CRITICAL) near the git mentions
    # Find the block containing git warnings — should have NEVER within proximity
    for match in re.finditer(r'(?i)git (checkout|switch|push|reset|fetch|stash)', script):
        start = max(0, match.start() - 200)
        end = min(len(script), match.end() + 200)
        context = script[start:end]
        if "NEVER" in context or "CRITICAL" in context:
            break
    else:
        assert False, "Review-PR.ps1 should have NEVER/CRITICAL near git command warnings"


# [pr_diff] fail_to_pass
def test_finalize_comment_code_review_params():
    """post-pr-finalize-comment.ps1 must accept CodeReviewStatus and CodeReviewFindings."""
    script = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1").read_text()
    assert re.search(r'\$CodeReviewStatus', script), \
        "post-pr-finalize-comment.ps1 should have CodeReviewStatus parameter"
    assert re.search(r'\$CodeReviewFindings', script), \
        "post-pr-finalize-comment.ps1 should have CodeReviewFindings parameter"
    # Validate accepted values for CodeReviewStatus
    assert re.search(r'ValidateSet.*Passed.*IssuesFound.*Skipped', script), \
        "CodeReviewStatus should validate against Passed/IssuesFound/Skipped"


# [pr_diff] fail_to_pass
def test_finalize_comment_builds_code_review_section():
    """post-pr-finalize-comment.ps1 must build a Code Review HTML section."""
    script = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1").read_text()
    # Must build a collapsible code review section using HTML details/summary
    assert "Code Review:" in script, \
        "Script should build a 'Code Review:' section in the comment"
    # Must generate an HTML collapsible section (details tag) for code review
    assert re.search(r'<summary>.*Code Review', script, re.DOTALL), \
        "Script should build an HTML <summary> element for Code Review"
    # Must handle the three statuses (Passed, IssuesFound, Skipped) with emoji
    script_lower = script.lower()
    assert "passed" in script_lower and "issuesfound" in script_lower and "skipped" in script_lower, \
        "Script should handle Passed, IssuesFound, and Skipped code review statuses"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_review_pr_multi_phase_execution():
    """Review-PR.ps1 must have multi-phase execution logic (not just params)."""
    script = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    # Must reference phases in output
    assert re.search(r'PHASE\s*[12]', script, re.IGNORECASE) or \
        re.search(r'phase\s*[12]', script, re.IGNORECASE), \
        "Review-PR.ps1 should reference Phase 1/2 in execution flow"
    # Must invoke copilot for finalize phase
    assert "pr-finalize" in script.lower() or "finaliz" in script.lower(), \
        "Review-PR.ps1 should invoke pr-finalize in a subsequent phase"
