"""
Task: sglang-customtestcase-circular-ref
Repo: sgl-project/sglang @ afb32d76224e39d1226273d4a4a7fc568bd36b8c
PR:   #21650

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import functools
import types
import unittest

TARGET = "/workspace/sglang/python/sglang/test/test_utils.py"


def _extract_custom_testcase(path=TARGET):
    """Extract CustomTestCase from source without importing heavy sglang deps."""
    with open(path) as f:
        source = f.read()
    lines = source.split("\n")
    in_class = False
    indent = None
    method_lines = []
    for line in lines:
        if "class CustomTestCase(unittest.TestCase):" in line:
            in_class = True
            indent = len(line) - len(line.lstrip())
            continue
        if in_class:
            if line.strip() == "":
                method_lines.append(line)
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent and line.strip():
                break
            method_lines.append(line)
    if not method_lines:
        return None
    min_indent = min(
        (len(l) - len(l.lstrip()) for l in method_lines if l.strip()), default=0
    )
    reindented = [
        "    " + l[min_indent:] if l.strip() else "" for l in method_lines
    ]
    ns = {"__builtins__": __builtins__, "functools": functools}
    exec(
        "import unittest\nimport functools\n\nclass CustomTestCase(unittest.TestCase):\n"
        + "\n".join(reindented),
        ns,
    )
    return ns["CustomTestCase"]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """test_utils.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dill_serialize_subclass():
    """dill.dumps succeeds on a CustomTestCase subclass (no circular ref error)."""
    import dill

    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    class SerTest(CTC):
        @classmethod
        def setUpClass(cls):
            pass

        def test_example(self):
            pass

    # Core bug: bound method default param creates a reference cycle that
    # breaks dill serialization.
    dill.dumps(SerTest)


# [pr_diff] fail_to_pass
def test_dill_roundtrip_preserves_state():
    """dill round-trip preserves class attributes and identity."""
    import dill

    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    class RoundTripTest(CTC):
        CLASS_VAR = "hello"
        NUMERIC = 42

        @classmethod
        def setUpClass(cls):
            pass

        def test_example(self):
            pass

    data = dill.dumps(RoundTripTest)
    restored = dill.loads(data)
    assert restored.CLASS_VAR == "hello", f"Lost CLASS_VAR: {restored.CLASS_VAR}"
    assert restored.NUMERIC == 42, f"Lost NUMERIC: {restored.NUMERIC}"
    assert restored.__name__ == "RoundTripTest", f"Lost name: {restored.__name__}"


# [pr_diff] fail_to_pass
def test_dill_serialize_inner_class():
    """dill.dumps succeeds on a class defined inside a CustomTestCase subclass scope."""
    import dill

    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    class OuterTest(CTC):
        @classmethod
        def setUpClass(cls):
            pass

        def test_example(self):
            pass

    # Inner class referencing the subclass — this is the pattern from the bug report
    class InnerClass:
        parent = OuterTest

    dill.dumps(InnerClass)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_teardown_called_on_setup_failure():
    """tearDownClass still runs when setUpClass raises."""
    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    teardown_called = []

    class FailingSetup(CTC):
        @classmethod
        def setUpClass(cls):
            raise RuntimeError("intentional failure")

        @classmethod
        def tearDownClass(cls):
            teardown_called.append(True)

    try:
        FailingSetup.setUpClass()
    except RuntimeError:
        pass

    assert teardown_called, "tearDownClass was not called after setUpClass failure"


# [pr_diff] pass_to_pass
def test_normal_setup_flow():
    """Normal setUpClass executes correctly and sets class state."""
    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    class NormalTest(CTC):
        @classmethod
        def setUpClass(cls):
            cls.data = 99

        @classmethod
        def tearDownClass(cls):
            pass

    NormalTest.setUpClass()
    assert NormalTest.data == 99, f"setUpClass did not set data: {NormalTest.data}"


# [pr_diff] pass_to_pass
def test_no_double_wrapping():
    """Subclass of subclass doesn't double-wrap setUpClass."""
    CTC = _extract_custom_testcase()
    assert CTC is not None, "Could not extract CustomTestCase"

    call_count = []

    class Parent(CTC):
        @classmethod
        def setUpClass(cls):
            call_count.append(1)

        @classmethod
        def tearDownClass(cls):
            pass

    class Child(Parent):
        pass  # inherits setUpClass

    Child.setUpClass()
    assert len(call_count) == 1, f"setUpClass called {len(call_count)} times (double-wrapped?)"


# ---------------------------------------------------------------------------
# Anti-stub (static) — ensure meaningful implementation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_init_subclass_not_stub():
    """__init_subclass__ has meaningful logic (not gutted to pass/return)."""
    import ast

    with open(TARGET) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CustomTestCase":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init_subclass__":
                    stmts = [
                        s
                        for s in item.body
                        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
                    ]
                    assert len(stmts) >= 3, (
                        f"__init_subclass__ too shallow ({len(stmts)} statements)"
                    )
                    return
            raise AssertionError("No __init_subclass__ found in CustomTestCase")
    raise AssertionError("CustomTestCase class not found")
