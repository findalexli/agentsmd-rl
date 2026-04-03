"""
Task: maui-microphone-permission-unpackaged-app
Repo: dotnet/maui @ 260770c977f376c9b0190c03ed1a41920725f079
PR:   33179

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"
PERMISSIONS_FILE = Path(REPO) / "src/Essentials/src/Permissions/Permissions.windows.cs"
COPILOT_INSTRUCTIONS = Path(REPO) / ".github/copilot-instructions.md"
PR_FINALIZE_SKILL = Path(REPO) / ".github/skills/pr-finalize/SKILL.md"
COMPLETE_EXAMPLE = Path(REPO) / ".github/skills/pr-finalize/references/complete-example.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified C# file has balanced braces (basic syntax sanity)."""
    content = PERMISSIONS_FILE.read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert opens == closes, f"Unbalanced braces: {opens} open vs {closes} close"
    # Ensure file still has the Microphone class
    assert "class Microphone" in content or "partial class Microphone" in content, \
        "Microphone class not found in Permissions.windows.cs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_check_status_conditional_ensure_declared():
    """CheckStatusAsync must only call EnsureDeclared for packaged apps."""
    content = PERMISSIONS_FILE.read_text()

    # Find the Microphone.CheckStatusAsync method body
    # Look for the method and extract until next method or end
    check_match = re.search(
        r'public\s+override\s+Task<PermissionStatus>\s+CheckStatusAsync\s*\(\s*\)'
        r'(.*?)(?=public\s+override|async\s+Task<PermissionStatus>\s+TryRequest|\Z)',
        content,
        re.DOTALL,
    )
    assert check_match, "CheckStatusAsync method not found in Microphone class"
    method_body = check_match.group(1)

    # The fix wraps EnsureDeclared in an IsPackagedApp check
    assert "IsPackagedApp" in method_body, \
        "CheckStatusAsync should check IsPackagedApp before calling EnsureDeclared"
    assert "EnsureDeclared" in method_body, \
        "CheckStatusAsync should still call EnsureDeclared (conditionally)"


# [pr_diff] fail_to_pass
def test_request_async_conditional_ensure_declared():
    """RequestAsync must only call EnsureDeclared for packaged apps."""
    content = PERMISSIONS_FILE.read_text()

    # Extract text from RequestAsync declaration to the private CheckStatus method
    req_match = re.search(
        r'public\s+override\s+async\s+Task<PermissionStatus>\s+RequestAsync\s*\(\s*\)'
        r'(.*?)(?=private\s+DeviceAccessStatus\s+CheckStatus)',
        content,
        re.DOTALL,
    )
    assert req_match, "RequestAsync method not found in Microphone class"
    # This region includes RequestAsync and any helpers between it and CheckStatus
    region = req_match.group(1)

    # The fix wraps EnsureDeclared in an IsPackagedApp check
    assert "IsPackagedApp" in region, \
        "RequestAsync (or its helpers) should check IsPackagedApp before calling EnsureDeclared"


# [pr_diff] fail_to_pass
def test_request_async_checks_status_before_ensure():
    """RequestAsync should check permission status before calling EnsureDeclared."""
    content = PERMISSIONS_FILE.read_text()

    # Find RequestAsync method body
    req_match = re.search(
        r'public\s+override\s+async\s+Task<PermissionStatus>\s+RequestAsync\s*\(\s*\)'
        r'(.*?)(?=\bprivate\b|\bDeviceAccessStatus\s+CheckStatus\b|\Z)',
        content,
        re.DOTALL,
    )
    assert req_match, "RequestAsync method not found in Microphone class"
    method_body = req_match.group(1)

    # The fix reorders: check status BEFORE EnsureDeclared (or skip EnsureDeclared entirely)
    # On base commit, EnsureDeclared is the first call before any status check
    status_pos = method_body.find("CheckStatus()")
    ensure_pos = method_body.find("EnsureDeclared()")

    if ensure_pos == -1:
        # Agent removed EnsureDeclared entirely from RequestAsync — valid if guarded elsewhere
        assert "IsPackagedApp" in method_body, \
            "If EnsureDeclared is removed, must still guard on IsPackagedApp"
    else:
        # EnsureDeclared still present — must come after status check or inside IsPackagedApp guard
        assert status_pos != -1, "RequestAsync should call CheckStatus()"
        assert status_pos < ensure_pos, \
            "CheckStatus() should be called before EnsureDeclared() in RequestAsync"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_microphone_class_still_functional():
    """Microphone class retains required declarations and CheckStatus logic."""
    content = PERMISSIONS_FILE.read_text()
    # RequiredDeclarations must still declare "microphone"
    assert '"microphone"' in content, \
        "Microphone class should still declare 'microphone' capability"
    # CheckStatus private method must still exist
    assert "DeviceClass.AudioCapture" in content, \
        "CheckStatus should still use DeviceClass.AudioCapture"
    # MediaCapture initialization should still be present somewhere
    assert "MediaCaptureInitializationSettings" in content, \
        "MediaCapture initialization logic should still be present"


# [static] pass_to_pass
