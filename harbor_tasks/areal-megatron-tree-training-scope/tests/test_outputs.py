"""
Task: areal-megatron-tree-training-scope
Repo: AReaL @ 933218365af85d5488a554367d9fbe5071442b49
PR:   1135

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"
TARGET = "areal/engine/megatron_engine.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"py_compile failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mcore_model_in_tree_training_scope():
    """make_mcore_model must be called within the patch_bridge_for_tree_training context."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    # Walk the AST to find the patch_bridge_for_tree_training with-block,
    # then verify make_mcore_model is called within its body.
    found_context = False
    mcore_in_context = False

    for node in ast.walk(tree):
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            ctx = item.context_expr
            if not isinstance(ctx, ast.Call):
                continue
            func = ctx.func
            name = getattr(func, "id", None) or getattr(func, "attr", None)
            if name != "patch_bridge_for_tree_training":
                continue
            found_context = True
            # Search the with-block body (including nested blocks) for make_mcore_model
            for body_node in node.body:
                for sub in ast.walk(body_node):
                    if isinstance(sub, ast.Call):
                        f = sub.func
                        call_name = getattr(f, "id", None) or getattr(f, "attr", None)
                        if call_name == "make_mcore_model":
                            mcore_in_context = True

    assert found_context, "patch_bridge_for_tree_training context manager not found"
    assert mcore_in_context, (
        "make_mcore_model must be called inside patch_bridge_for_tree_training, "
        "but it was found outside the context manager"
    )


# [pr_diff] fail_to_pass
def test_device_context_nested_in_tree_training():
    """with self.device: containing make_mcore_model must not be at initialize() body level."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    # Walk to the initialize method, then check its direct children.
    # The bug: `with self.device:` (containing make_mcore_model) was a direct
    # child of initialize() instead of being nested inside patch_bridge_for_tree_training.
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "initialize"):
                continue
            for stmt in item.body:
                if not isinstance(stmt, ast.With):
                    continue
                # Check if this direct-child with-block is a tree training context
                is_tree_ctx = False
                for wi in stmt.items:
                    ctx = wi.context_expr
                    if isinstance(ctx, ast.Call):
                        name = getattr(ctx.func, "id", None) or getattr(ctx.func, "attr", None)
                        if name == "patch_bridge_for_tree_training":
                            is_tree_ctx = True
                if is_tree_ctx:
                    continue
                # Non-tree-training with-block directly in initialize body —
                # it must NOT contain make_mcore_model
                for sub in ast.walk(stmt):
                    if isinstance(sub, ast.Call):
                        f = sub.func
                        call_name = getattr(f, "id", None) or getattr(f, "attr", None)
                        if call_name == "make_mcore_model":
                            raise AssertionError(
                                "make_mcore_model is inside a with-block at initialize() "
                                "body level, but it should be nested inside "
                                "patch_bridge_for_tree_training"
                            )
            return

    raise AssertionError("initialize method not found")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_initialize_not_stub():
    """The initialize method must contain real logic, not just pass/return."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "initialize":
                body = [
                    s for s in item.body
                    if not isinstance(s, (ast.Pass, ast.Expr))
                    or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                ]
                assert len(body) >= 10, (
                    f"initialize() body has only {len(body)} meaningful statements — "
                    "expected substantial logic, not a stub"
                )
                return

    assert False, "initialize method not found in any class"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:93 @ 933218365af85d5488a554367d9fbe5071442b49
def test_no_wildcard_imports():
    """Modified file must not use wildcard imports (CLAUDE.md: Never use wildcard imports)."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    tree = ast.parse(src)

    wildcards = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    wildcards.append(f"from {node.module} import *")

    assert not wildcards, f"Wildcard imports found: {wildcards}"
