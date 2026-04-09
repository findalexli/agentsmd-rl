"""
Task: pytorch-inductor-identity-evalf
Repo: pytorch/pytorch @ f95d7a4bacff6a1e4f11a232c0f8a3f2b42bed4e
PR:   176783

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/torch/utils/_sympy/functions.py"

# Preamble that extracts the Identity class via AST+exec (torch C extensions unavailable)
_PREAMBLE = '''\
import ast, sympy
from pathlib import Path

source = Path("/workspace/pytorch/torch/utils/_sympy/functions.py").read_text()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Identity":
        lines = source.splitlines()[node.lineno - 1 : node.end_lineno]
        class_source = "\\n".join(lines)
        ns = {"sympy": sympy, "__builtins__": __builtins__}
        exec(class_source, ns)
        Identity = ns["Identity"]
        break
else:
    raise RuntimeError("Identity class not found")
'''


def _run_identity_test(test_code: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a Python script that tests Identity behavior in a subprocess."""
    return subprocess.run(
        ["python3", "-c", _PREAMBLE + test_code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_identity_integer_comparison():
    """Identity-wrapped integers can be compared (>=) without RecursionError."""
    r = _run_identity_test("""
cases = [
    (sympy.Integer(0), 0, True),
    (sympy.Integer(-6), 0, False),
    (sympy.Integer(5), 3, True),
    (sympy.Integer(-1), -1, True),
    (sympy.Integer(10), 10, True),
    (sympy.Integer(-100), 1, False),
]
for val, rhs, expected in cases:
    result = Identity(val) >= rhs
    assert bool(result) == expected, f"Identity({val}) >= {rhs}: expected {expected}, got {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_max_with_identity():
    """Max(0, Identity(x)) evaluates correctly for several values."""
    r = _run_identity_test("""
cases = [(-6, 0), (0, 0), (3, 3), (-1, 0), (100, 100), (-50, 0)]
for val, expected in cases:
    expr = Identity(sympy.Integer(val))
    result = sympy.Max(0, expr)
    assert float(result) == expected, f"Max(0, Identity({val})) should be {expected}, got {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rational_comparison():
    """Identity-wrapped rationals can be compared without RecursionError."""
    r = _run_identity_test("""
cases = [
    (sympy.Rational(1, 7), 0, True),
    (sympy.Rational(-3, 4), 0, False),
    (sympy.Rational(5, 2), 2, True),
    (sympy.Rational(-1, 3), -1, True),
    (sympy.Rational(7, 3), 3, False),
]
for rat, rhs, expected in cases:
    result = Identity(rat) >= rhs
    assert bool(result) == expected, f"Identity({rat}) >= {rhs}: expected {expected}, got {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_min_with_identity():
    """Min(0, Identity(x)) evaluates correctly."""
    r = _run_identity_test("""
cases = [(-6, -6), (0, 0), (3, 0), (-1, -1), (50, 0), (-99, -99)]
for val, expected in cases:
    expr = Identity(sympy.Integer(val))
    result = sympy.Min(0, expr)
    assert float(result) == expected, f"Min(0, Identity({val})) should be {expected}, got {result}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_all_comparison_operators():
    """All four comparison operators (__ge__, __gt__, __le__, __lt__) work."""
    r = _run_identity_test("""
a = Identity(sympy.Integer(5))
b = Identity(sympy.Integer(-3))
c = Identity(sympy.Integer(0))

# __gt__
assert bool(a > 0) is True
assert bool(b > 0) is False
assert bool(c > 0) is False
# __lt__
assert bool(a < 10) is True
assert bool(b < -5) is False
assert bool(c < 1) is True
# __le__
assert bool(a <= 5) is True
assert bool(a <= 4) is False
assert bool(c <= 0) is True
# __ge__
assert bool(b >= -3) is True
assert bool(b >= 0) is False
assert bool(c >= 0) is True
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) -- coding style
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:53-56 @ f95d7a4bacff6a1e4f11a232c0f8a3f2b42bed4e
def test_no_dynamic_attr_access_in_identity():
    """Identity class must not use dynamic setattr/getattr for state management."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    identity_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Identity":
            identity_class = node
            break

    assert identity_class is not None, "Identity class not found"

    for node in ast.walk(identity_class):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ("setattr", "getattr"):
                raise AssertionError(
                    f"Identity class uses dynamic {func.id}() — "
                    "prefer explicit class members (CLAUDE.md line 53-56)"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Identity class retains original methods and has non-trivial body."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    identity_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Identity":
            identity_class = node
            break

    assert identity_class is not None, "Identity class not found"

    methods = {
        n.name for n in ast.walk(identity_class)
        if isinstance(n, ast.FunctionDef)
    }
    assert "__int__" in methods, "Identity missing __int__"
    assert "__float__" in methods, "Identity missing __float__"

    class_lines = identity_class.end_lineno - identity_class.lineno
    assert class_lines >= 10, f"Identity class only {class_lines} lines -- likely stubbed"
