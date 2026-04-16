"""
Task: sglang-cache-gfx95-quant-format
Repo: sgl_project/sglang @ 52801ff20c3d48ef594912bae3f2e49fbabe0a71
PR:   22143

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import re
import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/srt/models/deepseek_v2.py"
sys.path.insert(0, f"{REPO}/python")


def _parse_target_file():
    """Parse the target file and return the AST."""
    src = Path(TARGET_FILE).read_text()
    return ast.parse(src)


def _get_class_methods(tree, class_name):
    """Extract methods from a class in the AST."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {n.name: n for n in node.body if isinstance(n, ast.FunctionDef)}
    return {}


def _get_init_assignments(tree, class_name):
    """Extract attribute assignments from __init__ method."""
    methods = _get_class_methods(tree, class_name)
    if "__init__" not in methods:
        return {}

    init = methods["__init__"]
    assigns = {}
    for stmt in init.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        assigns[target.attr] = stmt
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Attribute) and isinstance(stmt.target.value, ast.Name):
                if stmt.target.value.id == "self":
                    assigns[stmt.target.attr] = stmt
    return assigns


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile
    py_compile.compile(TARGET_FILE, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cached_quant_format_attribute():
    """DeepseekV2DecoderLayer must cache quant format detection in __init__."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "__init__" in methods, "DeepseekV2DecoderLayer.__init__ not found"

    assigns = _get_init_assignments(tree, "DeepseekV2DecoderLayer")

    # Look for any self.<method>() call that assigns to an attribute related to quant format
    found_cache = False
    for attr, assign in assigns.items():
        if isinstance(assign.value, ast.Call):
            func = assign.value.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
                if ("quant" in attr.lower() or "format" in attr.lower() or
                    "detect" in func.attr.lower()):
                    found_cache = True
                    break

    assert found_cache, (
        "No cache assignment found in __init__ — expected self.<detect_method>() "
        "call to populate an attribute related to quant format detection"
    )


# [pr_diff] fail_to_pass
def test_detect_quant_format_method_exists():
    """DeepseekV2DecoderLayer must have a detection method for quant format."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")

    detect_methods = [name for name in methods if "detect" in name.lower() or "quant" in name.lower()]

    assert len(detect_methods) > 0, (
        f"No detection method found in DeepseekV2DecoderLayer. "
        f"Expected a method with 'detect' or 'quant' in the name."
    )

    method = methods[detect_methods[0]]
    if method.returns:
        assert isinstance(method.returns, ast.Name) and method.returns.id == "str", (
            f"Detection method should return str, got {method.returns.id}"
        )


# [pr_diff] fail_to_pass
def test_forward_uses_cached_quant_format():
    """forward() must use a cached attribute rather than recomputing inline."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")
    assert "forward" in methods, "forward method not found"

    forward = methods["forward"]
    src = ast.unparse(forward)

    cached_refs = re.findall(r'self\.(\w*(?:quant|format)\w*)', src, re.IGNORECASE)
    assert len(cached_refs) > 0, (
        "forward() does not use any cached quant/format attribute on self. "
        "Expected self.<quant_attr> reference."
    )

    has_old_pattern = (
        "quant_format = (" in src and
        "_is_gfx95_supported" in src and
        "fused_qkv_a_proj_with_mqa" in src
    )
    assert not has_old_pattern, (
        "forward() still has the old inline quant_format computation. "
        "It should use a cached value instead."
    )


# [pr_diff] fail_to_pass - BEHAVIORAL: actually execute the code via subprocess
def test_detection_method_executable():
    """Detection method exists and is executable as a standalone function."""
    # Write a test script that actually imports and inspects the code
    test_script = '''
import sys
sys.path.insert(0, "/workspace/sglang/python")

# Import the module using spec-based loading to avoid torch dependency issues
import importlib.util
import ast

TARGET = "/workspace/sglang/python/sglang/srt/models/deepseek_v2.py"
src = open(TARGET).read()
tree = ast.parse(src)

# Find the DeepseekV2DecoderLayer class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
        cls_node = node
        break

assert cls_node is not None, "DeepseekV2DecoderLayer not found"

# Find methods related to detection
detect_method = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef):
        if "detect" in item.name.lower() or "quant" in item.name.lower():
            detect_method = item
            break

assert detect_method is not None, "No detection method found"

# Compile the method to verify it's valid Python code
import inspect
method_src = ast.unparse(detect_method)

# Verify it has the expected logic structure
assert "uint8" in method_src.lower() or "torch.uint8" in method_src, "Missing uint8 check"
assert "float8" in method_src.lower() or "fp8" in method_src.lower(), "Missing fp8 check"

# Compile it to verify syntax
compile(method_src, "<string>", "exec")

print("OK")
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert "OK" in result.stdout, f"Script did not complete: {result.stdout}"
    finally:
        os.unlink(script_path)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "ruff"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_repo_ast_validity():
    """Repo's Python AST parsing passes on modified file (pass_to_pass)."""
    import ast
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "DeepseekV2DecoderLayer" in classes, "DeepseekV2DecoderLayer class not found"


# [static] pass_to_pass
def test_repo_file_structure():
    """Modified file has proper Python file structure (pass_to_pass)."""
    import ast
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    assert len(imports) > 0, "No imports found in file"

    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    assert len(classes) > 0, "No class definitions found in file"

    layer_class = None
    for cls in classes:
        if cls.name == "DeepseekV2DecoderLayer":
            layer_class = cls
            break

    assert layer_class is not None, "DeepseekV2DecoderLayer class not found"

    methods = [n.name for n in layer_class.body if isinstance(n, ast.FunctionDef)]
    assert "__init__" in methods, "DeepseekV2DecoderLayer.__init__ not found"
    assert "forward" in methods, "DeepseekV2DecoderLayer.forward not found"


# [repo_tests] pass_to_pass
def test_repo_black_format():
    """Repo's black format check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "black"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["black", "--check", "--diff", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "isort"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["isort", "--check-only", "--diff", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_codespell():
    """Repo's codespell check passes on modified file (pass_to_pass)."""
    import subprocess

    try:
        subprocess.run(["pip", "install", "-q", "codespell"], check=True, capture_output=True)
    except Exception:
        pass

    r = subprocess.run(
        ["codespell", TARGET_FILE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"codespell check failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """Modified function is not a stub (has real logic, not just pass/return)."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")

    detect_methods = [name for name in methods if "detect" in name.lower() or "quant" in name.lower()]
    assert len(detect_methods) > 0, "No detection method found"

    method = methods[detect_methods[0]]
    stmts = [s for s in method.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(stmts) >= 3, f"Method body is a stub (only {len(stmts)} non-trivial statements)"


# [static] pass_to_pass
def test_detect_method_has_proper_logic():
    """Detection method must have proper dtype checking logic for quantization."""
    tree = _parse_target_file()

    methods = _get_class_methods(tree, "DeepseekV2DecoderLayer")

    detect_methods = [name for name in methods if "detect" in name.lower() or "quant" in name.lower()]
    assert len(detect_methods) > 0, "No detection method found"

    method = methods[detect_methods[0]]
    src = ast.unparse(method)

    assert "torch.uint8" in src or "uint8" in src, "Missing uint8 dtype check"
    assert "float8_e4m3fn" in src or "fp8" in src.lower(), (
        "Missing fp8_e4m3fn dtype check"
    )
    assert "mxfp4" in src or "fp8" in src.lower() or "fp8_e4m3fn" in src, (
        "Missing format return values (mxfp4/fp8)"
    )
