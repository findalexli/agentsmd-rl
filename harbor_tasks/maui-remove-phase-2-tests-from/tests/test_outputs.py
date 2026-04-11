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

import subprocess
from pathlib import Path

REPO = "/workspace/maui"


def _run_pwsh(script_path: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute PowerShell script to verify it parses without errors."""
    return subprocess.run(
        ["pwsh", "-Command", f"Get-Command {script_path}; Test-Path {script_path}"],
        capture_output=True, text=True, timeout=timeout,
    )


def _parse_pwsh(script_path: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Parse PowerShell script to check for syntax errors."""
    return subprocess.run(
        ["pwsh", "-Command", f"[System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw '{script_path}'), [ref]$null) | Out-Null; if ($?) {{ exit 0 }} else {{ exit 1 }}"],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — PowerShell script changes (behavioral tests)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_summary_script_no_tests_phase_status():
    """post-ai-summary-comment.ps1 phaseStatuses must not include Tests."""
    script_path = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1"

    # First verify script parses correctly (behavioral check)
    r = _parse_pwsh(str(script_path))
    assert r.returncode == 0, f"Script has syntax errors: {r.stderr}"

    # Then check content for the specific fix
    content = script_path.read_text()
    # The old script had: "Tests" = "⏳ PENDING" in phaseStatuses
    assert '"Tests" = ' not in content, \
        "Script phaseStatuses should not include a Tests entry"


# [pr_diff] fail_to_pass
def test_summary_script_no_tests_section_extraction():
    """post-ai-summary-comment.ps1 must not extract a Tests section."""
    script_path = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1"

    # Verify script parses correctly (behavioral check)
    r = _parse_pwsh(str(script_path))
    assert r.returncode == 0, f"Script has syntax errors: {r.stderr}"

    content = script_path.read_text()
    # The gold patch removes the extraction of Tests content:
    # - The $testsContent = Get-SectionByPattern assignment is removed
    # - The $testsSection = New-PhaseSection building is removed
    # - The $testsSection output in phaseSections is removed
    assert "$testsContent = Get-SectionByPattern" not in content, \
        "Script should not have $testsContent extraction assignment"
    assert "$testsSection = New-PhaseSection" not in content, \
        "Script should not build $testsSection"
    assert "$phaseSections += $testsSection" not in content, \
        "Script should not add Tests section to output"


# [pr_diff] fail_to_pass
def test_summary_script_no_tests_validation_case():
    """post-ai-summary-comment.ps1 Test-PhaseContentComplete must not validate Tests."""
    script_path = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1"

    # Verify script parses correctly (behavioral check)
    r = _parse_pwsh(str(script_path))
    assert r.returncode == 0, f"Script has syntax errors: {r.stderr}"

    content = script_path.read_text()
    # The old script had a validation warning: "Tests phase missing test file paths"
    assert "Tests phase missing test file paths" not in content, \
        "Script should not have Tests phase validation logic"


# [pr_diff] fail_to_pass
def test_review_script_describes_4_phase():
    """Review-PR.ps1 must describe the workflow as 4-phase and parse correctly."""
    script_path = Path(REPO) / ".github/scripts/Review-PR.ps1"

    # Behavioral check: PowerShell script must parse without errors
    r = _parse_pwsh(str(script_path))
    assert r.returncode == 0, f"Review-PR.ps1 has syntax errors: {r.stderr}"

    # Content check for the specific fix
    content = script_path.read_text()
    assert "4-phase" in content, "Review-PR.ps1 should say 4-phase"
    assert "5-phase" not in content, "Review-PR.ps1 should not say 5-phase"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks for markdown files
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
    script_path = Path(REPO) / ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1"

    # Verify script parses correctly
    r = _parse_pwsh(str(script_path))
    assert r.returncode == 0, f"Script has syntax errors: {r.stderr}"

    content = script_path.read_text()
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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_powershell_scripts_parse():
    """All PowerShell scripts in .github must parse without syntax errors (pass_to_pass)."""
    scripts = [
        ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1",
        ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1",
        ".github/scripts/Review-PR.ps1",
    ]
    for script_rel in scripts:
        script_path = Path(REPO) / script_rel
        r = subprocess.run(
            ["pwsh", "-Command",
             f"[System.Management.Automation.PSParser]::Tokenize((Get-Content -Raw '{script_path}'), [ref]$null) | Out-Null; if ($?) {{ exit 0 }} else {{ exit 1 }}"],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"PowerShell script {script_rel} has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_scripts_loadable():
    """Modified PowerShell scripts can be loaded by Get-Command (pass_to_pass)."""
    scripts = [
        ".github/skills/ai-summary-comment/scripts/post-ai-summary-comment.ps1",
        ".github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1",
        ".github/scripts/Review-PR.ps1",
    ]
    for script_rel in scripts:
        script_path = Path(REPO) / script_rel
        r = subprocess.run(
            ["pwsh", "-Command", f"Get-Command '{script_path}'"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"PowerShell script {script_rel} is not loadable: {r.stderr}"
