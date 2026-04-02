"""
Task: react-useactionstate-error-message
Repo: facebook/react @ 3bc2d414287e62a7b74731c6c7b837270353a339
PR:   35790

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_source_error_message_updated():
    """ReactFiberHooks.js must use 'action state' in the error message."""
    src = Path(f"{REPO}/packages/react-reconciler/src/ReactFiberHooks.js").read_text()
    assert "Cannot update action state while rendering." in src, (
        "ReactFiberHooks.js is missing the updated error message "
        "'Cannot update action state while rendering.'"
    )


# [pr_diff] fail_to_pass
def test_source_old_message_removed():
    """The old 'form state' error message must be gone from ReactFiberHooks.js."""
    src = Path(f"{REPO}/packages/react-reconciler/src/ReactFiberHooks.js").read_text()
    assert "Cannot update form state while rendering." not in src, (
        "ReactFiberHooks.js still contains the outdated error message "
        "'Cannot update form state while rendering.'"
    )


# [pr_diff] fail_to_pass
def test_test_file_error_message_updated():
    """ReactDOMForm-test.js must expect the updated 'action state' error message."""
    src = Path(
        f"{REPO}/packages/react-dom/src/__tests__/ReactDOMForm-test.js"
    ).read_text()
    assert "Cannot update action state while rendering." in src, (
        "ReactDOMForm-test.js is missing the updated error message"
    )


# [pr_diff] fail_to_pass
def test_error_codes_json_updated():
    """Error code 485 in codes.json must reference 'action state'."""
    codes = json.loads(
        Path(f"{REPO}/scripts/error-codes/codes.json").read_text()
    )
    actual = codes.get("485")
    assert actual == "Cannot update action state while rendering.", (
        f"codes.json key '485' has wrong value: {actual!r}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — consistency / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_error_codes_consistency():
    """The message for code 485 in codes.json must match the thrown message in ReactFiberHooks.js."""
    codes = json.loads(
        Path(f"{REPO}/scripts/error-codes/codes.json").read_text()
    )
    msg_485 = codes.get("485", "")
    assert msg_485, "Error code 485 missing from codes.json"
    src = Path(f"{REPO}/packages/react-reconciler/src/ReactFiberHooks.js").read_text()
    assert msg_485 in src, (
        f"Error code 485 message {msg_485!r} not found in ReactFiberHooks.js — "
        "codes.json and the source are out of sync"
    )
