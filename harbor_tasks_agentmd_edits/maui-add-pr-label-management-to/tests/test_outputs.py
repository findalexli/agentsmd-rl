"""
Task: maui-add-pr-label-management-to
Repo: dotnet/maui @ d7d5e048c6941e80aa56982adff9aa48de260ed7
PR:   33739

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"
PS1 = Path(REPO) / ".github/skills/verify-tests-fail-without-fix/scripts/verify-tests-fail.ps1"
SKILL_MD = Path(REPO) / ".github/skills/verify-tests-fail-without-fix/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ps1_not_empty():
    """PowerShell script exists and is non-trivial."""
    content = PS1.read_text()
    assert len(content) > 5000, "Script should be substantial"
    assert "param(" in content, "Script should have parameter block"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_update_labels_function_defined():
    """Script must define Update-VerificationLabels with label add/remove logic."""
    content = PS1.read_text()
    # Function must exist
    assert re.search(r"function\s+Update-VerificationLabels", content), \
        "Must define Update-VerificationLabels function"
    # Must accept a boolean parameter for reproduction status
    assert "ReproductionConfirmed" in content, \
        "Function must have ReproductionConfirmed parameter"
    # Must use gh CLI to manage labels
    assert "gh api" in content or "gh pr edit" in content or "gh issue edit" in content, \
        "Must use gh CLI for label management"


# [pr_diff] fail_to_pass
def test_label_names_defined():
    """Script must define both confirmed and failed label name strings."""
    content = PS1.read_text()
    assert "s/ai-reproduction-confirmed" in content, \
        "Must define the confirmed label name"
    assert "s/ai-reproduction-failed" in content, \
        "Must define the failed label name"


# [pr_diff] fail_to_pass
def test_labels_called_on_verification_pass():
    """Update-VerificationLabels must be called with $true on verification pass."""
    content = PS1.read_text()
    # Find calls with ReproductionConfirmed $true
    true_calls = re.findall(
        r"Update-VerificationLabels\s+-ReproductionConfirmed\s+\$true", content
    )
    assert len(true_calls) >= 2, \
        f"Expected at least 2 calls with $true (simple + full mode), found {len(true_calls)}"


# [pr_diff] fail_to_pass
def test_labels_called_on_verification_fail():
    """Update-VerificationLabels must be called with $false on verification fail."""
    content = PS1.read_text()
    # Find calls with ReproductionConfirmed $false
    false_calls = re.findall(
        r"Update-VerificationLabels\s+-ReproductionConfirmed\s+\$false", content
    )
    assert len(false_calls) >= 2, \
        f"Expected at least 2 calls with $false (simple + full mode), found {len(false_calls)}"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_verify_failure_mode_preserved():
    """The verify-failure-only mode logic must still be present."""
    content = PS1.read_text()
    assert "DetectedFixFiles" in content, \
        "Fix file detection logic must be preserved"
    assert "VERIFICATION PASSED" in content, \
        "Success output must be preserved"
    assert "RequireFullVerification" in content, \
        "RequireFullVerification parameter must be preserved"


# [static] pass_to_pass
