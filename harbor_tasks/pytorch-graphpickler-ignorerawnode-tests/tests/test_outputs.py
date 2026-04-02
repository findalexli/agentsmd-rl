"""
Task: pytorch-graphpickler-ignorerawnode-tests
Repo: pytorch/pytorch @ e931ab4802816cec55aa5a25b51f27cb941c924e
PR:   176954

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: torch is not installed; all checks are AST-based.
"""

import ast
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/test/fx/test_graph_pickler.py"


def _source():
    return Path(TARGET).read_text()


def _tree():
    return ast.parse(_source())


def _find_agent_test_methods():
    """Return test methods in classes that reference ignore_raw_node."""
    result = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    result.append(item)
    # Also catch top-level test functions
    for node in ast.iter_child_nodes(_tree()):
        if (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
                and "ignore_raw_node" in ast.dump(node)):
            result.append(node)
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target test file must parse without syntax errors."""
    ast.parse(_source())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_ignore_raw_node_tests():
    """Agent must add at least one test method that exercises ignore_raw_node."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, (
        "No test methods found that reference ignore_raw_node — "
        "add tests for GraphPickler.Options(ignore_raw_node=...)"
    )


# [pr_diff] fail_to_pass
def test_default_raises_covered():
    """A test must verify GraphPickler.dumps raises by default on raw Node metadata."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, "No test methods found"
    for m in methods:
        dump = ast.dump(m)
        if ("assertRaises" in dump or "assertRaisesRegex" in dump) and "dumps" in dump:
            return
    assert False, (
        "No test method covers the default-raises behavior: "
        "expected assertRaises/assertRaisesRegex + GraphPickler.dumps call"
    )


# [pr_diff] fail_to_pass
def test_ignore_true_round_trip():
    """A test must verify the ignore_raw_node=True round-trip (dumps then loads)."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, "No test methods found"
    for m in methods:
        dump = ast.dump(m)
        if "ignore_raw_node" in dump and "loads" in dump:
            return
    assert False, (
        "No test method tests the ignore_raw_node=True round-trip: "
        "expected a test that passes Options(ignore_raw_node=True) and calls loads()"
    )


# [pr_diff] fail_to_pass
def test_raw_node_in_meta():
    """Tests must inject a raw Node into node.meta to trigger the code path."""
    tree = _tree()
    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        if "ignore_raw_node" not in ast.dump(cls):
            continue
        for child in ast.walk(cls):
            # Match: something.meta[key] = value
            if (isinstance(child, ast.Assign)
                    and child.targets
                    and isinstance(child.targets[0], ast.Subscript)
                    and isinstance(child.targets[0].value, ast.Attribute)
                    and child.targets[0].value.attr == "meta"):
                return
    assert False, (
        "No assignment into node.meta found in agent's test code — "
        "tests must inject a raw Node (e.g. call_node.meta['key'] = call_node) "
        "to exercise the ignore_raw_node code path"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Agent must have >=2 test methods with real assertions and at least one pickler call."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 2, f"Found {len(methods)} test method(s), need >= 2"

    for m in methods:
        has_assert = any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and "assert" in child.func.attr.lower()
            for child in ast.walk(m)
        ) or any(isinstance(child, ast.Assert) for child in ast.walk(m))
        assert has_assert, f"{m.name} has no assertions (stub)"

        stmt_count = sum(
            1 for child in ast.walk(m)
            if isinstance(child, (ast.Assign, ast.Expr, ast.Assert, ast.With, ast.If))
        )
        assert stmt_count >= 3, f"{m.name} has only {stmt_count} statements (trivial)"

    any_pickler = any(
        "dumps" in ast.dump(m) or "loads" in ast.dump(m) for m in methods
    )
    assert any_pickler, "No test method calls dumps or loads — not testing pickling"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:17-27 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_pytorch_test_class():
    """Tests must use PyTorch's TestCase (not unittest.TestCase) — CLAUDE.md:17-27."""
    agent_classes = [
        n for n in ast.walk(_tree())
        if isinstance(n, ast.ClassDef) and "ignore_raw_node" in ast.dump(n)
    ]
    assert len(agent_classes) > 0, "No test class found for ignore_raw_node feature"

    for cls in agent_classes:
        # Reject: class Foo(unittest.TestCase)
        for base in cls.bases:
            if (isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    and isinstance(base.value, ast.Name)
                    and base.value.id == "unittest"):
                assert False, (
                    f"{cls.name} uses unittest.TestCase; "
                    "use TestCase from torch.testing._internal.common_utils — CLAUDE.md:17-27"
                )
        # Require: bare TestCase name (imported from torch)
        good = any(isinstance(b, ast.Name) and b.id == "TestCase" for b in cls.bases)
        assert good, (
            f"{cls.name} must inherit from TestCase "
            "(from torch.testing._internal.common_utils) — CLAUDE.md:17-27"
        )


# [agent_config] fail_to_pass — .claude/skills/pr-review/review-checklist.md:68 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_assert_raises_for_errors():
    """Error tests must use assertRaises/assertRaisesRegex, not bare try/except — review-checklist.md:68."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, "No test methods found"

    found = any(
        "assertRaises" in ast.dump(m) or "assertRaisesRegex" in ast.dump(m)
        for m in methods
    )
    assert found, (
        "No test method uses assertRaises/assertRaisesRegex for the error path — "
        "see review-checklist.md:68"
    )
