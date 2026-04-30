"""
Task: maui-add-pr-label-management-to
Repo: dotnet/maui @ d7d5e048c6941e80aa56982adff9aa48de260ed7
PR:   33739

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/maui"
PS1 = Path(REPO) / ".github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1"
SKILL_MD = Path(REPO) / ".github/skills/verify-tests-fail-without-fix/SKILL.md"

PS1_STR = str(PS1)
SKILL_MD_STR = str(SKILL_MD)


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code that validates repo file content."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_ps1_not_empty():
    """PowerShell script exists and is non-trivial."""
    content = PS1.read_text()
    assert len(content) > 5000, "Script should be substantial"
    assert "param(" in content, "Script should have parameter block"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_update_labels_function_logic():
    """Update-VerificationLabels implements correct toggle logic with REST API."""
    r = _run_py(
        "import re, sys\n"
        "content = open('" + PS1_STR + "').read()\n"
        "\n"
        "# Extract the function body by tracking braces\n"
        "match = re.search(r'function\\s+Update-VerificationLabels\\s*\\{', content)\n"
        "if not match:\n"
        "    print('FAIL: function not found'); sys.exit(1)\n"
        "\n"
        "start = match.end() - 1\n"
        "depth = 0\n"
        "body = ''\n"
        "for i in range(start, len(content)):\n"
        "    if content[i] == '{': depth += 1\n"
        "    elif content[i] == '}':\n"
        "        depth -= 1\n"
        "        if depth == 0:\n"
        "            body = content[start:i+1]\n"
        "            break\n"
        "if not body:\n"
        "    print('FAIL: could not find function end'); sys.exit(1)\n"
        "\n"
        "# Validate toggle logic: conditional assignment of labelToAdd/labelToRemove\n"
        "if '$labelToAdd' not in body:\n"
        "    print('FAIL: no $labelToAdd variable'); sys.exit(1)\n"
        "if '$labelToRemove' not in body:\n"
        "    print('FAIL: no $labelToRemove variable'); sys.exit(1)\n"
        "if '$LabelConfirmed' not in body or '$LabelFailed' not in body:\n"
        "    print('FAIL: label constants not referenced in function'); sys.exit(1)\n"
        "\n"
        "# Must use REST API DELETE for removal\n"
        "if 'DELETE' not in body:\n"
        "    print('FAIL: no DELETE method for label removal'); sys.exit(1)\n"
        "# Must use REST API POST for addition\n"
        "if 'POST' not in body:\n"
        "    print('FAIL: no POST method for label addition'); sys.exit(1)\n"
        "# Must check $LASTEXITCODE for error handling\n"
        "if '$LASTEXITCODE' not in body:\n"
        "    print('FAIL: no error handling via $LASTEXITCODE'); sys.exit(1)\n"
        "# Must have guard for unknown PR number\n"
        "if 'unknown' not in body:\n"
        "    print('FAIL: no guard for unknown PR number'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Function logic validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_label_names_and_constants():
    """Script defines $LabelConfirmed and $LabelFailed with correct label strings."""
    r = _run_py(
        "import re, sys\n"
        "content = open('" + PS1_STR + "').read()\n"
        "\n"
        "confirmed = re.search(r'\\$LabelConfirmed\\s*=\\s*[\"\']([^\"\']+)[\"\']', content)\n"
        "failed = re.search(r'\\$LabelFailed\\s*=\\s*[\"\']([^\"\']+)[\"\']', content)\n"
        "if not confirmed:\n"
        "    print('FAIL: $LabelConfirmed not defined'); sys.exit(1)\n"
        "if not failed:\n"
        "    print('FAIL: $LabelFailed not defined'); sys.exit(1)\n"
        "\n"
        "c, f = confirmed.group(1), failed.group(1)\n"
        "if 'ai-reproduction-confirmed' not in c:\n"
        "    print(f'FAIL: unexpected confirmed label: {c}'); sys.exit(1)\n"
        "if 'ai-reproduction-failed' not in f:\n"
        "    print(f'FAIL: unexpected failed label: {f}'); sys.exit(1)\n"
        "if c == f:\n"
        "    print('FAIL: labels must be different'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Label constants validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_labels_called_on_all_paths():
    """Update-VerificationLabels called with correct bool in all 4 verification paths."""
    r = _run_py(
        "import re, sys\n"
        "content = open('" + PS1_STR + "').read()\n"
        "\n"
        "true_calls = re.findall(\n"
        "    r'Update-VerificationLabels\\s+-ReproductionConfirmed\\s+\\$true', content\n"
        ")\n"
        "false_calls = re.findall(\n"
        "    r'Update-VerificationLabels\\s+-ReproductionConfirmed\\s+\\$false', content\n"
        ")\n"
        "if len(true_calls) < 2:\n"
        "    print(f'FAIL: expected >= 2 $true calls, found {len(true_calls)}'); sys.exit(1)\n"
        "if len(false_calls) < 2:\n"
        "    print(f'FAIL: expected >= 2 $false calls, found {len(false_calls)}'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"Label calls validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_pr_detection_fallback():
    """PR detection has gh pr list --head fallback for fork branches."""
    r = _run_py(
        "import sys\n"
        "content = open('" + PS1_STR + "').read()\n"
        "\n"
        "if 'gh pr view' not in content:\n"
        "    print('FAIL: missing gh pr view primary detection'); sys.exit(1)\n"
        "if 'gh pr list' not in content:\n"
        "    print('FAIL: missing gh pr list fallback'); sys.exit(1)\n"
        "if '--head' not in content:\n"
        "    print('FAIL: missing --head flag in fallback'); sys.exit(1)\n"
        "if '$foundPR' not in content:\n"
        "    print('FAIL: missing $foundPR tracking variable'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"PR detection fallback validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


def test_skill_md_labels_section():
    """SKILL.md has PR Labels section with both labels, table, and toggle behavior."""
    r = _run_py(
        "import sys\n"
        "content = open('" + SKILL_MD_STR + "').read()\n"
        "\n"
        "if '## PR Labels' not in content:\n"
        "    print('FAIL: missing ## PR Labels section'); sys.exit(1)\n"
        "if 'ai-reproduction-confirmed' not in content:\n"
        "    print('FAIL: SKILL.md missing ai-reproduction-confirmed'); sys.exit(1)\n"
        "if 'ai-reproduction-failed' not in content:\n"
        "    print('FAIL: SKILL.md missing ai-reproduction-failed'); sys.exit(1)\n"
        "# Must describe toggle behavior\n"
        "lower = content.lower()\n"
        "if 'remove' not in lower or 'add' not in lower:\n"
        "    print('FAIL: SKILL.md does not describe label toggle (add/remove)'); sys.exit(1)\n"
        "# Must have label table\n"
        "if '|' not in content or 'Label' not in content:\n"
        "    print('FAIL: SKILL.md missing label table'); sys.exit(1)\n"
        "# Workflow steps must mention PR labels\n"
        "if 'pr labels' not in lower:\n"
        "    print('FAIL: workflow steps do not mention PR labels'); sys.exit(1)\n"
        "\n"
        "print('PASS')\n"
    )
    assert r.returncode == 0, f"SKILL.md validation failed: {r.stdout}{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_existing_verify_failure_mode_preserved():
    """The verify-failure-only mode logic must still be present."""
    content = PS1.read_text()
    assert "DetectedFixFiles" in content, \
        "Fix file detection logic must be preserved"
    assert "VERIFICATION PASSED" in content, \
        "Success output must be preserved"
    assert "RequireFullVerification" in content, \
        "RequireFullVerification parameter must be preserved"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD validation
# ---------------------------------------------------------------------------


def test_powershell_script_basic_structure():
    """PowerShell script has basic valid structure.

    This is a pass_to_pass gate that validates the PowerShell script structure
    without requiring PowerShell to be installed.
    """
    content = PS1.read_text()

    # Basic structure checks
    assert content.startswith("#!/usr/bin/env pwsh"), \
        "Script should have PowerShell shebang"
    assert "<#" in content and "#>" in content, \
        "Script should have help comment block"
    assert "param(" in content, \
        "Script should have parameter block"
    assert "$ErrorActionPreference" in content, \
        "Script should set error handling preference"

    # Count braces (simple check - not perfect but catches major issues)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Count parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_shared_baseline_script_imports():
    """Verify-tests-fail.ps1 imports from EstablishBrokenBaseline.ps1.

    This validates the dependency chain with the shared baseline script
    that provides common test detection utilities.
    """
    content = PS1.read_text()

    # Script should import from the baseline script
    assert "EstablishBrokenBaseline.ps1" in content, \
        "Script must reference EstablishBrokenBaseline.ps1"
    assert "Test-IsTestFile" in content or "Find-MergeBase" in content, \
        "Script should import shared utilities from baseline script"


def test_skill_md_documentation_structure():
    """SKILL.md has required documentation sections.

    Validates that the documentation includes all required sections
    for the skill to be usable by AI agents.
    """
    content = SKILL_MD.read_text()

    # For base commit, check that the file has the basic structure
    # The ## Description section is in the YAML frontmatter, not a heading
    required_patterns = [
        ("name:", "name field in frontmatter"),
        ("description:", "description field in frontmatter"),
        ("## Mode 1:", "Mode 1 section"),
        ("## Mode 2:", "Mode 2 section"),
        ("## Requirements", "Requirements section"),
        ("## Output Files", "Output Files section"),
    ]

    for pattern, desc in required_patterns:
        assert pattern in content, f"SKILL.md missing {desc}"

    # Verify it has code examples
    assert "```" in content, "SKILL.md should have code examples"


def test_git_repository_integrity():
    """Git repository is in expected state for verification.

    Validates that the git repo is properly initialized and at the
    expected base commit.
    """
    import subprocess

    # Check git status works
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=REPO
    )
    assert result.returncode == 0, "Git status failed"

    # Verify we're at the expected base commit
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=REPO
    )
    assert result.returncode == 0, "Git rev-parse failed"
    head_commit = result.stdout.strip()

    # Should be at the expected base commit
    expected_commit = "d7d5e048c6941e80aa56982adff9aa48de260ed7"
    assert head_commit == expected_commit, \
        f"Expected commit {expected_commit}, got {head_commit}"
