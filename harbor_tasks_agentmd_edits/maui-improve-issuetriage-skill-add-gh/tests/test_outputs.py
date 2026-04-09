"""
Task: maui-improve-issuetriage-skill-add-gh
Repo: dotnet/maui @ 62894e405b36c5b6cede44fdfe56832e26cdc8af
PR:   33750

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"
SKILL_MD = Path(REPO) / ".github" / "skills" / "issue-triage" / "SKILL.md"
INIT_SCRIPT = Path(REPO) / ".github" / "skills" / "issue-triage" / "scripts" / "init-triage-session.ps1"
QUERY_SCRIPT = Path(REPO) / ".github" / "skills" / "issue-triage" / "scripts" / "query-issues.ps1"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_scripts_exist():
    """Both PowerShell scripts must exist."""
    assert INIT_SCRIPT.exists(), "init-triage-session.ps1 not found"
    assert QUERY_SCRIPT.exists(), "query-issues.ps1 not found"


# [static] pass_to_pass
def test_skill_md_exists():
    """SKILL.md documentation must exist."""
    assert SKILL_MD.exists(), "SKILL.md not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests with subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_init_script_valid_powershell():
    """init-triage-session.ps1 must have valid PowerShell syntax."""
    r = subprocess.run(
        ["pwsh", "-Command", f"Get-Command {INIT_SCRIPT} | Test-ModuleManifest -ErrorAction SilentlyContinue; $?"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # If pwsh is not available, at least parse the AST
    if r.returncode != 0 or "not found" in r.stderr.lower():
        # Fallback: use PowerShell parser
        r2 = subprocess.run(
            ["pwsh", "-Command", f"$e = $null; [System.Management.Automation.Language.Parser]::ParseFile('{INIT_SCRIPT}', [ref]$e, [ref]$e); if ($e) {{ exit 1 }} else {{ exit 0 }}"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r2.returncode == 0, f"PowerShell syntax errors in init-triage-session.ps1: {r2.stderr}"


# [pr_diff] fail_to_pass
def test_init_script_has_gh_check():
    """init-triage-session.ps1 must check for gh CLI and exit if not found/authenticated."""
    content = INIT_SCRIPT.read_text()

    # Verify the script has the gh check pattern with proper exit behavior
    assert "Get-Command gh" in content, "Missing 'Get-Command gh' check"
    assert "gh auth status" in content, "Missing 'gh auth status' authentication check"
    assert "exit 1" in content, "Missing 'exit 1' for gh check failure"

    # Verify the check is at the start of the script (before milestone fetching)
    # The check should appear within the first 50 lines
    lines = content.split("\n")
    gh_check_line = None
    milestone_fetch_line = None
    for i, line in enumerate(lines):
        if "Get-Command gh" in line and gh_check_line is None:
            gh_check_line = i
        if "Invoke-RestMethod" in line and "milestones" in content[i:i+100] and milestone_fetch_line is None:
            milestone_fetch_line = i

    assert gh_check_line is not None, "Could not find gh check in script"
    if milestone_fetch_line is not None:
        assert gh_check_line < milestone_fetch_line, "gh check should come before milestone fetching"


# [pr_diff] fail_to_pass
def test_init_script_uses_invoke_restmethod():
    """init-triage-session.ps1 must use Invoke-RestMethod for milestones instead of gh api."""
    content = INIT_SCRIPT.read_text()

    # Must use Invoke-RestMethod for milestone fetching
    assert "Invoke-RestMethod" in content, "Missing 'Invoke-RestMethod' for milestone fetching"

    # Must NOT use gh api for milestones (the old broken approach)
    assert "gh api repos/dotnet/maui/milestones" not in content, \
        "Should not use 'gh api repos/dotnet/maui/milestones' - use Invoke-RestMethod instead"

    # Verify the URL is correct in the Invoke-RestMethod call
    assert "api.github.com/repos/dotnet/maui/milestones" in content, \
        "Invoke-RestMethod should call the correct GitHub API endpoint for milestones"


# [pr_diff] fail_to_pass
def test_query_script_has_gh_check():
    """query-issues.ps1 must check for gh CLI and exit if not found/authenticated."""
    content = QUERY_SCRIPT.read_text()

    # Verify the script has the gh check pattern
    assert "Get-Command gh" in content, "Missing 'Get-Command gh' check"
    assert "gh auth status" in content, "Missing 'gh auth status' authentication check"
    assert "exit 1" in content, "Missing 'exit 1' for gh check failure"

    # The gh auth check should produce a clear error message
    assert "not authenticated" in content.lower() or "not installed" in content.lower(), \
        "Should have clear error messages for missing/unauthenticated gh"


# [pr_diff] fail_to_pass
def test_query_script_valid_powershell():
    """query-issues.ps1 must have valid PowerShell syntax."""
    r = subprocess.run(
        ["pwsh", "-Command", f"$e = $null; [System.Management.Automation.Language.Parser]::ParseFile('{QUERY_SCRIPT}', [ref]$e, [ref]$e); if ($e) {{ exit 1 }} else {{ exit 0 }}"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PowerShell syntax errors in query-issues.ps1: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — SKILL.md documentation tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_skill_prerequisites_section():
    """SKILL.md must have Prerequisites section with gh installation instructions."""
    content = SKILL_MD.read_text()

    assert "## Prerequisites" in content, "Missing '## Prerequisites' section"
    assert "gh auth login" in content, "Missing 'gh auth login' authentication instruction"
    assert "winget install" in content or "brew install" in content, \
        "Missing gh CLI installation instructions (winget or brew)"


# [agent_config] fail_to_pass
def test_skill_common_mistakes_section():
    """SKILL.md must have Common Mistakes to Avoid section."""
    content = SKILL_MD.read_text()

    assert "## Common Mistakes to Avoid" in content, \
        "Missing '## Common Mistakes to Avoid' section"
    assert "Mistake" in content and "Correct Approach" in content, \
        "Common Mistakes section should have a table with 'Mistake' and 'Correct Approach' columns"


# [agent_config] fail_to_pass
def test_skill_critical_always_use_scripts():
    """SKILL.md must have CRITICAL rule about always using skill scripts."""
    content = SKILL_MD.read_text()

    assert "CRITICAL" in content and "ALWAYS use the skill scripts" in content, \
        "Missing CRITICAL warning to always use skill scripts"
    assert "NEVER use ad-hoc GitHub API queries" in content, \
        "Missing warning against ad-hoc GitHub API queries"


# [agent_config] fail_to_pass
def test_skill_step_6_batch_reload():
    """SKILL.md must document Step 6 automatic batch reload with -Skip parameter."""
    content = SKILL_MD.read_text()

    assert "### Step 6" in content, "Missing '### Step 6' section"
    assert "-Skip" in content, "Missing '-Skip' parameter documentation for batch reload"
    assert "AUTOMATICALLY reload" in content or "automatically reload" in content, \
        "Missing guidance to automatically reload more issues"


# [agent_config] fail_to_pass
def test_skill_version_updated():
    """SKILL.md version must be updated to reflect the changes."""
    content = SKILL_MD.read_text()

    # Version should be 2.3 (the fixed version)
    assert 'version: "2.3"' in content, \
        "SKILL.md version should be '2.3' to reflect the changes"
