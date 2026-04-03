"""
Task: maui-remove-phase-2-tests-from
Repo: dotnet/maui @ d417bea8d060b23aed36aa2e5f4a2bda2eb84a88
PR:   33905

Remove the redundant Tests phase (Phase 2) from the PR agent workflow,
simplifying from 5 phases to 4 phases. Updates span agent config files,
documentation, and PowerShell scripts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Config update tests (config_edit, fail_to_pass)
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Code behavior tests (pr_diff, fail_to_pass) — PowerShell script changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_summary_script_no_tests_phase_status():
    """post-ai-summary-comment.ps1 phaseStatuses must not include Tests."""
    content = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1").read_text()
    # The old script had: "Tests" = "⏳ PENDING" in phaseStatuses
    assert '"Tests" = ' not in content, \
        "Script phaseStatuses should not include a Tests entry"


# [pr_diff] fail_to_pass
def test_summary_script_no_tests_section_extraction():
    """post-ai-summary-comment.ps1 must not extract a Tests section."""
    content = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1").read_text()
    # The old script had $testsContent, $testsSection, $newTestsSession variables
    assert "$testsContent" not in content, "Script should not extract $testsContent"
    assert "$testsSection" not in content, "Script should not build $testsSection"


# [pr_diff] fail_to_pass
def test_summary_script_no_tests_validation_case():
    """post-ai-summary-comment.ps1 Test-PhaseContentComplete must not validate Tests."""
    content = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1").read_text()
    # The old script had a validation warning: "Tests phase missing test file paths"
    assert "Tests phase missing test file paths" not in content, \
        "Script should not have Tests phase validation logic"


# [pr_diff] fail_to_pass
def test_review_script_describes_4_phase():
    """Review-PR.ps1 must describe the workflow as 4-phase."""
    content = (Path(REPO) / ".github/scripts/Review-PR.ps1").read_text()
    assert "4-phase" in content, "Review-PR.ps1 should say 4-phase"
    assert "5-phase" not in content, "Review-PR.ps1 should not say 5-phase"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_pr_agent_has_all_4_phases():
    """pr.md + post-gate.md must still define Pre-Flight, Gate, Fix, Report."""
    pr_md = (Path(REPO) / ".github/agents/pr.md").read_text()
    post_gate = (Path(REPO) / ".github/agents/pr/post-gate.md").read_text()
    combined = pr_md + post_gate
    assert "Pre-Flight" in combined, "Missing Pre-Flight phase"
    assert "Gate" in combined, "Missing Gate phase"
    assert "Fix" in combined, "Missing Fix phase"
    assert "Report" in combined, "Missing Report phase"


# [static] pass_to_pass
def test_summary_script_still_extracts_core_phases():
    """post-ai-summary-comment.ps1 must still extract Gate, Fix, Report sections."""
    content = (Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1").read_text()
    assert "$gateContent" in content, "Script should still extract Gate content"
    assert "$fixContent" in content, "Script should still extract Fix content"
    assert "$reportContent" in content, "Script should still extract Report content"
    assert "$preFlightContent" in content, "Script should still extract Pre-Flight content"


# [static] pass_to_pass
def test_plan_template_has_gate_fix_report():
    """PLAN-TEMPLATE.md must still have Gate, Fix, Report phases."""
    content = (Path(REPO) / ".github/agents/pr/PLAN-TEMPLATE.md").read_text()
    assert "Gate" in content, "PLAN-TEMPLATE should have Gate phase"
    assert "Fix" in content, "PLAN-TEMPLATE should have Fix phase"
    assert "Report" in content, "PLAN-TEMPLATE should have Report phase"
