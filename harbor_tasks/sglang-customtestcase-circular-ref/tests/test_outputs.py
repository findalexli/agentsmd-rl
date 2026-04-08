"""
Task: sglang-customtestcase-circular-ref
Repo: sgl-project/sglang @ afb32d76224e39d1226273d4a4a7fc568bd36b8c
PR:   #21650

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/test/test_utils.py"

# Self-contained helper code that extracts CustomTestCase from source
# without importing the full sglang package (which has heavy deps).
_EXTRACT_HELPER = r'''
import functools
import types
import unittest

TARGET = "/workspace/sglang/python/sglang/test/test_utils.py"

def _extract_custom_testcase():
    with open(TARGET) as f:
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
        raise RuntimeError("Could not find CustomTestCase")
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
'''


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess with the extraction helper."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(_EXTRACT_HELPER + "\n" + code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """test_utils.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dill_no_recursive_ref_warning():
    """dill.dumps on a CustomTestCase subclass must not emit recursive-ref warnings."""
    r = _run_python('''
import dill, warnings

CTC = _extract_custom_testcase()

class SerTest(CTC):
    @classmethod
    def setUpClass(cls):
        pass
    def test_example(self):
        pass

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    dill.dumps(SerTest)

recursive_warns = [x for x in w if "recursive self-references" in str(x.message)]
assert len(recursive_warns) == 0, (
    f"dill.dumps emitted {len(recursive_warns)} recursive-ref warning(s) — "
    f"circular reference not broken"
)
print("PASS")
''')
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Assertion failed in subprocess: {r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_no_circular_ref_in_setup_defaults():
    """safe_setUpClass must not hold a bound-method default that creates a circular ref."""
    r = _run_python('''
CTC = _extract_custom_testcase()

class SerTest(CTC):
    @classmethod
    def setUpClass(cls):
        pass
    def test_example(self):
        pass

# The wrapped setUpClass should not capture the original bound method
# as a default parameter (which creates cls -> setUpClass -> default -> __self__ -> cls).
setup_func = SerTest.setUpClass.__func__
defaults = setup_func.__defaults__
if defaults is not None:
    for d in defaults:
        if hasattr(d, "__self__"):
            assert d.__self__ is not SerTest, (
                "safe_setUpClass default parameter holds a bound method "
                "referencing back to the subclass — circular reference exists"
            )
print("PASS")
''')
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Assertion failed in subprocess: {r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dill_roundtrip_preserves_state():
    """dill round-trip preserves class attributes and identity."""
    r = _run_python('''
import dill, warnings
warnings.filterwarnings("ignore")

CTC = _extract_custom_testcase()

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
print("PASS")
''')
    assert r.returncode == 0, f"dill round-trip failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_teardown_called_on_setup_failure():
    """tearDownClass still runs when setUpClass raises."""
    r = _run_python('''
CTC = _extract_custom_testcase()

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
print("PASS")
''')
    assert r.returncode == 0, f"teardown test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_normal_setup_flow():
    """Normal setUpClass executes correctly and sets class state."""
    r = _run_python('''
CTC = _extract_custom_testcase()

class NormalTest(CTC):
    @classmethod
    def setUpClass(cls):
        cls.data = 99
    @classmethod
    def tearDownClass(cls):
        pass

NormalTest.setUpClass()
assert NormalTest.data == 99, f"setUpClass did not set data: {NormalTest.data}"
print("PASS")
''')
    assert r.returncode == 0, f"normal setup test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_no_double_wrapping():
    """Subclass of subclass doesn't double-wrap setUpClass."""
    r = _run_python('''
CTC = _extract_custom_testcase()

call_count = []

class Parent(CTC):
    @classmethod
    def setUpClass(cls):
        call_count.append(1)
    @classmethod
    def tearDownClass(cls):
        pass

class Child(Parent):
    pass

Child.setUpClass()
assert len(call_count) == 1, f"setUpClass called {len(call_count)} times (double-wrapped?)"
print("PASS")
''')
    assert r.returncode == 0, f"double-wrap test failed: {r.stderr}"
    assert "PASS" in r.stdout


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
