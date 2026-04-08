"""
Task: pytorch-mps-modular-indexing-safe-mod
Repo: pytorch/pytorch @ 483b55d84c74b92b3c2c67be4b9b7c7359ec2bbc
PR:   178009

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
import textwrap
from pathlib import Path

import sympy

REPO = "/workspace/pytorch"


# ---------------------------------------------------------------------------
# Helpers for inline (p2p) tests
# ---------------------------------------------------------------------------

def _extract_method(filepath, method_name):
    """Extract a method from mps.py via AST and return it as a callable."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
            ns = {"__builtins__": __builtins__, "sympy": sympy}
            for attr in dir(sympy):
                if not attr.startswith("_"):
                    ns[attr] = getattr(sympy, attr)
            exec(func_src, ns)
            return ns[method_name]
    return None


class _FakePrinter:
    """Minimal printer mock — converts sympy objects to str."""

    def doprint(self, x):
        return str(x)

    def _print(self, x):
        return str(x)

    def parenthesize(self, x, *a, **kw):
        return str(x)


class _FakeExpr:
    """Mock for a ModularIndexing expression with (base, div, mod)."""

    def __init__(self, x, div, mod):
        self.args = (x, div, mod)
        self.is_integer = True


class _FakeFloorDivExpr:
    """Mock for a FloorDiv expression with (base, div)."""

    def __init__(self, x, div):
        self.args = (x, div)
        self.is_integer = True


# ---------------------------------------------------------------------------
# Subprocess helper for behavioral f2p tests
# ---------------------------------------------------------------------------

_SUBPROCESS_HELPER = '''
import ast, textwrap, re
from pathlib import Path
import sympy

def _extract_method(filepath, method_name):
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
            ns = {"__builtins__": __builtins__, "sympy": sympy}
            for attr in dir(sympy):
                if not attr.startswith("_"):
                    ns[attr] = getattr(sympy, attr)
            exec(func_src, ns)
            return ns[method_name]
    return None

class _FakePrinter:
    def doprint(self, x): return str(x)
    def _print(self, x): return str(x)
    def parenthesize(self, x, *a, **kw): return str(x)

class _FakeExpr:
    def __init__(self, x, div, mod):
        self.args = (x, div, mod)
        self.is_integer = True
'''


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess with AST extraction helpers."""
    return subprocess.run(
        ["python3", "-c", _SUBPROCESS_HELPER + code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

def test_mps_syntax():
    """mps.py must parse without syntax errors."""
    src = Path(f"{REPO}/torch/_inductor/codegen/mps.py").read_text()
    ast.parse(src)


def test_utils_h_balanced_braces():
    """c10/metal/utils.h must have balanced braces."""
    content = Path(f"{REPO}/c10/metal/utils.h").read_text()
    assert content.count("{") == content.count("}"), "Unbalanced braces in utils.h"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-executed behavioral tests
# ---------------------------------------------------------------------------

def test_buggy_pattern_not_bare_modulo():
    """_print_ModularIndexing with div=65536 + non-power-of-2 mod must NOT
    return bare (x/div) % (mod) — the Metal compiler bug workaround must activate."""
    r = _run_py(r"""
method = _extract_method("/workspace/pytorch/torch/_inductor/codegen/mps.py", "_print_ModularIndexing")
assert method is not None, "_print_ModularIndexing not found"
printer = _FakePrinter()

buggy_cases = [(65536, 6), (65536, 3), (65536, 5)]
for div_val, mod_val in buggy_cases:
    expr = _FakeExpr(sympy.Symbol("idx"), sympy.Integer(div_val), sympy.Integer(mod_val))
    result = str(method(printer, expr))
    # On base commit this returns "((idx) / (65536)) % (6)" — fix must differ
    clean = result.replace(" ", "")
    bare_pattern = f"((idx)/({div_val}))%({mod_val})"
    assert clean != bare_pattern, f"Still bare modulo for div={div_val}, mod={mod_val}: {result}"
    # Output must reference both the base variable and the mod value
    assert "idx" in result, f"Missing base variable: {result}"
    assert str(mod_val) in result, f"Missing mod value {mod_val}: {result}"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_buggy_pattern_uses_function_call():
    """Buggy-pattern output must call a function (any name) rather than
    using bare % operator that triggers the Metal compiler bug."""
    r = _run_py(r"""
import re as _re
method = _extract_method("/workspace/pytorch/torch/_inductor/codegen/mps.py", "_print_ModularIndexing")
assert method is not None, "_print_ModularIndexing not found"
printer = _FakePrinter()

buggy_cases = [(65536, 6), (65536, 3), (65536, 5)]
for div_val, mod_val in buggy_cases:
    expr = _FakeExpr(sympy.Symbol("idx"), sympy.Integer(div_val), sympy.Integer(mod_val))
    result = str(method(printer, expr))
    has_func_call = bool(_re.search(r"[a-zA-Z_][\w:]*\s*\([^)]*\)", result))
    clean = result.replace(" ", "")
    uses_bare_pct = bool(_re.search(r"\)%\(", clean))
    assert not (uses_bare_pct and not has_func_call), \
        f"Bare % without function call for div={div_val}, mod={mod_val}: {result}"
    assert has_func_call, f"No function call in output for div={div_val}, mod={mod_val}: {result}"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_utils_h_new_mod_safety_function():
    """utils.h must have a new function providing safe modulo with
    an optimization barrier (volatile, optnone, asm, etc.)."""
    r = _run_py(r"""
import re
from pathlib import Path
content = Path("/workspace/pytorch/c10/metal/utils.h").read_text()

# A safe-modulo function was added (common naming patterns)
func_match = re.search(r'\b(safe_mod|mod_safe|safe_modulo|safe_remainder)\b', content)
assert func_match, "No safe_mod (or similar) function found in utils.h"

# The function has an optimization barrier — search nearby
start = max(0, func_match.start() - 300)
end = min(len(content), func_match.end() + 300)
region = content[start:end]
has_barrier = any(
    kw in region for kw in ("volatile", "optnone", "__attribute__", "asm(", "noinline")
)
assert has_barrier, \
    "Safe modulo function missing optimization barrier (volatile/optnone/etc.) near definition"
assert "%" in region or "remainder" in region.lower(), \
    "Safe modulo function doesn't appear to perform modulo operation"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_non_buggy_patterns_preserved():
    """Non-buggy patterns (div=1, power-of-2 mod) and FloorDiv still produce valid output."""
    method = _extract_method(f"{REPO}/torch/_inductor/codegen/mps.py", "_print_ModularIndexing")
    assert method is not None, "_print_ModularIndexing not found"
    printer = _FakePrinter()

    cases = [
        (1, 8, "div=1, mod=8"),
        (65536, 8, "div=65536, mod=8 (power-of-2 mod)"),
        (256, 16, "div=256, mod=16"),
        (1, 32, "div=1, mod=32"),
    ]
    for div_val, mod_val, desc in cases:
        expr = _FakeExpr(sympy.Symbol("idx"), sympy.Integer(div_val), sympy.Integer(mod_val))
        result = str(method(printer, expr))
        assert len(result.strip()) >= 3, f"Trivial output for {desc}: {result}"
        assert str(mod_val) in result, f"Output missing mod value for {desc}: {result}"
        if div_val != 1:
            assert (
                str(div_val) in result or "/" in result or ">>" in result
            ), f"Output drops division for {desc}: {result}"

    # FloorDiv must also still work
    fd_method = _extract_method(f"{REPO}/torch/_inductor/codegen/mps.py", "_print_FloorDiv")
    assert fd_method is not None, "_print_FloorDiv missing"
    fd_expr = _FakeFloorDivExpr(sympy.Symbol("idx"), sympy.Integer(4))
    fd_result = str(fd_method(printer, fd_expr))
    assert "idx" in fd_result, f"FloorDiv output missing base var: {fd_result}"
    assert "floor_divide" in fd_result or "/" in fd_result, f"FloorDiv invalid: {fd_result}"


def test_existing_functions_preserved():
    """floor_divide and fmod still present in utils.h; files not gutted."""
    content = Path(f"{REPO}/c10/metal/utils.h").read_text()
    for fn in ("floor_divide", "fmod"):
        assert re.search(rf"\b{fn}\s*\(", content), f"{fn} function missing from utils.h"

    mps_lines = Path(f"{REPO}/torch/_inductor/codegen/mps.py").read_text().count("\n")
    utils_lines = content.count("\n")
    assert mps_lines >= 100, f"mps.py only {mps_lines} lines — appears gutted"
    assert utils_lines >= 50, f"utils.h only {utils_lines} lines — appears gutted"
