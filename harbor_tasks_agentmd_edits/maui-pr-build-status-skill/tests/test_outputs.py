"""
Task: maui-pr-build-status-skill
Repo: dotnet/maui @ 235cb6f394a4eb7a525fbf2e583b727ec83da656
PR:   33325

Tests verify the pr-build-status Copilot CLI skill: SKILL.md config and
PowerShell scripts for querying Azure DevOps build status.
All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"
SKILL_DIR = Path(REPO) / ".github" / "skills" / "pr-build-status"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def run_pwsh(command: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a PowerShell command and return the result."""
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — PowerShell script behavioral tests via pwsh
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scripts_parse_without_errors():
    """All three PS1 scripts parse without PowerShell syntax errors."""
    scripts = ["Get-PrBuildIds.ps1", "Get-BuildInfo.ps1", "Get-BuildErrors.ps1"]
    for script_name in scripts:
        path = SCRIPTS_DIR / script_name
        assert path.exists(), f"{script_name} must exist in scripts directory"
        r = run_pwsh(
            f"$errors = $null; $tokens = $null; "
            f"$null = [System.Management.Automation.Language.Parser]::ParseFile("
            f"'{path}', [ref]$tokens, [ref]$errors); "
            f"if ($errors.Count -gt 0) {{ $errors | ForEach-Object {{ Write-Error $_.Message }}; exit 1 }}; "
            f"Write-Output 'OK'"
        )
        assert r.returncode == 0, f"{script_name} has syntax errors: {r.stderr}"
        assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_get_pr_build_ids_parameters():
    """Get-PrBuildIds.ps1 has mandatory PrNumber and optional Repo defaulting to dotnet/maui."""
    path = SCRIPTS_DIR / "Get-PrBuildIds.ps1"
    r = run_pwsh(
        f"$cmd = Get-Command '{path}'; "
        f"$params = $cmd.Parameters; "
        # PrNumber must be mandatory
        f"$pn = $params['PrNumber']; "
        f"if (-not $pn) {{ Write-Error 'Missing PrNumber param'; exit 1 }}; "
        f"$mand = ($pn.Attributes | Where-Object {{ $_ -is [System.Management.Automation.ParameterAttribute] }}).Mandatory; "
        f"if (-not $mand) {{ Write-Error 'PrNumber not mandatory'; exit 1 }}; "
        # Repo must exist
        f"$repo = $params['Repo']; "
        f"if (-not $repo) {{ Write-Error 'Missing Repo param'; exit 1 }}; "
        # Check Repo default via AST
        f"$ast = [System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$null, [ref]$null); "
        f"$rp = $ast.ParamBlock.Parameters | Where-Object {{ $_.Name.VariablePath.UserPath -eq 'Repo' }}; "
        f"$dv = $rp.DefaultValue.Value; "
        f"if ($dv -ne 'dotnet/maui') {{ Write-Error \"Repo default is '$dv', expected 'dotnet/maui'\"; exit 1 }}; "
        f"Write-Output 'OK'"
    )
    assert r.returncode == 0, f"Parameter check failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_get_build_info_parameters():
    """Get-BuildInfo.ps1 has mandatory BuildId, FailedOnly switch, and Org defaulting to dnceng-public."""
    path = SCRIPTS_DIR / "Get-BuildInfo.ps1"
    r = run_pwsh(
        f"$cmd = Get-Command '{path}'; "
        f"$params = $cmd.Parameters; "
        # BuildId must be mandatory
        f"$bid = $params['BuildId']; "
        f"if (-not $bid) {{ Write-Error 'Missing BuildId param'; exit 1 }}; "
        f"$mand = ($bid.Attributes | Where-Object {{ $_ -is [System.Management.Automation.ParameterAttribute] }}).Mandatory; "
        f"if (-not $mand) {{ Write-Error 'BuildId not mandatory'; exit 1 }}; "
        # FailedOnly must be a switch
        f"$fo = $params['FailedOnly']; "
        f"if (-not $fo) {{ Write-Error 'Missing FailedOnly param'; exit 1 }}; "
        f"if ($fo.ParameterType -ne [switch]) {{ Write-Error 'FailedOnly is not a switch'; exit 1 }}; "
        # Org default
        f"$ast = [System.Management.Automation.Language.Parser]::ParseFile('{path}', [ref]$null, [ref]$null); "
        f"$op = $ast.ParamBlock.Parameters | Where-Object {{ $_.Name.VariablePath.UserPath -eq 'Org' }}; "
        f"$dv = $op.DefaultValue.Value; "
        f"if ($dv -ne 'dnceng-public') {{ Write-Error \"Org default is '$dv'\"; exit 1 }}; "
        f"Write-Output 'OK'"
    )
    assert r.returncode == 0, f"Parameter check failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_get_build_errors_parameters():
    """Get-BuildErrors.ps1 has mandatory BuildId plus TestsOnly, ErrorsOnly, and JobFilter params."""
    path = SCRIPTS_DIR / "Get-BuildErrors.ps1"
    r = run_pwsh(
        f"$cmd = Get-Command '{path}'; "
        f"$params = $cmd.Parameters; "
        # BuildId must be mandatory
        f"$bid = $params['BuildId']; "
        f"if (-not $bid) {{ Write-Error 'Missing BuildId param'; exit 1 }}; "
        f"$mand = ($bid.Attributes | Where-Object {{ $_ -is [System.Management.Automation.ParameterAttribute] }}).Mandatory; "
        f"if (-not $mand) {{ Write-Error 'BuildId not mandatory'; exit 1 }}; "
        # Filter params must exist
        f"foreach ($name in @('TestsOnly', 'ErrorsOnly', 'JobFilter')) {{ "
        f"  if (-not $params[$name]) {{ Write-Error \"Missing $name param\"; exit 1 }} "
        f"}}; "
        # TestsOnly and ErrorsOnly must be switches
        f"if ($params['TestsOnly'].ParameterType -ne [switch]) {{ Write-Error 'TestsOnly not switch'; exit 1 }}; "
        f"if ($params['ErrorsOnly'].ParameterType -ne [switch]) {{ Write-Error 'ErrorsOnly not switch'; exit 1 }}; "
        f"Write-Output 'OK'"
    )
    assert r.returncode == 0, f"Parameter check failed: {r.stderr}"


# [pr_diff] fail_to_pass

    # Both scripts must target Azure DevOps APIs
    assert "dev.azure.com" in build_info, \
        "Get-BuildInfo.ps1 should query dev.azure.com"
    assert "dev.azure.com" in build_errors, \
        "Get-BuildErrors.ps1 should query dev.azure.com"

    # Both should use the timeline API for stage/job/task details
    assert "timeline" in build_info, \
        "Get-BuildInfo.ps1 should use the build timeline API"
    assert "timeline" in build_errors, \
        "Get-BuildErrors.ps1 should use the build timeline API"

    # Error script must handle build errors and test failures
    assert "BuildError" in build_errors or "build error" in build_errors.lower(), \
        "Get-BuildErrors.ps1 should distinguish build errors"
    assert "TestFailure" in build_errors or "test failure" in build_errors.lower(), \
        "Get-BuildErrors.ps1 should distinguish test failures"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md agent config file tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have complete frontmatter (--- ... ---)"

    frontmatter = parts[1]
    assert "name:" in frontmatter, "Frontmatter must include 'name' field"
    assert "description:" in frontmatter, "Frontmatter must include 'description' field"
    # Name or description should reference builds/PR
    fm_lower = frontmatter.lower()
    assert "build" in fm_lower, "Skill name/description should reference builds"


# [config_edit] fail_to_pass

    # Each script must be mentioned so Copilot knows how to invoke them
    for script in ["Get-PrBuildIds", "Get-BuildInfo", "Get-BuildErrors"]:
        assert script in content, \
            f"SKILL.md should reference the {script} script"


# [config_edit] fail_to_pass

    # Should describe an ordered workflow (numbered steps or "workflow" section)
    assert "1." in content and "2." in content, \
        "SKILL.md should describe numbered workflow steps"
    # Should cover both PR→build-IDs and build-ID→details flow
    content_lower = content.lower()
    assert "build" in content_lower and "pr" in content_lower, \
        "SKILL.md workflow should cover PR-to-build-ID and build-details flow"


# [config_edit] fail_to_pass

    assert "gh" in content, \
        "SKILL.md should mention GitHub CLI (gh) as a prerequisite"
    assert "pwsh" in content or "PowerShell" in content, \
        "SKILL.md should mention PowerShell as a prerequisite"
