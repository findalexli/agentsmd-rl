"""
Task: maui-improve-issuetriage-skill-add-gh
Repo: dotnet/maui @ 62894e405b36c5b6cede44fdfe56832e26cdc8af
PR:   33750

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/maui"
SKILL_MD = Path(REPO) / ".github" / "skills" / "issue-triage" / "SKILL.md"
INIT_SCRIPT = Path(REPO) / ".github" / "skills" / "issue-triage" / "scripts" / "init-triage-session.ps1"
QUERY_SCRIPT = Path(REPO) / ".github" / "skills" / "issue-triage" / "scripts" / "query-issues.ps1"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass
def test_scripts_exist():
    """Both PowerShell scripts must exist."""
    assert INIT_SCRIPT.exists(), "init-triage-session.ps1 not found"
    assert QUERY_SCRIPT.exists(), "query-issues.ps1 not found"


# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_script_checks_gh_prerequisite():
    """init-triage-session.ps1 must check for gh CLI before proceeding."""
    content = INIT_SCRIPT.read_text()
    assert "Get-Command gh" in content, \
        "init script should check for gh CLI using Get-Command"
    assert "exit 1" in content, \
        "init script should exit with error if gh not found"


# [pr_diff] fail_to_pass
def test_init_script_uses_invoke_restmethod():
    """init-triage-session.ps1 must use Invoke-RestMethod for milestones, not gh api."""
    content = INIT_SCRIPT.read_text()
    assert "Invoke-RestMethod" in content, \
        "init script should use Invoke-RestMethod for milestone fetching"
    assert "gh api repos/dotnet/maui/milestones" not in content, \
        "init script should not use gh api for milestones (use Invoke-RestMethod)"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
