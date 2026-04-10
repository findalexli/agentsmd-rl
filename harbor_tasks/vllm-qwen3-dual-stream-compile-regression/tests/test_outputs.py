"""
Task: vllm-qwen3-dual-stream-compile-regression
Repo: vllm-project/vllm
PR:   #38152
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"
QWEN3_NEXT = f"{REPO}/vllm/model_executor/models/qwen3_next.py"
QWEN3_5 = f"{REPO}/vllm/model_executor/models/qwen3_5.py"

def _parse_file(filepath):
    source = Path(filepath).read_text()
    return source, ast.parse(source)

def _get_class_method(tree, class_substr, method_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and class_substr in node.name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return item
    raise AssertionError(f"Could not find {class_substr}.{method_name}")

def _calls_in_method(tree, class_substr, method_name):
    method = _get_class_method(tree, class_substr, method_name)
    names = []
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            func = node.func
            parts = []
            while isinstance(func, ast.Attribute):
                parts.append(func.attr)
                func = func.value
            if isinstance(func, ast.Name):
                parts.append(func.id)
            parts.reverse()
            names.append(".".join(parts))
    return names

# Pass-to-pass tests
def test_syntax_check():
    for path in (QWEN3_NEXT, QWEN3_5):
        source = Path(path).read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {path}: {e}") from e

def test_repo_ruff_check():
    """Repo's ruff lint check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Ruff check failed: {r.stdout}{r.stderr}"

def test_repo_ruff_format():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Ruff format check failed: {r.stdout}{r.stderr}"

def test_repo_spdx_headers():
    """Modified files have valid SPDX headers (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_spdx_header.py", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"SPDX header check failed: {r.stdout}{r.stderr}"

def test_repo_forbidden_imports():
    """Modified files have no forbidden imports (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_forbidden_imports.py", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Forbidden imports check failed: {r.stdout}{r.stderr}"

def test_repo_boolean_context_manager():
    """Modified files have no boolean ops in with-statements (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_boolean_context_manager.py", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Boolean context manager check failed: {r.stdout}{r.stderr}"

def test_repo_torch_cuda_check():
    """Modified files have no improper torch.cuda API calls (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_torch_cuda.py", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Torch CUDA check failed: {r.stdout}{r.stderr}"



def test_repo_check_init_lazy_imports():
    """Modified files have valid lazy imports (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/check_init_lazy_imports.py", QWEN3_NEXT, QWEN3_5],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Init lazy imports check failed: {r.stdout}{r.stderr}"

def test_repo_attention_backend_docs():
    """Attention backend documentation is up to date (pass_to_pass)."""
    r = subprocess.run(
        ["python", f"{REPO}/tools/pre_commit/generate_attention_backend_docs.py", "--check"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Attention backend docs check failed: {r.stdout}{r.stderr}"

# Fail-to-pass tests
def test_qwen3next_forward_no_custom_op():
    _, tree = _parse_file(QWEN3_NEXT)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    gdn_calls = [c for c in calls if "gdn_in_proj" in c]
    assert not gdn_calls, f"forward still routes through gdn_in_proj: {gdn_calls}"

def test_qwen35_forward_no_custom_op():
    _, tree = _parse_file(QWEN3_5)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    gdn_calls = [c for c in calls if "gdn_in_proj" in c]
    assert not gdn_calls, f"forward still routes through gdn_in_proj: {gdn_calls}"

def test_gdn_in_proj_not_registered():
    _, tree = _parse_file(QWEN3_NEXT)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            for kw in call.keywords:
                if kw.arg == "op_name" and isinstance(kw.value, ast.Constant) and kw.value.value == "gdn_in_proj":
                    raise AssertionError("gdn_in_proj is still registered")
            if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "gdn_in_proj":
                raise AssertionError("gdn_in_proj is still registered")

def test_no_dual_stream_infra():
    _, tree = _parse_file(QWEN3_NEXT)
    init = _get_class_method(tree, "GatedDeltaNet", "__init__")
    found = []
    for node in ast.walk(init):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr in ("aux_stream", "events"):
                    found.append(t.attr)
    assert not found, f"__init__ still sets up dual-stream infra: {found}"

def test_dead_code_removed():
    _, tree = _parse_file(QWEN3_NEXT)
    dead_module = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("gdn_in_proj", "gdn_in_proj_fake"):
            dead_module.append(node.name)
    dead_class = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "GatedDeltaNet" in node.name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "_forward_in_proj":
                    dead_class.append("_forward_in_proj")
    dead = dead_module + dead_class
    assert not dead, f"Dead code still present: {dead}"

def test_unused_imports_removed():
    _, tree = _parse_file(QWEN3_NEXT)
    dead_imports = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in ("maybe_execute_in_parallel", "aux_stream"):
                    dead_imports.append(alias.name)
    assert not dead_imports, f"Unused dual-stream imports: {dead_imports}"

def test_qwen3next_direct_projection():
    _, tree = _parse_file(QWEN3_NEXT)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    called_attrs = set(c.split(".")[-1] for c in calls if "." in c)
    missing = {"in_proj_qkvz", "in_proj_ba"} - called_attrs
    assert not missing, f"Missing direct calls: {missing}"

def test_qwen35_direct_projection():
    _, tree = _parse_file(QWEN3_5)
    calls = _calls_in_method(tree, "GatedDeltaNet", "forward")
    called_attrs = set(c.split(".")[-1] for c in calls if "." in c)
    missing = {"in_proj_qkvz", "in_proj_ba"} - called_attrs
    assert not missing, f"Missing direct calls: {missing}"

def test_attention_core_op_preserved():
    _, tree = _parse_file(QWEN3_NEXT)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            for kw in call.keywords:
                if kw.arg == "op_name" and isinstance(kw.value, ast.Constant) and kw.value.value == "gdn_attention_core":
                    return
            if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == "gdn_attention_core":
                return
    raise AssertionError("gdn_attention_core registration missing")

def test_forward_not_stub():
    for filepath in (QWEN3_NEXT, QWEN3_5):
        _, tree = _parse_file(filepath)
        method = _get_class_method(tree, "GatedDeltaNet", "forward")
        stmts = [s for s in ast.walk(method) if isinstance(s, ast.Assign)]
        assert len(stmts) >= 3, f"forward appears stubby ({len(stmts)} assignments)"
