"""
Task: sglang-reopen-kl-accuracy-qwen3-specv2
Repo: sglang @ e9d92b0e33770651fd065c04ea28d0a5564e229d
PR:   22104

Verify that TestQwen3NextMTPV2 class has KLDivergenceMixin restored
and kl_div_thres threshold set.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/test/registered/4-gpu-models/test_qwen3_next_models_mtp.py"


def _get_ast_tree():
    """Parse the target file and return AST tree."""
    src = Path(TARGET_FILE).read_text()
    return ast.parse(src)


def _get_class_node(tree, class_name):
    """Find a class node by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _get_class_body_elements(class_node):
    """Extract class body elements: bases, assignments, comments."""
    bases = []
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            bases.append(base.id)
        elif isinstance(base, ast.Attribute):
            bases.append(f"{base.value.id}.{base.attr}" if isinstance(base.value, ast.Name) else base.attr)

    assignments = {}
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if isinstance(stmt.value, ast.Constant):
                        assignments[target.id] = stmt.value.value
                    elif isinstance(stmt.value, ast.List):
                        # For list values, just mark as list type
                        assignments[target.id] = "list"

    return bases, assignments


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    src = Path(TARGET_FILE).read_text()
    ast.parse(src)  # Will raise SyntaxError if invalid


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kl_divergence_mixin_added():
    """TestQwen3NextMTPV2 class should include KLDivergenceMixin in its bases."""
    tree = _get_ast_tree()
    class_node = _get_class_node(tree, "TestQwen3NextMTPV2")
    assert class_node is not None, "TestQwen3NextMTPV2 class not found"

    bases, _ = _get_class_body_elements(class_node)
    assert "KLDivergenceMixin" in bases, f"KLDivergenceMixin not found in class bases: {bases}"


# [pr_diff] fail_to_pass
def test_kl_div_thres_set():
    """TestQwen3NextMTPV2 class should have kl_div_thres = 0.0025."""
    tree = _get_ast_tree()
    class_node = _get_class_node(tree, "TestQwen3NextMTPV2")
    assert class_node is not None, "TestQwen3NextMTPV2 class not found"

    _, assignments = _get_class_body_elements(class_node)
    assert "kl_div_thres" in assignments, f"kl_div_thres not found in class. Assignments: {assignments}"
    assert assignments["kl_div_thres"] == 0.0025, f"kl_div_thres should be 0.0025, got {assignments['kl_div_thres']}"


# [pr_diff] fail_to_pass
def test_todo_comment_removed():
    """The TODO comment about re-adding KLDivergenceMixin should be removed."""
    src = Path(TARGET_FILE).read_text()

    # Check that the TODO comment is NOT present
    assert "TODO(hzh): After merging the PR that fixes specv2" not in src, \
        "TODO comment about re-adding KLDivergenceMixin should be removed"
    assert "add KLDivergenceMixin back" not in src, \
        "Reference to adding KLDivergenceMixin back should be removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_other_classes_unchanged():
    """Other test classes (TestQwen3NextMTP, TestQwen3NextMTPTopk) should retain KLDivergenceMixin."""
    tree = _get_ast_tree()

    # TestQwen3NextMTP should still have KLDivergenceMixin
    class1 = _get_class_node(tree, "TestQwen3NextMTP")
    assert class1 is not None, "TestQwen3NextMTP class not found"
    bases1, _ = _get_class_body_elements(class1)
    assert "KLDivergenceMixin" in bases1, f"TestQwen3NextMTP should retain KLDivergenceMixin: {bases1}"

    # TestQwen3NextMTPTopk should still have KLDivergenceMixin
    class2 = _get_class_node(tree, "TestQwen3NextMTPTopk")
    assert class2 is not None, "TestQwen3NextMTPTopk class not found"
    bases2, _ = _get_class_body_elements(class2)
    assert "KLDivergenceMixin" in bases2, f"TestQwen3NextMTPTopk should retain KLDivergenceMixin: {bases2}"


# [static] pass_to_pass
def test_gsm8k_mixin_preserved():
    """TestQwen3NextMTPV2 should still have GSM8KMixin."""
    tree = _get_ast_tree()
    class_node = _get_class_node(tree, "TestQwen3NextMTPV2")
    assert class_node is not None, "TestQwen3NextMTPV2 class not found"

    bases, _ = _get_class_body_elements(class_node)
    assert "GSM8KMixin" in bases, f"GSM8KMixin should be preserved: {bases}"
