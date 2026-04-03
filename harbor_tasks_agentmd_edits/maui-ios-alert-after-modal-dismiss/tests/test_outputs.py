"""
Task: maui-ios-alert-after-modal-dismiss
Repo: dotnet/maui @ 39325cec7d8a6de66e4608471b7843c7dfe3b4e1
PR:   32872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """AlertManager.iOS.cs must have balanced braces and valid C# structure."""
    path = Path(REPO) / "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
    content = path.read_text()
    # Basic structural check: balanced braces
    assert content.count("{") == content.count("}"), \
        "AlertManager.iOS.cs has unbalanced braces"
    # Must still contain the GetTopUIViewController method
    assert "GetTopUIViewController" in content, \
        "GetTopUIViewController method must exist in AlertManager.iOS.cs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dismissal_check_in_traversal():
    """GetTopUIViewController must check IsBeingDismissed when traversing the
    presented view controller chain, so it stops at the presenting controller
    when the presented one is being dismissed."""
    path = Path(REPO) / "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
    content = path.read_text()
    # The while loop that walks PresentedViewController must also check IsBeingDismissed
    assert "IsBeingDismissed" in content, \
        "AlertManager.iOS.cs must reference IsBeingDismissed to avoid returning a dismissing VC"


# [pr_diff] fail_to_pass
def test_traversal_skips_dismissing_controller():
    """GetTopUIViewController must not follow PresentedViewController when it is
    being dismissed. The method body should contain logic that uses both
    PresentedViewController and IsBeingDismissed together to avoid returning
    a controller that iOS will silently refuse to present on."""
    path = Path(REPO) / "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
    content = path.read_text()
    # Extract the GetTopUIViewController method definition body
    method_match = re.search(
        r'static\s+\w+\s+GetTopUIViewController\b.*?\{(.*?)\n\s*\}',
        content,
        re.DOTALL,
    )
    assert method_match, "Could not find GetTopUIViewController method definition"
    method_body = method_match.group(1)
    # The method must reference both PresentedViewController and IsBeingDismissed
    assert "PresentedViewController" in method_body, \
        "Method must traverse PresentedViewController chain"
    assert "IsBeingDismissed" in method_body, \
        "Method must check IsBeingDismissed to skip dismissing controllers"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — agent config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """GetTopUIViewController must have a real implementation with a while loop,
    not just a stub returning null or the root controller."""
    path = Path(REPO) / "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
    content = path.read_text()
    method_match = re.search(
        r'static\s+\w+\s+GetTopUIViewController\b.*?\{(.*?)\n\s*\}',
        content,
        re.DOTALL,
    )
    assert method_match, "GetTopUIViewController method definition not found"
    body = method_match.group(1)
    assert "while" in body, "GetTopUIViewController must contain a while loop"
    assert "PresentedViewController" in body, \
        "GetTopUIViewController must traverse PresentedViewController chain"
    assert "return" in body or "topUIViewController" in body, \
        "GetTopUIViewController must return a view controller"
