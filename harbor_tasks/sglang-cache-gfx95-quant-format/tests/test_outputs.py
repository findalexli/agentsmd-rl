"""
Task: sglang-cache-gfx95-quant-format
Repo: sgl_project/sglang @ 52801ff20c3d48ef594912bae3f2e49fbabe0a71
PR:   22143

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/sglang"
TARGET_FILE = f"{REPO}/python/sglang/srt/models/deepseek_v2.py"
sys.path.insert(0, f"{REPO}/python")


def _run_script(script_content):
    """Write a Python script to a temp file and execute it via subprocess."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script_content)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=60
        )
        return result
    finally:
        os.unlink(path)


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
    """Execute the quant format detection logic and verify correct dtype-to-format mapping."""
    script = r"""
import torch
import ast
import types
import copy

TARGET = "/workspace/sglang/python/sglang/srt/models/deepseek_v2.py"
src = open(TARGET).read()
tree = ast.parse(src)

# Find DeepseekV2DecoderLayer class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
        cls_node = node
        break
assert cls_node is not None, "DeepseekV2DecoderLayer not found"

# Collect all methods
methods = {}
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef):
        methods[item.name] = item

# Find detection method: any method (not __init__/forward/_is_layer_sparse/op_*)
# that contains dtype checking logic (references uint8 AND float8/fp8)
detect_name = None
detect_node = None
for name, node in methods.items():
    if name in ("__init__", "forward", "_is_layer_sparse") or name.startswith("op_"):
        continue
    node_src = ast.unparse(node)
    if "uint8" in node_src and ("float8" in node_src or "fp8" in node_src.lower()):
        detect_name = name
        detect_node = node
        break

if detect_node is not None:
    # Strip decorators so we can call the method directly
    node_copy = copy.deepcopy(detect_node)
    node_copy.decorator_list = []
    method_src = ast.unparse(node_copy)

    # Build a minimal test class containing this method
    lines = method_src.split("\n")
    class_body = "\n".join("    " + l for l in lines)
    class_code = "class _TestDetector:\n" + class_body + "\n"

    exec_ns = {"torch": torch, "_is_gfx95_supported": True}
    exec(class_code, exec_ns)
    Cls = exec_ns["_TestDetector"]

    # Test uint8 weight -> "mxfp4"
    obj = Cls()
    obj.self_attn = types.SimpleNamespace(
        fused_qkv_a_proj_with_mqa=types.SimpleNamespace(
            weight=types.SimpleNamespace(dtype=torch.uint8)))
    result = getattr(obj, detect_name)()
    assert result == "mxfp4", f"uint8 weight should yield 'mxfp4', got {result!r}"

    # Test float8_e4m3fn weight -> "fp8"
    if hasattr(torch, "float8_e4m3fn"):
        obj2 = Cls()
        obj2.self_attn = types.SimpleNamespace(
            fused_qkv_a_proj_with_mqa=types.SimpleNamespace(
                weight=types.SimpleNamespace(dtype=torch.float8_e4m3fn)))
        result2 = getattr(obj2, detect_name)()
        assert result2 == "fp8", f"float8_e4m3fn weight should yield 'fp8', got {result2!r}"

    # Test other dtype -> ""
    obj3 = Cls()
    obj3.self_attn = types.SimpleNamespace(
        fused_qkv_a_proj_with_mqa=types.SimpleNamespace(
            weight=types.SimpleNamespace(dtype=torch.float32)))
    result3 = getattr(obj3, detect_name)()
    assert result3 == "", f"float32 weight should yield '', got {result3!r}"

    # Test None weight -> ""
    obj4 = Cls()
    obj4.self_attn = types.SimpleNamespace(
        fused_qkv_a_proj_with_mqa=types.SimpleNamespace(weight=None))
    result4 = getattr(obj4, detect_name)()
    assert result4 == "", f"None weight should yield '', got {result4!r}"

    print("OK")
else:
    # No separate detection method; verify detection is inline in __init__ (not forward)
    forward = methods.get("forward")
    assert forward is not None
    forward_src = ast.unparse(forward)
    has_old_pattern = (
        "uint8" in forward_src
        and "mxfp4" in forward_src
        and "fused_qkv_a_proj_with_mqa" in forward_src
    )
    assert not has_old_pattern, "forward() still has inline quant format computation"

    init = methods.get("__init__")
    assert init is not None
    init_src = ast.unparse(init)
    assert "uint8" in init_src and "mxfp4" in init_src, (
        "No detection logic found (neither separate method nor inline in __init__)"
    )
    print("OK")
"""
    result = _run_script(script)
    assert result.returncode == 0, f"Detection correctness test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_detect_quant_format_method_exists():
    """forward() must not recompute quant format inline; detection must live outside forward."""
    script = r"""
import ast

TARGET = "/workspace/sglang/python/sglang/srt/models/deepseek_v2.py"
src = open(TARGET).read()
tree = ast.parse(src)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
        cls_node = node
        break
assert cls_node is not None

methods = {}
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef):
        methods[item.name] = item

# forward() must NOT contain the inline quant_format computation
forward = methods.get("forward")
assert forward is not None, "forward method not found"
forward_src = ast.unparse(forward)

has_inline = (
    "uint8" in forward_src
    and "fused_qkv_a_proj_with_mqa" in forward_src
)
assert not has_inline, (
    "forward() still has inline quant format computation with dtype checks. "
    "The format should be pre-computed during initialization."
)

# Detection logic must exist OUTSIDE forward (in another method or __init__)
non_forward = ""
for name, node in methods.items():
    if name != "forward" and not name.startswith("op_"):
        non_forward += ast.unparse(node) + "\n"

has_detection = "uint8" in non_forward or "mxfp4" in non_forward
assert has_detection, (
    "No quant format detection logic found outside forward(). "
    "Detection must happen during initialization."
)

print("OK")
"""
    result = _run_script(script)
    assert result.returncode == 0, f"Detection separation test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_forward_uses_cached_quant_format():
    """forward() must pass a pre-cached self.* attribute to prepare_attn."""
    script = r"""
import ast

TARGET = "/workspace/sglang/python/sglang/srt/models/deepseek_v2.py"
src = open(TARGET).read()
tree = ast.parse(src)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
        cls_node = node
        break
assert cls_node is not None

forward = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "forward":
        forward = item
        break
assert forward is not None, "forward method not found"

forward_src = ast.unparse(forward)

# The old inline pattern must be gone
has_old = (
    ("quant_format" in forward_src and "dtype" in forward_src)
    or ("uint8" in forward_src and "fused_qkv_a_proj_with_mqa" in forward_src)
)
assert not has_old, "forward() still has inline quant_format computation"

# prepare_attn must be called with a self.* attribute (the cached value)
found_cached = False
for node in ast.walk(forward):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "prepare_attn":
            for arg in node.args:
                if (isinstance(arg, ast.Attribute)
                        and isinstance(arg.value, ast.Name)
                        and arg.value.id == "self"):
                    found_cached = True
                    break
            if found_cached:
                break

assert found_cached, (
    "forward() does not pass a cached self.* attribute to prepare_attn. "
    "The quant format should be stored as an instance attribute."
)

print("OK")
"""
    result = _run_script(script)
    assert result.returncode == 0, f"Forward caching test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# [pr_diff] fail_to_pass
def test_detection_method_executable():
    """Detection handles edge cases and is cached during __init__."""
    script = r"""
import torch
import ast
import types
import copy

TARGET = "/workspace/sglang/python/sglang/srt/models/deepseek_v2.py"
src = open(TARGET).read()
tree = ast.parse(src)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
        cls_node = node
        break
assert cls_node is not None

methods = {}
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef):
        methods[item.name] = item

# Find detection method (any non-init/forward/op_* method with dtype logic)
detect_name = None
detect_node = None
for name, node in methods.items():
    if name in ("__init__", "forward", "_is_layer_sparse") or name.startswith("op_"):
        continue
    node_src = ast.unparse(node)
    if "uint8" in node_src and ("float8" in node_src or "fp8" in node_src.lower()):
        detect_name = name
        detect_node = node
        break

if detect_node is not None:
    node_copy = copy.deepcopy(detect_node)
    node_copy.decorator_list = []
    method_src = ast.unparse(node_copy)
    lines = method_src.split("\n")
    class_body = "\n".join("    " + l for l in lines)
    class_code = "class _TestDetector:\n" + class_body + "\n"

    # Test: _is_gfx95_supported=False should return ""
    exec_ns = {"torch": torch, "_is_gfx95_supported": False}
    exec(class_code, exec_ns)
    Cls = exec_ns["_TestDetector"]
    obj = Cls()
    obj.self_attn = types.SimpleNamespace(
        fused_qkv_a_proj_with_mqa=types.SimpleNamespace(
            weight=types.SimpleNamespace(dtype=torch.uint8)))
    result = getattr(obj, detect_name)()
    assert result == "", f"With gfx95 unsupported, expected '', got {result!r}"

    # Test: no fused_qkv_a_proj_with_mqa attribute should return ""
    exec_ns2 = {"torch": torch, "_is_gfx95_supported": True}
    exec(class_code, exec_ns2)
    Cls2 = exec_ns2["_TestDetector"]
    obj2 = Cls2()
    obj2.self_attn = types.SimpleNamespace()  # no fused attr
    result2 = getattr(obj2, detect_name)()
    assert result2 == "", f"With no fused attr, expected '', got {result2!r}"

# Verify __init__ caches the format value
init = methods.get("__init__")
assert init is not None
init_src = ast.unparse(init)

if detect_name:
    assert detect_name in init_src, "Detection method not called in __init__"
else:
    assert "uint8" in init_src or "mxfp4" in init_src, (
        "No detection logic caching found in __init__"
    )

# Verify __init__ stores result as a self.* attribute
found_cache = False
for stmt in ast.walk(init):
    if isinstance(stmt, ast.Assign):
        for target in stmt.targets:
            if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"):
                stmt_src = ast.unparse(stmt)
                if detect_name and detect_name in stmt_src:
                    found_cache = True
                    break
                if not detect_name and ("mxfp4" in stmt_src or "uint8" in stmt_src):
                    found_cache = True
                    break
    if found_cache:
        break

assert found_cache, "No self.* attribute in __init__ caching the quant format"

print("OK")
"""
    result = _run_script(script)
    assert result.returncode == 0, f"Detection integration test failed:\n{result.stderr}"
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + structure
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_lint():
    """Repo's ruff lint check passes on modified file (pass_to_pass)."""
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
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "DeepseekV2DecoderLayer" in classes, "DeepseekV2DecoderLayer class not found"


# [static] pass_to_pass
def test_repo_file_structure():
    """Modified file has proper Python file structure (pass_to_pass)."""
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
    """DeepseekV2DecoderLayer has real logic in __init__ and forward (not stubs)."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    cls_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
            cls_node = node
            break
    assert cls_node is not None

    methods = {}
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef):
            methods[item.name] = item

    init = methods.get("__init__")
    assert init is not None, "__init__ not found"
    init_stmts = [s for s in init.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(init_stmts) >= 10, (
        f"__init__ has only {len(init_stmts)} non-trivial statements - likely a stub"
    )

    forward = methods.get("forward")
    assert forward is not None, "forward not found"
    forward_stmts = [s for s in forward.body if not isinstance(s, (ast.Pass, ast.Expr))]
    assert len(forward_stmts) >= 5, (
        f"forward has only {len(forward_stmts)} non-trivial statements - likely a stub"
    )


# [static] pass_to_pass
def test_detect_method_has_proper_logic():
    """Class contains proper dtype-based quant format detection logic."""
    src = Path(TARGET_FILE).read_text()
    tree = ast.parse(src)

    cls_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV2DecoderLayer":
            cls_node = node
            break
    assert cls_node is not None

    # The class must handle all three dtype cases somewhere in its code
    class_src = ast.unparse(cls_node)
    assert "torch.uint8" in class_src or "uint8" in class_src, (
        "Missing uint8 dtype handling in class"
    )
    assert "float8_e4m3fn" in class_src or "fp8" in class_src.lower(), (
        "Missing fp8/float8_e4m3fn dtype handling in class"
    )
    assert "mxfp4" in class_src, "Missing 'mxfp4' format string in class"
