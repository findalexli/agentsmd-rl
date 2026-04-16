"""
Task: pytorch-mps-modular-indexing-safe-mod
Repo: pytorch/pytorch @ 483b55d84c74b92b3c2c67be4b9b7c7359ec2bbc
PR:   178009

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
import re
import subprocess
import textwrap
from pathlib import Path
import sympy

REPO = "/workspace/pytorch"


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
    def doprint(self, x): return str(x)
    def _print(self, x): return str(x)
    def parenthesize(self, x, *a, **kw): return str(x)


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


_SUBPROCESS_HELPER = """
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
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess with AST extraction helpers."""
    return subprocess.run(
        ["python3", "-c", _SUBPROCESS_HELPER + code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO
    )


def test_mps_syntax():
    """mps.py must parse without syntax errors."""
    src = Path(f"{REPO}/torch/_inductor/codegen/mps.py").read_text()
    ast.parse(src)


def test_mps_py_compile():
    """mps.py must compile to bytecode without errors (pass_to_pass)."""
    py_compile.compile(f"{REPO}/torch/_inductor/codegen/mps.py", doraise=True)


def test_utils_h_balanced_braces():
    """c10/metal/utils.h must have balanced braces."""
    content = Path(f"{REPO}/c10/metal/utils.h").read_text()
    assert content.count('{') == content.count('}'), "Unbalanced braces in utils.h"


def test_utils_h_syntax():
    """c10/metal/utils.h must be valid C++ header (basic structural checks)."""
    content = Path(f"{REPO}/c10/metal/utils.h").read_text()
    assert "#pragma once" in content or ("#ifndef" in content and "#define" in content), \
        "Missing header guard or #pragma once"
    assert content.count('{') == content.count('}'), "Unbalanced braces in utils.h"
    assert "namespace" in content, "Missing namespace declaration"


def test_codegen_mps_imports():
    """mps.py must have valid import statements (pass_to_pass)."""
    src = Path(f"{REPO}/torch/_inductor/codegen/mps.py").read_text()
    tree = ast.parse(src)
    imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert len(imports) > 0, "No imports found in mps.py"


def test_mps_ast_valid():
    """mps.py has valid AST structure with required classes and methods (pass_to_pass)."""
    r = subprocess.run(
        ("python3", "-c", """
import ast
from pathlib import Path

src = Path('/workspace/pytorch/torch/_inductor/codegen/mps.py').read_text()
tree = ast.parse(src)

# Find MetalExprPrinter class
found_class = False
required_methods = {'_print_ModularIndexing', '_print_FloorDiv', '_print_Min', '_print_Max'}
found_methods = set()

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'MetalExprPrinter':
        found_class = True
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name in required_methods:
                found_methods.add(item.name)

assert found_class, 'MetalExprPrinter class not found'
missing = required_methods - found_methods
assert not missing, f'Missing required methods: {missing}'
print('AST check passed')
"""),
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"AST validation failed:\n{r.stderr}"
    assert "AST check passed" in r.stdout


def test_utils_h_key_functions_exist():
    """utils.h contains required Metal utility functions (pass_to_pass)."""
    r = subprocess.run(
        ("python3", "-c", """
import re
from pathlib import Path

content = Path('/workspace/pytorch/c10/metal/utils.h').read_text()

# Check for required functions
required_funcs = ['floor_divide', 'fmod']
for func in required_funcs:
    pattern = rf'\\b{func}\\s*\\('
    assert re.search(pattern, content), f'{func} function not found in utils.h'

# Check for namespace structure
assert 'namespace c10' in content, 'Missing c10 namespace'
assert 'namespace metal' in content, 'Missing metal namespace'

print('utils.h functions check passed')
"""),
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"utils.h validation failed:\n{r.stderr}"
    assert "utils.h functions check passed" in r.stdout


def test_modular_indexing_method_signature():
    """_print_ModularIndexing has correct method signature (pass_to_pass)."""
    r = subprocess.run(
        ("python3", "-c", """
import ast
from pathlib import Path

src = Path('/workspace/pytorch/torch/_inductor/codegen/mps.py').read_text()
tree = ast.parse(src)

# Find _print_ModularIndexing method
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_print_ModularIndexing':
        found = True
        # Check it has 'self' and 'expr' parameters
        args = [arg.arg for arg in node.args.args]
        assert 'self' in args, 'Missing self parameter'
        assert 'expr' in args, 'Missing expr parameter'
        # Check for expr.args unpacking (x, div, mod)
        source = ast.unparse(node)
        assert 'x, div, mod' in source or 'expr.args' in source, 'Missing expr.args unpacking'
        break

assert found, '_print_ModularIndexing method not found'
print('Method signature check passed')
"""),
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Method signature check failed:\n{r.stderr}"
    assert "Method signature check passed" in r.stdout


def test_mps_modular_indexing_behavior():
    """_print_ModularIndexing produces valid output for standard cases (pass_to_pass)."""
    r = subprocess.run(
        ("python3", "-c", """
import ast
import textwrap
import sympy
from pathlib import Path

def _extract_method(filepath, method_name):
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = textwrap.dedent(''.join(lines[node.lineno - 1 : node.end_lineno]))
            ns = {'__builtins__': __builtins__, 'sympy': sympy}
            for attr in dir(sympy):
                if not attr.startswith('_'):
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

method = _extract_method('/workspace/pytorch/torch/_inductor/codegen/mps.py', '_print_ModularIndexing')
assert method is not None, '_print_ModularIndexing not found'

printer = _FakePrinter()

# Test non-buggy cases (should work on base commit)
test_cases = [
    (1, 8, 'div=1, mod=8'),
    (256, 16, 'div=256, mod=16'),
    (1, 32, 'div=1, mod=32'),
]

for div_val, mod_val, desc in test_cases:
    expr = _FakeExpr(sympy.Integer(100), sympy.Integer(div_val), sympy.Integer(mod_val))
    result = str(method(printer, expr))
    assert len(result.strip()) >= 3, f'Trivial output for {desc}: {result}'
    assert str(mod_val) in result, f'Output missing mod value for {desc}: {result}'
    print(f'Case {desc}: {result}')

print('All behavior checks passed')
"""),
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"Behavior test failed:\n{r.stderr}"
    assert "All behavior checks passed" in r.stdout


def test_floordiv_method_exists():
    """_print_FloorDiv method exists and has correct signature (pass_to_pass)."""
    r = subprocess.run(
        ("python3", "-c", """
import ast
from pathlib import Path

src = Path('/workspace/pytorch/torch/_inductor/codegen/mps.py').read_text()
tree = ast.parse(src)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_print_FloorDiv':
        found = True
        args = [arg.arg for arg in node.args.args]
        assert 'self' in args, 'Missing self parameter'
        assert 'expr' in args, 'Missing expr parameter'
        break

assert found, '_print_FloorDiv method not found'
print('FloorDiv method check passed')
"""),
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    assert r.returncode == 0, f"FloorDiv check failed:\n{r.stderr}"
    assert "FloorDiv method check passed" in r.stdout


def test_buggy_pattern_not_bare_modulo():
    """_print_ModularIndexing with div=65536 + non-power-of-2 mod must NOT
    return bare (x/div) % (mod) — the Metal compiler bug workaround must activate."""
    r = _run_py("""
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
    r = _run_py("""
import re as _re
method = _extract_method("/workspace/pytorch/torch/_inductor/codegen/mps.py", "_print_ModularIndexing")
assert method is not None, "_print_ModularIndexing not found"
printer = _FakePrinter()

buggy_cases = [(65536, 6), (65536, 3), (65536, 5)]
for div_val, mod_val in buggy_cases:
    expr = _FakeExpr(sympy.Symbol("idx"), sympy.Integer(div_val), sympy.Integer(mod_val))
    result = str(method(printer, expr))
    has_func_call = bool(_re.search(r"[a-zA-Z_][\\w:]*\\s*\\([^)]*\\)", result))
    clean = result.replace(" ", "")
    uses_bare_pct = bool(_re.search(r"\\)%\\(", clean))
    assert not (uses_bare_pct and not has_func_call), \
        f"Bare % without function call for div={div_val}, mod={mod_val}: {result}"
    assert has_func_call, f"No function call in output for div={div_val}, mod={mod_val}: {result}"

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_utils_h_new_mod_safety_function():
    """The codegen's buggy-pattern workaround must call a function defined in utils.h."""
    r = _run_py("""
import re as _re
from pathlib import Path

# Get codegen output for a buggy case (div=65536, non-power-of-2 mod)
method = _extract_method("/workspace/pytorch/torch/_inductor/codegen/mps.py", "_print_ModularIndexing")
assert method is not None, "_print_ModularIndexing not found"
printer = _FakePrinter()
expr = _FakeExpr(sympy.Symbol("idx"), sympy.Integer(65536), sympy.Integer(6))
result = str(method(printer, expr))

# Extract function-call identifiers (possibly namespace-qualified) from the output
func_calls = _re.findall(r'([a-zA-Z_][\\w:]*)\\s*\\(', result)
assert func_calls, f"No function calls in codegen output for buggy case: {result}"

# Verify at least one called function is defined in utils.h
content = Path("/workspace/pytorch/c10/metal/utils.h").read_text()
found = False
for qualified_name in func_calls:
    func_name = qualified_name.split("::")[-1]
    if _re.search(r'\\b' + _re.escape(func_name) + r'\\s*\\(', content):
        found = True
        break

assert found, (
    f"Codegen output calls {func_calls} for buggy pattern, "
    f"but none are defined in utils.h"
)

print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


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
        expr = _FakeExpr(sympy.Integer(100), sympy.Integer(div_val), sympy.Integer(mod_val))
        result = str(method(printer, expr))
        assert len(result.strip()) >= 3, f"Trivial output for {desc}: {result}"
        assert str(mod_val) in result, f"Output missing mod value for {desc}: {result}"
        if div_val > 1:
            assert str(div_val) in result or "/" in result or ">>" in result, \
                f"Output drops division for {desc}: {result}"

    # FloorDiv check
    fd_method = _extract_method(f"{REPO}/torch/_inductor/codegen/mps.py", "_print_FloorDiv")
    assert fd_method is not None, "_print_FloorDiv missing"
    fd_expr = _FakeFloorDivExpr(sympy.Integer(100), sympy.Integer(4))
    fd_result = str(fd_method(printer, fd_expr))
    assert "100" in fd_result, f"FloorDiv invalid: {fd_result}"
    assert "floor" in fd_result.lower(), f"FloorDiv invalid: {fd_result}"


def test_existing_functions_preserved():
    """floor_divide and fmod still present in utils.h; files not gutted."""
    content = Path(f"{REPO}/c10/metal/utils.h").read_text()
    for fn in ('floor_divide', 'fmod'):
        assert re.search(rf'\b{fn}\s*\(', content), f"{fn} function missing from utils.h"

    mps_lines = Path(f"{REPO}/torch/_inductor/codegen/mps.py").read_text().count('\n')
    assert mps_lines >= 100, f"mps.py only {mps_lines} lines — appears gutted"

    utils_lines = content.count('\n')
    assert utils_lines >= 50, f"utils.h only {utils_lines} lines — appears gutted"
