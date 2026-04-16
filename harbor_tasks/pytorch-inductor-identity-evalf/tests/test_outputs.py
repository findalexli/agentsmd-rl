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
# Pass-to-pass (repo_tests) -- CI/CD gates that should pass on base AND after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_flake8_syntax():
    """Repo's Python flake8 syntax check passes (pass_to_pass)."""
    # Ensure flake8 is installed
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["python3", "-m", "flake8", TARGET, "--select=E9,F63,F7,F82", "--show-source"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Flake8 syntax check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """Target file compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_test_sympy_utils_syntax():
    """Test file for sympy utils compiles without errors (pass_to_pass)."""
    test_file = f"{REPO}/test/test_sympy_utils.py"
    r = subprocess.run(
        ["python3", "-m", "py_compile", test_file],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Test file compile failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_identity_class_ast():
    """Identity class AST structure is valid (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import ast
source = open('{TARGET}').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Identity':
        methods = {{n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)}}
        assert '__int__' in methods, 'Missing __int__'
        assert '__float__' in methods, 'Missing __float__'
        assert '_eval_expand_identity' in methods, 'Missing _eval_expand_identity'
        print('OK')
        break
else:
    raise RuntimeError('Identity class not found')
"""
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"AST check failed:\n{r.stderr}"
    assert "OK" in r.stdout, f"Expected OK in output, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_repo_sympy_functions_imports():
    """Target file imports are valid Python (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import ast
source = open('{TARGET}').read()
tree = ast.parse(source)
errors = []
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == '*':
                errors.append(f"Star import at line {{node.lineno}}")
    elif isinstance(node, ast.ImportFrom):
        if node.module and node.level != 0:
            # Check relative imports are valid
            pass
if errors:
    raise AssertionError('Import errors: ' + '; '.join(errors))
print('Imports OK')
"""
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (repo_tests) -- tests that verify the fix is present
# ---------------------------------------------------------------------------

# [repo_tests] fail_to_pass
def test_identity_has_comparison_methods():
    """Identity-wrapped integers produce correct boolean results for all comparison operators."""
    r = _run_identity_test("""
a = Identity(sympy.Integer(7))
b = Identity(sympy.Integer(-2))
c = Identity(sympy.Integer(0))

# boundary: value == rhs
assert bool(a >= 7) is True
assert bool(a > 7) is False
assert bool(a <= 7) is True
assert bool(a < 7) is False

# boundary: value vs rhs +/- 1
assert bool(a >= 8) is False
assert bool(a > 6) is True
assert bool(a <= 6) is False
assert bool(a < 8) is True

# negative values
assert bool(b >= -2) is True
assert bool(b >= 0) is False
assert bool(b > -3) is True
assert bool(b > -2) is False
assert bool(b <= -2) is True
assert bool(b < -1) is True
assert bool(b < -3) is False

# zero
assert bool(c >= 0) is True
assert bool(c > 0) is False
assert bool(c <= 0) is True
assert bool(c < 0) is False

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] fail_to_pass
def test_identity_has_helper_compare_method():
    """Identity numeric comparisons and Max/Min complete without RecursionError."""
    r = _run_identity_test("""
import sys
old_limit = sys.getrecursionlimit()
sys.setrecursionlimit(200)
try:
    # Integer comparisons must complete without hitting recursion limit
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
        assert bool(result) == expected, f"Identity({val}) >= {rhs}: expected {expected}"

    # Rational comparisons must also work
    assert bool(Identity(sympy.Rational(1, 7)) >= 0) is True
    assert bool(Identity(sympy.Rational(-3, 4)) >= 0) is False

    # Max/Min internally rely on comparisons
    assert float(sympy.Max(0, Identity(sympy.Integer(-6)))) == 0
    assert float(sympy.Max(0, Identity(sympy.Integer(3)))) == 3
    assert float(sympy.Min(0, Identity(sympy.Integer(-1)))) == -1
    assert float(sympy.Min(0, Identity(sympy.Integer(50)))) == 0
finally:
    sys.setrecursionlimit(old_limit)

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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
