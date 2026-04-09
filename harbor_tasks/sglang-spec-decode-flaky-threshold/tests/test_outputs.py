"""
Task: sglang-spec-decode-flaky-threshold
Repo: sgl-project/sglang @ 1ad6839659085732a6fe308f97141841d67f6323
PR:   22100

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: The modified test file (test_standalone_speculative_decoding.py) requires
GPUs to import/run, so we use AST parsing to verify the fix. This is justified
because the code cannot be executed in a CPU-only environment.
"""

import ast
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/spec/test_standalone_speculative_decoding.py"


def _parse_test_file():
    """Parse the test file and return the AST tree."""
    source = Path(TEST_FILE).read_text()
    return ast.parse(source)


def _get_class_node(tree, class_name):
    """Find a class definition by name in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _get_class_attr_value(class_node, attr_name):
    """Get the literal value of a class-level attribute assignment."""
    for item in class_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == attr_name:
                    if isinstance(item.value, ast.Constant):
                        return item.value.value
    return None


def _method_uses_assert(method_node, method_name):
    """Check which assert method is called for accuracy comparison in a method.

    Returns the assert method name (e.g., 'assertGreater', 'assertGreaterEqual')
    used with self.accuracy_threshold.
    """
    for node in ast.walk(method_node):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute) and
                    func.attr in ('assertGreater', 'assertGreaterEqual') and
                    isinstance(func.value, ast.Name) and func.value.id == 'self'):
                # Check if accuracy_threshold is referenced in args
                for arg in node.args:
                    if (isinstance(arg, ast.Attribute) and
                            isinstance(arg.value, ast.Name) and
                            arg.value.id == 'self' and
                            arg.attr == 'accuracy_threshold'):
                        return func.attr
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    source = Path(TEST_FILE).read_text()
    tree = ast.parse(source)
    assert tree is not None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_accuracy_threshold_v1():
    """TestStandaloneSpeculativeDecodingBase.accuracy_threshold must be 0.69.

    On the base commit it is 0.7, causing flaky failures when score == 0.7.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneSpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneSpeculativeDecodingBase not found"
    value = _get_class_attr_value(cls, "accuracy_threshold")
    assert value == 0.69, f"Expected accuracy_threshold=0.69, got {value}"


# [pr_diff] fail_to_pass
def test_accuracy_threshold_v2():
    """TestStandaloneV2SpeculativeDecodingBase.accuracy_threshold must be 0.69.

    Same flaky-threshold fix for the V2 speculative decoding base class.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneV2SpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneV2SpeculativeDecodingBase not found"
    value = _get_class_attr_value(cls, "accuracy_threshold")
    assert value == 0.69, f"Expected accuracy_threshold=0.69, got {value}"


# [pr_diff] fail_to_pass
def test_gsm8k_uses_greater_equal_v1():
    """V1 test_gsm8k must use assertGreaterEqual (not assertGreater).

    assertGreater(score, 0.7) fails when score == 0.7 exactly.
    assertGreaterEqual(score, 0.69) correctly accepts boundary values.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneSpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneSpeculativeDecodingBase not found"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
            used = _method_uses_assert(item, "test_gsm8k")
            assert used == "assertGreaterEqual", (
                f"Expected assertGreaterEqual for accuracy check, got {used}"
            )
            return
    raise AssertionError("test_gsm8k method not found in TestStandaloneSpeculativeDecodingBase")


# [pr_diff] fail_to_pass
def test_gsm8k_uses_greater_equal_v2():
    """V2 test_gsm8k must use assertGreaterEqual (not assertGreater).

    Same assertion fix for the V2 speculative decoding test class.
    """
    tree = _parse_test_file()
    cls = _get_class_node(tree, "TestStandaloneV2SpeculativeDecodingBase")
    assert cls is not None, "TestStandaloneV2SpeculativeDecodingBase not found"
    for item in cls.body:
        if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
            used = _method_uses_assert(item, "test_gsm8k")
            assert used == "assertGreaterEqual", (
                f"Expected assertGreaterEqual for accuracy check, got {used}"
            )
            return
    raise AssertionError("test_gsm8k method not found in TestStandaloneV2SpeculativeDecodingBase")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """test_gsm8k methods have real logic, not just pass/return."""
    tree = _parse_test_file()
    for class_name in ("TestStandaloneSpeculativeDecodingBase",
                       "TestStandaloneV2SpeculativeDecodingBase"):
        cls = _get_class_node(tree, class_name)
        assert cls is not None, f"{class_name} not found"
        for item in cls.body:
            if isinstance(item, ast.FunctionDef) and item.name == "test_gsm8k":
                stmts = [s for s in item.body
                         if not isinstance(s, (ast.Pass, ast.Expr))]
                assert len(stmts) >= 2, (
                    f"{class_name}.test_gsm8k body is a stub"
                )


# [agent_config] pass_to_pass — .claude/skills/write-sglang-test/SKILL.md:12 @ base
def test_inherits_custom_test_case():
    """Both base classes inherit from CustomTestCase per write-sglang-test skill.

    The skill mandates: 'Always use CustomTestCase — never raw unittest.TestCase.'
    """
    tree = _parse_test_file()
    for class_name in ("TestStandaloneSpeculativeDecodingBase",
                       "TestStandaloneV2SpeculativeDecodingBase"):
        cls = _get_class_node(tree, class_name)
        assert cls is not None, f"{class_name} not found"
        base_names = [
            b.id if isinstance(b, ast.Name) else b.attr
            for b in cls.bases
        ]
        assert "CustomTestCase" in base_names, (
            f"{class_name} must inherit from CustomTestCase, got bases: {base_names}"
        )
