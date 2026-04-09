"""
Task: areal-fsdp-qwenvl-rope-dtype
Repo: inclusionAI/AReaL @ f6556e88582e82b747ab1ac4038af2e106a464ee
PR:   1094

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

FSDPEngine requires torch.distributed / FSDP / multi-GPU, so f2p tests
AST-extract the Qwen-VL branch from _prepare_mb_list and exec it with
lightweight mock objects inside a subprocess for isolation.
"""

import ast
import json
import subprocess
import sys
from pathlib import Path

FILE = "/repo/areal/engine/fsdp_engine.py"

# ---------------------------------------------------------------------------
# Subprocess helpers: mock torch + AST extraction, run in isolated process
# ---------------------------------------------------------------------------

_EVAL_HELPERS = r'''
import ast as _ast
import json as _json
import sys as _sys
import textwrap as _textwrap
import types as _types


class _DType:
    """Mock dtype that supports equality comparison."""
    def __init__(self, n):
        self.n = n
    def __eq__(self, o):
        return isinstance(o, _DType) and self.n == o.n
    def __ne__(self, o):
        return not self.__eq__(o)
    def __hash__(self):
        return hash(self.n)
    def __repr__(self):
        return f"torch.{self.n}"


INT32 = _DType("int32")
LONG = _DType("long")
INT64 = _DType("int64")
FLOAT32 = _DType("float32")
BFLOAT16 = _DType("bfloat16")
FLOAT16 = _DType("float16")


class _MockTensor:
    """Mock tensor with dtype tracking and identity preservation."""
    def __init__(self, dtype=None):
        self.dtype = dtype or FLOAT32
    def to(self, *a, **kw):
        d = a[0] if a else kw.get("dtype", self.dtype)
        return _MockTensor(dtype=d)
    def long(self):
        return _MockTensor(dtype=LONG)
    def int(self):
        return _MockTensor(dtype=INT32)
    def __getattr__(self, name):
        return _MockTensor(dtype=self.dtype)


def _make_torch_ns():
    ns = _types.ModuleType("torch")
    ns.long = LONG
    ns.int64 = INT64
    ns.int32 = INT32
    ns.float32 = FLOAT32
    ns.bfloat16 = BFLOAT16
    ns.float16 = FLOAT16
    ns.Tensor = _MockTensor
    ns.einsum = lambda *a, **kw: a[1] if len(a) > 1 else _MockTensor(LONG)
    ns.cat = lambda lst, **kw: lst[0] if lst else _MockTensor(LONG)
    return ns


def _extract_qwen_vl_branch():
    source = open("/repo/areal/engine/fsdp_engine.py").read()
    tree = _ast.parse(source)
    func_node = None
    for node in _ast.walk(tree):
        if isinstance(node, _ast.FunctionDef) and node.name == "_prepare_mb_list":
            func_node = node
            break
    assert func_node is not None, "_prepare_mb_list not found"
    vl_if = None
    for child in _ast.walk(func_node):
        if isinstance(child, _ast.If):
            test_src = _ast.get_source_segment(source, child.test)
            if test_src and "qwen_vl" in test_src.lower().replace("-", "_").replace(" ", "_"):
                vl_if = child
                break
    assert vl_if is not None, "is_qwen_vl_model branch not found"
    body_start = vl_if.body[0].lineno
    body_end = vl_if.body[-1].end_lineno
    raw_lines = source.splitlines()[body_start - 1:body_end]
    return _textwrap.dedent("\n".join(raw_lines))


def _exec_branch(input_ids_dtype):
    body_src = _extract_qwen_vl_branch()
    torch_ns = _make_torch_ns()
    calls = []

    class MModel:
        @staticmethod
        def get_rope_index(*args, **kwargs):
            calls.append({"args_n": len(args), "kwargs": list(kwargs.keys())})
            return _MockTensor(LONG), None

    class SelfMock:
        class model:
            model = MModel()
        class model_config:
            model_type = "qwen2_5_vl"

    original_tensor = _MockTensor(input_ids_dtype)
    input_ = {
        "input_ids": original_tensor,
        "attention_mask": _MockTensor(LONG),
    }

    old_torch = _sys.modules.get("torch")
    _sys.modules["torch"] = torch_ns
    try:
        ns = {
            "torch": torch_ns,
            "input_": input_,
            "self": SelfMock(),
            "__builtins__": __builtins__,
        }
        exec(body_src, ns)
    finally:
        if old_torch is not None:
            _sys.modules["torch"] = old_torch
        else:
            _sys.modules.pop("torch", None)

    return {
        "final_dtype": repr(input_["input_ids"].dtype),
        "is_new_tensor": input_["input_ids"] is not original_tensor,
        "calls": calls,
    }
'''


def _run_python(test_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute mock-based test code in an isolated subprocess."""
    script = _EVAL_HELPERS + "\n" + test_code
    return subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """fsdp_engine.py must parse without errors."""
    source = open(FILE).read()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dtype_cast_int32_to_int64():
    """Non-long input_ids must be cast to int64/long to prevent dtype mismatch."""
    r = _run_python("""
import json
results = []
for dt in [INT32, FLOAT16, BFLOAT16]:
    res = _exec_branch(dt)
    results.append({
        "final_dtype": res["final_dtype"],
        "is_new": res["is_new_tensor"],
    })
print(json.dumps(results))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for item in results:
        dtype_str = item["final_dtype"]
        assert "long" in dtype_str or "int64" in dtype_str, (
            f"input_ids should be cast to int64/long, got {dtype_str}"
        )
        assert item["is_new"], (
            f"input_ids should be a new tensor after dtype cast"
        )


# [pr_diff] fail_to_pass
def test_dict_updated_with_cast_tensor():
    """The cast tensor must be written back to the input_ dict (not just local var)."""
    r = _run_python("""
import json
res = _exec_branch(INT32)
print(json.dumps({
    "final_dtype": res["final_dtype"],
    "is_new": res["is_new_tensor"],
}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["is_new"], (
        "input_ dict still holds original int32 tensor — cast not written back"
    )
    dtype_str = data["final_dtype"]
    assert "long" in dtype_str or "int64" in dtype_str, (
        f"input_ dict should contain tensor with int64/long dtype, got {dtype_str}"
    )


# [pr_diff] fail_to_pass
def test_keyword_args_in_get_rope_index():
    """get_rope_index must use keyword args to avoid positional binding ambiguity."""
    r = _run_python("""
import json
res = _exec_branch(INT32)
print(json.dumps(res["calls"]))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    calls = json.loads(r.stdout.strip())
    assert calls, "get_rope_index was never called"
    call = calls[0]
    n_pos = call["args_n"]
    kw = set(call["kwargs"])
    assert n_pos == 0, (
        f"get_rope_index should use keyword-only args, got {n_pos} positional"
    )
    for expected in ("input_ids", "image_grid_thw", "video_grid_thw", "attention_mask"):
        assert expected in kw, f"Missing keyword arg '{expected}', got kwargs={kw}"


# [pr_diff] fail_to_pass
def test_keyword_args_with_int64_input():
    """get_rope_index uses keyword args even when input_ids is already int64."""
    r = _run_python("""
import json
results = []
for dt in [INT64, LONG]:
    res = _exec_branch(dt)
    results.append(res["calls"])
print(json.dumps(results))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    all_calls = json.loads(r.stdout.strip())
    for calls in all_calls:
        assert calls, "get_rope_index was never called"
        call = calls[0]
        n_pos = call["args_n"]
        kw = set(call["kwargs"])
        assert n_pos == 0 and len(kw) >= 2, (
            f"get_rope_index should use keyword-only args, "
            f"got {n_pos} positional, kwargs={kw}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_noop_int64_input():
    """When input_ids is already int64, code must not crash or change dtype."""
    r = _run_python("""
import json
res = _exec_branch(INT64)
print(json.dumps({"final_dtype": res["final_dtype"]}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "long" in data["final_dtype"] or "int64" in data["final_dtype"], (
        f"int64 input_ids should be preserved, got {data['final_dtype']}"
    )


# [pr_diff] pass_to_pass
def test_noop_long_input():
    """When input_ids is already torch.long, code must not crash or change dtype."""
    r = _run_python("""
import json
res = _exec_branch(LONG)
print(json.dumps({"final_dtype": res["final_dtype"]}))
""")
    assert r.returncode == 0, f"Script failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "long" in data["final_dtype"] or "int64" in data["final_dtype"], (
        f"torch.long input_ids should be preserved, got {data['final_dtype']}"
    )


# [static] pass_to_pass
def test_not_stub():
    """_prepare_mb_list must have substantial implementation (>=10 meaningful stmts)."""
    source = open(FILE).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_prepare_mb_list":
            meaningful = 0
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                     ast.Return, ast.If, ast.For, ast.While,
                                     ast.Expr)):
                    meaningful += 1
            assert meaningful >= 10, (
                f"_prepare_mb_list has only {meaningful} meaningful statements (need >=10)"
            )
            return
    raise AssertionError("_prepare_mb_list not found")


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ f6556e88582e82b747ab1ac4038af2e106a464ee
def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in fsdp_engine.py."""
    source = open(FILE).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                assert alias.name != "*", (
                    f"Wildcard import found: from {node.module} import *"
                )


# [agent_config] pass_to_pass — AGENTS.md:90-92 @ f6556e88582e82b747ab1ac4038af2e106a464ee
def test_no_print_statements():
    """No bare print() calls in fsdp_engine.py — use areal.utils.logging logger."""
    source = open(FILE).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                raise AssertionError(
                    f"Bare print() call found at line {node.lineno} — "
                    "use areal.utils.logging.getLogger() instead"
                )


# [agent_config] pass_to_pass — AGENTS.md:189 @ f6556e88582e82b747ab1ac4038af2e106a464ee
def test_no_global_process_groups():
    """No global process group creation at module level in fsdp_engine.py."""
    source = open(FILE).read()
    tree = ast.parse(source)
    pg_funcs = {"new_group", "init_process_group"}
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if isinstance(call.func, ast.Attribute) and call.func.attr in pg_funcs:
                raise AssertionError(
                    f"Global process group creation at module level: {call.func.attr}()"
                )


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates — static analysis (no torch/GPU required)
# ---------------------------------------------------------------------------

REPO = "/repo"


# [repo_tests] pass_to_pass
def test_repo_all_python_syntax():
    """All Python files in areal/ must have valid syntax (pass_to_pass)."""
    import os

    areal_dir = os.path.join(REPO, "areal")
    errors = []

    for root, dirs, files in os.walk(areal_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path) as f:
                        source = f.read()
                    ast.parse(source)
                except SyntaxError as e:
                    rel_path = path.replace(REPO, "")
                    errors.append(f"{rel_path}: {e}")

    if errors:
        raise AssertionError(
            f"Syntax errors in {len(errors)} files:\n" + "\n".join(errors[:10])
        )


# [repo_tests] pass_to_pass
def test_repo_no_bare_excepts():
    """No bare except: clauses in areal/engine/ (pass_to_pass)."""
    import os

    engine_dir = os.path.join(REPO, "areal/engine")
    errors = []

    for root, dirs, files in os.walk(engine_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path) as f:
                    source = f.read()
                try:
                    tree = ast.parse(source)
                except SyntaxError:
                    continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        errors.append(f"{path.replace(REPO, '')}:{node.lineno}")

    if errors:
        raise AssertionError(
            f"Bare except: found in {len(errors)} locations:\n" + "\n".join(errors[:10])
        )


# [repo_tests] pass_to_pass
def test_repo_import_structure():
    """Engine module imports must be syntactically valid (pass_to_pass)."""
    import os

    fsdp_engine = os.path.join(REPO, "areal/engine/fsdp_engine.py")
    with open(fsdp_engine) as f:
        source = f.read()
    tree = ast.parse(source)

    # Check for relative imports (which should be minimal in engine files)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Ensure imports are absolute (from areal.xxx or third-party)
            if node.module and node.level > 0:
                # This is a relative import - note it but don't fail
                # (relative imports are sometimes used intentionally)
                pass

    # Just verifying the file parses with valid import statements
    # If we got here, the imports are syntactically valid
    assert True
