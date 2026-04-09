"""
Task: sglang-pause-generation-writer-lock-deadlock
Repo: sglang @ 8c3d80eabec2d2a41ccff4d15b5fc81e59d24fbe
PR:   22290

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = "python/sglang/srt/managers/tokenizer_communicator_mixin.py"


def get_function_source(filepath: str, func_name: str) -> str:
    """Extract the source code of a specific function."""
    src = Path(filepath).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            return ast.unparse(node)

    raise ValueError(f"Function {func_name} not found in {filepath}")


def function_contains_pattern(filepath: str, func_name: str, patterns: list) -> bool:
    """Check if function contains all specified patterns."""
    func_src = get_function_source(filepath, func_name)
    return all(p in func_src for p in patterns)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    src = Path(f"{REPO}/{TARGET_FILE}").read_text()
    ast.parse(src)  # Raises SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_update_weights_from_ipc_uses_pause_check():
    """
    update_weights_from_ipc must check is_pause before acquiring writer_lock.

    The bug: when scheduler is paused, existing readers block on is_pause_cond,
    so acquiring writer_lock would deadlock. The fix checks is_pause first
    and uses nullcontext() when paused (following the pattern in update_weights_from_distributed).
    """
    filepath = f"{REPO}/{TARGET_FILE}"

    # Must check is_pause before acquiring lock
    # Note: ast.unparse() may reformat, so check for semantic patterns
    patterns = [
        "async with self.is_pause_cond:",
        "is_paused = self.is_pause",
        "lock_context =",  # Assignment (parentheses may be elided by ast.unparse)
        "nullcontext()",  # The key fix: using nullcontext when paused
        "async with lock_context:",
    ]

    assert function_contains_pattern(
        filepath, "update_weights_from_ipc", patterns
    ), "update_weights_from_ipc must check is_pause before acquiring writer_lock"


# [pr_diff] fail_to_pass
def test_pattern_matches_reference_implementation():
    """
    The fix pattern must match the established pattern in update_weights_from_distributed.

    This ensures consistency in how pause-aware locking is implemented across
    similar weight update functions.
    """
    filepath = f"{REPO}/{TARGET_FILE}"

    # Get source of both functions
    ipc_src = get_function_source(filepath, "update_weights_from_ipc")
    dist_src = get_function_source(filepath, "update_weights_from_distributed")

    # Both must use the same pause-check pattern
    required_patterns = [
        "async with self.is_pause_cond:",
        "is_paused = self.is_pause",
        "lock_context =",
        "nullcontext()",
        "async with lock_context:",
    ]

    ipc_has_all = all(p in ipc_src for p in required_patterns)
    dist_has_all = all(p in dist_src for p in required_patterns)

    # Reference implementation should have the pattern (it had the fix already)
    # After fix, IPC implementation must also have the pattern
    assert ipc_has_all, (
        "update_weights_from_ipc must follow the same pause-aware locking "
        "pattern as update_weights_from_distributed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    filepath = f"{REPO}/{TARGET_FILE}"
    src = Path(filepath).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_weights_from_ipc":
            # Check function has meaningful body (not just pass/return/...)
            stmts = [s for s in node.body if not isinstance(s, (ast.Expr, ast.Pass))]
            assert len(stmts) >= 3, "Function body is a stub"

            # Must have try block with actual logic
            try_blocks = [s for s in node.body if isinstance(s, ast.Try)]
            assert len(try_blocks) >= 1, "Function should have try block for error handling"
            break
    else:
        raise ValueError("update_weights_from_ipc not found")


# [static] pass_to_pass
def test_function_structure_preserved():
    """
    Function maintains proper async structure and exception handling.
    The fix should not break the existing function structure.
    """
    filepath = f"{REPO}/{TARGET_FILE}"
    src = Path(filepath).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_weights_from_ipc":
            # Should have try-except block
            try_nodes = [s for s in node.body if isinstance(s, ast.Try)]
            assert len(try_nodes) >= 1, "Function must have try-except for error handling"

            # Should handle exceptions and return (success, message) tuple
            assert "return success, message" in src, "Function should return (success, message) tuple"
            break
    else:
        raise ValueError("update_weights_from_ipc not found")
