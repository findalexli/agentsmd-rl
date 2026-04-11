"""
Task: maui-copilot-agent-infrastructure-emulator-reliability
Repo: dotnet/maui @ c1e543e1f116911ffb934e60c79bb501ea1814e3
PR:   33937

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"

SHARED_UTILS = Path(REPO) / ".github/scripts/shared/shared-utils.ps1"
HOST_APP = Path(REPO) / ".github/scripts/BuildAndRunHostApp.ps1"
REVIEW_PR = Path(REPO) / ".github/scripts/Review-PR.ps1"
START_EMULATOR = Path(REPO) / ".github/scripts/shared/Start-Emulator.ps1"
ANDROID_CAKE = Path(REPO) / "eng/devices/android.cake"
PLAN_TEMPLATE = Path(REPO) / ".github/agents/pr/PLAN-TEMPLATE.md"
SHARED_RULES = Path(REPO) / ".github/agents/pr/SHARED-RULES.md"
POST_GATE = Path(REPO) / ".github/agents/pr/post-gate.md"
TRY_FIX_SKILL = Path(REPO) / ".github/skills/try-fix/SKILL.md"


def _run_pwsh(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a PowerShell snippet and return the result."""
    return subprocess.run(
        ["pwsh", "-NoProfile", "-Command", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------


def test_shared_utils_valid_syntax():
    """shared-utils.ps1 must source without syntax errors in PowerShell."""
    result = _run_pwsh(f". '{SHARED_UTILS}'")
    assert result.returncode == 0, f"shared-utils.ps1 syntax error: {result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI commands that actually run repo code
# ---------------------------------------------------------------------------


def test_repo_script_files_exist():
    """All PowerShell script files must exist at their declared paths (pass_to_pass)."""
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-Command",
         f"Test-Path '{SHARED_UTILS}' && Test-Path '{HOST_APP}' && "
         f"Test-Path '{REVIEW_PR}' && Test-Path '{START_EMULATOR}' && "
         f"Test-Path '{ANDROID_CAKE}'"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Script files missing: {result.stderr}"


def test_repo_git_works():
    """Git commands must work in the repo (pass_to_pass)."""
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"git status failed: {result.stderr}"


def test_repo_ps_file_info():
    """PowerShell Get-ChildItem must work on script directories (pass_to_pass)."""
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-Command",
         f"Get-ChildItem '{REPO}/.github/scripts' -Filter '*.ps1' | Measure-Object | "
         f"Select-Object -ExpandProperty Count"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"PowerShell file listing failed: {result.stderr}"
    count = result.stdout.strip()
    assert int(count) > 0, f"Expected PowerShell files, got count: {count}"


def test_repo_test_script_syntax():
    """Test-EstablishBrokenBaseline.ps1 must have valid PowerShell syntax (pass_to_pass)."""
    test_script = f"{REPO}/.github/scripts/tests/Test-EstablishBrokenBaseline.ps1"
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-Command",
         f"Get-Command '{test_script}' -ErrorAction Stop | Out-Null; 'SYNTAX_OK'"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Test script syntax error: {result.stderr}"
    assert "SYNTAX_OK" in result.stdout, f"Test script validation failed: {result.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass — code behavioral tests
# ---------------------------------------------------------------------------


def test_write_warn_executes():
    """Write-Warn function must exist and produce warning output."""
    result = _run_pwsh(
        f". '{SHARED_UTILS}'; Write-Warn 'hello check'"
    )
    assert result.returncode == 0, f"Write-Warn failed: {result.stderr}"
    combined = result.stdout + result.stderr
    assert "hello check" in combined, f"Write-Warn output missing, got: {combined}"


def test_host_app_uses_write_warn():
    """BuildAndRunHostApp.ps1 must use Write-Warn helper (not Write-Warning)."""
    content = HOST_APP.read_text()
    assert 'Write-Warn "MacCatalyst app not found' in content, \
        "BuildAndRunHostApp.ps1 should call Write-Warn for MacCatalyst warning"
    assert 'Write-Warn "Could not read device log' in content, \
        "BuildAndRunHostApp.ps1 should call Write-Warn for device log warning"
    assert 'Write-Warn "No logs found for' in content, \
        "BuildAndRunHostApp.ps1 should call Write-Warn for logcat warning"


def test_review_pr_logfile_param():
    """Review-PR.ps1 must accept -LogFile parameter with transcript logging."""
    content = REVIEW_PR.read_text()
    assert "[string]$LogFile" in content, \
        "Review-PR.ps1 must declare [string]$LogFile parameter"
    assert "Start-Transcript" in content, \
        "Review-PR.ps1 must use Start-Transcript when -LogFile is provided"
    assert "Stop-Transcript" in content, \
        "Review-PR.ps1 must stop transcript on exit"


def test_review_pr_tree_restore():
    """Review-PR.ps1 must restore working tree between phases."""
    content = REVIEW_PR.read_text()
    assert "git checkout HEAD -- ." in content, \
        "Review-PR.ps1 must restore tracked files with git checkout HEAD -- ."
    # Must appear more than once (at least phase 1->2 and phase 2->3)
    count = content.count("git checkout HEAD -- .")
    assert count >= 2, f"Expected >= 2 tree restorations, got {count}"


def test_android_cake_boot_timeout():
    """android.cake must set emulator boot timeout to 10 minutes."""
    content = ANDROID_CAKE.read_text()
    assert "10 * 60" in content, \
        "EmulatorBootTimeoutSeconds should be 10 * 60 (10 minutes)"


# ---------------------------------------------------------------------------
# Fail-to-pass — config/instruction file update tests
# ---------------------------------------------------------------------------


def test_plan_template_model_version():
    """PLAN-TEMPLATE.md must reference claude-opus-4.6 (updated model)."""
    content = PLAN_TEMPLATE.read_text()
    assert "claude-opus-4.6" in content, \
        "PLAN-TEMPLATE.md should reference claude-opus-4.6 model"
    # Old model name should be gone
    assert "claude-opus-4.5" not in content, \
        "PLAN-TEMPLATE.md should not reference old claude-opus-4.5"


def test_shared_rules_model_version():
    """SHARED-RULES.md must reference claude-opus-4.6 in model table."""
    content = SHARED_RULES.read_text()
    assert "claude-opus-4.6" in content, \
        "SHARED-RULES.md should reference claude-opus-4.6 model"
    assert "claude-opus-4.5" not in content, \
        "SHARED-RULES.md should not reference old claude-opus-4.5"


def test_post_gate_env_blockers():
    """post-gate.md must have stop-on-environment-blocker rules for Phase 4."""
    content = POST_GATE.read_text()
    assert "Stop on Environment Blockers" in content, \
        "post-gate.md must have Stop on Environment Blockers section"
    assert "Missing Appium drivers" in content, \
        "post-gate.md must list Missing Appium drivers as a blocker"
    assert "Device/emulator not available" in content, \
        "post-gate.md must list device/emulator unavailability as a blocker"


def test_post_gate_mandatory_cleanup():
    """post-gate.md must require cleanup between try-fix attempts."""
    content = POST_GATE.read_text()
    assert "git checkout HEAD -- ." in content, \
        "post-gate.md must require git checkout HEAD between attempts"
    assert "git clean -fd" in content, \
        "post-gate.md must require git clean -fd between attempts"
    assert "CustomAgentLogsTmp/" in content, \
        "post-gate.md must exclude CustomAgentLogsTmp/ from cleanup"


def test_skill_md_no_git_add_state():
    """try-fix SKILL.md must warn against git add of state files."""
    content = TRY_FIX_SKILL.read_text()
    assert "git add" in content, \
        "SKILL.md must mention git add in context of state files"
    # Must explicitly warn against committing state files
    assert "CustomAgentLogsTmp" in content or "gitignored" in content, \
        "SKILL.md must explain why state files should not be committed"
