"""
Task: maui-regressionwindowsfix-exception-thrown-on-net
Repo: dotnet/maui @ 260770c977f376c9b0190c03ed1a41920725f079
PR:   33179

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"
PERMISSIONS_FILE = Path(REPO) / "src/Essentials/src/Permissions/Permissions.windows.cs"
COPILOT_INSTRUCTIONS = Path(REPO) / ".github/copilot-instructions.md"
SKILL_MD = Path(REPO) / ".github/skills/pr-finalize/SKILL.md"
EXAMPLE_MD = Path(REPO) / ".github/skills/pr-finalize/references/complete-example.md"


def _run_dotnet_build(project_file: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Build a .NET project to verify it compiles."""
    return subprocess.run(
        ["dotnet", "build", project_file, "--no-restore", "-v:q"],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code that validates repo file content."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_permissions_file_compiles():
    """Modified Permissions.windows.cs compiles without errors."""
    r = _run_dotnet_build(
        "src/Essentials/src/Microsoft.Maui.Essentials.csproj",
        timeout=120
    )
    assert r.returncode == 0, f"Build failed: {r.stderr}"


def test_copilot_instructions_valid():
    """Copilot instructions file still exists and has valid markdown structure."""
    assert COPILOT_INSTRUCTIONS.exists(), "copilot-instructions.md must exist"
    content = COPILOT_INSTRUCTIONS.read_text()
    # Must have basic structure
    assert "# " in content, "Missing header in copilot-instructions.md"
    assert ".NET MAUI" in content or "MAUI" in content, "Missing MAUI reference"


def test_skill_md_valid():
    """SKILL.md still exists and has valid structure."""
    assert SKILL_MD.exists(), "SKILL.md must exist"
    content = SKILL_MD.read_text()
    assert "Description Requirements" in content, "Missing Description Requirements section"


def test_example_md_valid():
    """complete-example.md still exists and has valid structure."""
    assert EXAMPLE_MD.exists(), "complete-example.md must exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_microphone_uses_packaged_check():
    """Microphone permission checks IsPackagedApp before EnsureDeclared."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Find Microphone class section\n"
        "if 'class Microphone' not in content:\n"
        "    print('FAIL: Microphone class not found'); sys.exit(1)\n"
        "\n"
        "# Check for IsPackagedApp check in CheckStatusAsync\n"
        "if 'AppInfoUtils.IsPackagedApp' not in content:\n"
        "    print('FAIL: IsPackagedApp check not found'); sys.exit(1)\n"
        "\n"
        "# Must have at least 2 occurrences (CheckStatusAsync and RequestAsync)\n"
        "count = content.count('AppInfoUtils.IsPackagedApp')\n"
        "if count < 2:\n"
        "    print(f'FAIL: Expected at least 2 IsPackagedApp checks, found {count}'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"IsPackagedApp check validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_checkstatusasync_conditional_ensuredeclared():
    """CheckStatusAsync only calls EnsureDeclared for packaged apps."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Find CheckStatusAsync method\n"
        "if 'public override Task<PermissionStatus> CheckStatusAsync()' not in content:\n"
        "    print('FAIL: CheckStatusAsync method not found'); sys.exit(1)\n"
        "\n"
        "# Split to find CheckStatusAsync method body\n"
        "method_start = content.find('public override Task<PermissionStatus> CheckStatusAsync()')\n"
        "method_section = content[method_start:method_start + 2000]\n"
        "\n"
        "# Must have conditional IsPackagedApp check\n"
        "if 'if (AppInfoUtils.IsPackagedApp)' not in method_section:\n"
        "    print('FAIL: IsPackagedApp check not in CheckStatusAsync'); sys.exit(1)\n"
        "\n"
        "# EnsureDeclared must be inside the if block\n"
        "if 'EnsureDeclared()' not in method_section:\n"
        "    print('FAIL: EnsureDeclared not found in CheckStatusAsync'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"CheckStatusAsync validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_requestasync_conditional_ensuredeclared():
    """RequestAsync only calls EnsureDeclared for packaged apps."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Find RequestAsync method\n"
        "if 'public override async Task<PermissionStatus> RequestAsync()' not in content:\n"
        "    print('FAIL: RequestAsync method not found'); sys.exit(1)\n"
        "\n"
        "# Split to find RequestAsync method body\n"
        "method_start = content.find('public override async Task<PermissionStatus> RequestAsync()')\n"
        "method_section = content[method_start:method_start + 2500]\n"
        "\n"
        "# Must have conditional IsPackagedApp check\n"
        "if 'if (AppInfoUtils.IsPackagedApp)' not in method_section:\n"
        "    print('FAIL: IsPackagedApp check not in RequestAsync'); sys.exit(1)\n"
        "\n"
        "# Must check status before EnsureDeclared\n"
        "if 'var status = CheckStatus()' not in method_section:\n"
        "    print('FAIL: CheckStatus call not found before EnsureDeclared'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"RequestAsync validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_tryrequestpermissionasync_extracted():
    """TryRequestPermissionAsync helper method is extracted from RequestAsync."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Must have TryRequestPermissionAsync method\n"
        "if 'async Task<PermissionStatus> TryRequestPermissionAsync()' not in content:\n"
        "    print('FAIL: TryRequestPermissionAsync method not found'); sys.exit(1)\n"
        "\n"
        "# Must contain MediaCaptureInitializationSettings\n"
        "if 'MediaCaptureInitializationSettings' not in content:\n"
        "    print('FAIL: MediaCaptureInitializationSettings not found'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"TryRequestPermissionAsync validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_copilot_instructions_pr_note_removed():
    """Stale PR testing note removed from copilot-instructions.md."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(COPILOT_INSTRUCTIONS) + "').read()\n"
        "\n"
        "# The stale PR note should be removed\n"
        "if 'Are you waiting for the changes in this PR to be merged?' in content:\n"
        "    print('FAIL: Stale PR note still present in copilot-instructions.md'); sys.exit(1)\n"
        "\n"
        "if 'Testing-PR-Builds' in content:\n"
        "    print('FAIL: Testing-PR-Builds link still present'); sys.exit(1)\n"
        "\n"
        "# Opening PRs section should be removed\n"
        "if '### Opening PRs' in content:\n"
        "    print('FAIL: Opening PRs section should be removed'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Copilot instructions validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_skill_md_pr_note_removed():
    """Stale PR testing note removed from SKILL.md."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(SKILL_MD) + "').read()\n"
        "\n"
        "# The stale PR note should be removed\n"
        "if 'Are you waiting for the changes in this PR to be merged?' in content:\n"
        "    print('FAIL: Stale PR note still present in SKILL.md'); sys.exit(1)\n"
        "\n"
        "if 'Testing-PR-Builds' in content:\n"
        "    print('FAIL: Testing-PR-Builds link still present in SKILL.md'); sys.exit(1)\n"
        "\n"
        "# Description requirements should be updated (now 2 items, not 3)\n"
        "if 'Start with the required NOTE block' in content:\n"
        "    print('FAIL: Old NOTE block requirement still in SKILL.md'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"SKILL.md validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_example_md_pr_note_removed():
    """Stale PR testing note removed from complete-example.md."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(EXAMPLE_MD) + "').read()\n"
        "\n"
        "# The stale PR note should be removed\n"
        "if 'Are you waiting for the changes in this PR to be merged?' in content:\n"
        "    print('FAIL: Stale PR note still present in complete-example.md'); sys.exit(1)\n"
        "\n"
        "if 'Testing-PR-Builds' in content:\n"
        "    print('FAIL: Testing-PR-Builds link still present in complete-example.md'); sys.exit(1)\n"
        "\n"
        "# Root Cause section should be preserved\n"
        "if '### Root Cause' not in content:\n"
        "    print('FAIL: Root Cause section missing in complete-example.md'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"complete-example.md validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_permissions_file_not_stub():
    """Permissions.windows.cs has real implementation, not just stubs."""
    content = PERMISSIONS_FILE.read_text()
    # Must have substantial content
    assert len(content) > 5000, "Permissions file too small - likely stubbed"
    # Must have multiple permission classes
    assert content.count("class ") >= 3, "Not enough permission classes found"


def test_repo_permissions_file_parses():
    """Modified Permissions.windows.cs has valid C# syntax (pass_to_pass)."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Quick syntax check - ensure braces are balanced\n"
        "open_braces = content.count('{')\n"
        "close_braces = content.count('}')\n"
        "open_parens = content.count('(')\n"
        "close_parens = content.count(')')\n"
        "\n"
        "if open_braces != close_braces:\n"
        "    print(f'FAIL: Brace mismatch - open: {open_braces}, close: {close_braces}')\n"
        "    sys.exit(1)\n"
        "if open_parens != close_parens:\n"
        "    print(f'FAIL: Paren mismatch - open: {open_parens}, close: {close_parens}')\n"
        "    sys.exit(1)\n"
        "\n"
        "# Check for basic C# structure\n"
        "if 'namespace' not in content:\n"
        "    print('FAIL: Missing namespace')\n"
        "    sys.exit(1)\n"
        "if 'class' not in content:\n"
        "    print('FAIL: Missing class definition')\n"
        "    sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"C# syntax validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_repo_file_headers_valid():
    """Modified files have valid headers and structure (pass_to_pass)."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Check for required C# file elements\n"
        "if 'using System' not in content:\n"
        "    print('FAIL: Missing using System'); sys.exit(1)\n"
        "\n"
        "# Must have namespace declaration\n"
        "if 'namespace Microsoft.Maui.ApplicationModel' not in content:\n"
        "    print('FAIL: Missing or incorrect namespace'); sys.exit(1)\n"
        "\n"
        "# Must have partial class for Permissions\n"
        "if 'public static partial class Permissions' not in content:\n"
        "    print('FAIL: Missing Permissions class'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"File header validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_no_stub_implementations():
    """Permissions file has no NotImplementedException stubs (pass_to_pass)."""
    r = _run_py(
        "import sys\n"
        "content = open('" + str(PERMISSIONS_FILE) + "').read()\n"
        "\n"
        "# Check for stub implementations\n"
        "stub_count = content.count('throw new NotImplementedException()')\n"
        "if stub_count > 0:\n"
        "    print(f'FAIL: Found {stub_count} NotImplementedException stubs'); sys.exit(1)\n"
        "\n"
        "# Check for placeholder methods (empty throw blocks)\n"
        "if '=> throw new' in content:\n"
        "    print('FAIL: Found expression-bodied throw stubs'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Stub check failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout
