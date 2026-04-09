"""
Task: sglang-toctou-weight-update-locking
Repo: sglang @ eca62ab8f48359bfc8d1602c36aa88f7ba84a46c
PR:   22304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This task tests for a TOCTOU race fix in pause-aware weight update locking.
The bug: is_pause was read under is_pause_cond lock, then the lock was released,
and a lock decision was made based on the stale value.
The fix: when paused, the weight update runs inside the is_pause_cond scope.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/srt/managers/tokenizer_communicator_mixin.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    src = Path(TARGET_FILE).read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nullcontext_import_removed():
    """The nullcontext import must be removed (it was used for the buggy locking)."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "contextlib":
                for alias in node.names:
                    if alias.name == "nullcontext":
                        raise AssertionError(
                            "nullcontext import found - should be removed in the fix"
                        )


# [pr_diff] fail_to_pass
def test_locking_pattern_fixed_in_distributed():
    """update_weights_from_distributed must hold is_pause_cond during update when paused."""
    src = Path(TARGET_FILE).read_text()

    # The fix should:
    # 1. Read is_paused inside is_pause_cond block
    # 2. When is_paused is True, do the update INSIDE that block
    # 3. When is_paused is False, do the update under writer_lock OUTSIDE the is_pause_cond block

    # Check that the buggy pattern (lock_context = ... nullcontext) is gone
    if "lock_context" in src and "nullcontext" in src:
        raise AssertionError("Buggy lock_context pattern still present")

    # Check for the fixed pattern in update_weights_from_distributed
    # The fix moves the communicator call inside the is_pause_cond block when paused
    func_start = src.find("async def update_weights_from_distributed(")
    func_end = src.find("async def init_weights_send_group_for_remote_instance", func_start)
    func_src = src[func_start:func_end]

    # Should have the pattern: async with self.is_pause_cond: ... if is_paused: ... communicator call
    if "async with self.is_pause_cond:" not in func_src:
        raise AssertionError("Missing is_pause_cond lock in update_weights_from_distributed")

    # Should have the conditional update pattern
    if "if is_paused:" not in func_src:
        raise AssertionError("Missing 'if is_paused' check in update_weights_from_distributed")

    # The fix should have the communicator call inside the if is_paused block
    # (checking that update_weights_from_distributed_communicator appears after if is_paused)
    is_paused_idx = func_src.find("if is_paused:")
    communicator_call = "update_weights_from_distributed_communicator"
    first_communicator_idx = func_src.find(communicator_call)

    if first_communicator_idx == -1:
        raise AssertionError(f"Missing {communicator_call} call")

    # In the fixed version, the FIRST communicator call should be inside the if is_paused block
    # which comes before any "if not is_paused" block
    if first_communicator_idx < is_paused_idx:
        raise AssertionError(
            "Communicator call found before 'if is_paused' - should be inside the paused block"
        )


# [pr_diff] fail_to_pass
def test_locking_pattern_fixed_in_tensor():
    """update_weights_from_tensor must hold is_pause_cond during update when paused."""
    src = Path(TARGET_FILE).read_text()

    func_start = src.find("async def update_weights_from_tensor(")
    func_end = src.find("async def update_weights_from_ipc", func_start)
    func_src = src[func_start:func_end]

    if "async with self.is_pause_cond:" not in func_src:
        raise AssertionError("Missing is_pause_cond lock in update_weights_from_tensor")

    if "if is_paused:" not in func_src:
        raise AssertionError("Missing 'if is_paused' check in update_weights_from_tensor")

    is_paused_idx = func_src.find("if is_paused:")
    communicator_call = "update_weights_from_tensor_communicator"
    first_communicator_idx = func_src.find(communicator_call)

    if first_communicator_idx == -1:
        raise AssertionError(f"Missing {communicator_call} call")

    if first_communicator_idx < is_paused_idx:
        raise AssertionError(
            "Communicator call found before 'if is_paused' - should be inside the paused block"
        )


# [pr_diff] fail_to_pass
def test_locking_pattern_fixed_in_ipc():
    """update_weights_from_ipc must hold is_pause_cond during update when paused."""
    src = Path(TARGET_FILE).read_text()

    func_start = src.find("async def update_weights_from_ipc(")
    # Find end of function (next async def or class end)
    func_end = len(src)
    for marker in ["async def init_weights_send_group_for_remote_instance", "\nclass ", "\n# "]:
        idx = src.find(marker, func_start + 1)
        if idx != -1 and idx < func_end:
            func_end = idx

    func_src = src[func_start:func_end]

    if "async with self.is_pause_cond:" not in func_src:
        raise AssertionError("Missing is_pause_cond lock in update_weights_from_ipc")

    if "if is_paused:" not in func_src:
        raise AssertionError("Missing 'if is_paused' check in update_weights_from_ipc")

    is_paused_idx = func_src.find("if is_paused:")
    communicator_call = "update_weights_from_ipc_communicator"
    first_communicator_idx = func_src.find(communicator_call)

    if first_communicator_idx == -1:
        raise AssertionError(f"Missing {communicator_call} call")

    if first_communicator_idx < is_paused_idx:
        raise AssertionError(
            "Communicator call found before 'if is_paused' - should be inside the paused block"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_functions_not_stub():
    """Modified functions have real logic (not just pass/return)."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    target_funcs = [
        "update_weights_from_distributed",
        "update_weights_from_tensor",
        "update_weights_from_ipc",
    ]

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name in target_funcs:
            # Count non-trivial statements (not Pass, not docstring)
            meaningful = [
                s
                for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
                and not (isinstance(s, ast.Constant) and isinstance(s.value, str))
            ]
            assert len(meaningful) >= 3, f"{node.name} appears to be a stub"
