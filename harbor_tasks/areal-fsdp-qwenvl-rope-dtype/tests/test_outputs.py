"""
Task: areal-fsdp-qwenvl-rope-dtype
Repo: inclusionAI/AReaL @ f6556e88582e82b747ab1ac4038af2e106a464ee
PR:   1094

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The FSDP engine requires distributed process groups and multi-GB model weights,
so we AST-extract the Qwen-VL branch from _prepare_mb_list and exec it with
lightweight mock objects on CPU.
# AST-only because: FSDPEngine requires torch.distributed, FSDP, multi-GPU
"""

import ast
import sys
import textwrap
import types

FILE = "/repo/areal/engine/fsdp_engine.py"


# ---------------------------------------------------------------------------
# Helpers: mock torch environment + AST extraction
# ---------------------------------------------------------------------------

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
    """Build a mock torch module namespace."""
    ns = types.ModuleType("torch")
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
    """AST-extract the is_qwen_vl_model branch from _prepare_mb_list."""
    source = open(FILE).read()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_prepare_mb_list":
            func_node = node
            break
    assert func_node is not None, "_prepare_mb_list not found in fsdp_engine.py"

    vl_if = None
    for child in ast.walk(func_node):
        if isinstance(child, ast.If):
            test_src = ast.get_source_segment(source, child.test)
            if test_src and "qwen_vl" in test_src.lower().replace("-", "_").replace(" ", "_"):
                vl_if = child
                break
    assert vl_if is not None, "is_qwen_vl_model branch not found in _prepare_mb_list"

    body_start = vl_if.body[0].lineno
    body_end = vl_if.body[-1].end_lineno
    raw_lines = source.splitlines()[body_start - 1:body_end]
    return textwrap.dedent("\n".join(raw_lines))


def _exec_branch(input_ids_dtype):
    """Execute the Qwen-VL branch with a mock input_ dict and return results."""
    body_src = _extract_qwen_vl_branch()
    torch_ns = _make_torch_ns()

    calls = []

    class MModel:
        @staticmethod
        def get_rope_index(*args, **kwargs):
            calls.append({"args": args, "kwargs": kwargs})
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

    old_torch = sys.modules.get("torch")
    sys.modules["torch"] = torch_ns
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
            sys.modules["torch"] = old_torch
        else:
            sys.modules.pop("torch", None)

    return {
        "input_": input_,
        "original_tensor": original_tensor,
        "calls": calls,
    }


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """fsdp_engine.py must parse without errors."""
    source = open(FILE).read()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dtype_cast_int32_to_int64():
    """Non-long input_ids must be cast to int64/long to prevent dtype mismatch."""
    # Test multiple non-long dtypes — prevents agents from only special-casing int32
    for dtype in (INT32, FLOAT16, BFLOAT16):
        result = _exec_branch(dtype)
        final = result["input_"]["input_ids"]
        assert final.dtype in (LONG, INT64), (
            f"input_ids with {dtype} should be cast to int64/long, got {final.dtype}"
        )
        assert final is not result["original_tensor"], (
            f"input_ids with {dtype} should be a new tensor after dtype cast"
        )


# [pr_diff] fail_to_pass
def test_dict_updated_with_cast_tensor():
    """The cast tensor must be written back to the input_ dict (not just local var)."""
    result = _exec_branch(INT32)
    final = result["input_"]["input_ids"]
    # The dict must hold the cast tensor, not the original
    assert final is not result["original_tensor"], (
        "input_ dict still holds original int32 tensor — cast not written back"
    )
    assert final.dtype in (LONG, INT64), (
        f"input_ dict should contain tensor with int64/long dtype, got {final.dtype}"
    )


# [pr_diff] fail_to_pass
def test_keyword_args_in_get_rope_index():
    """get_rope_index must use keyword args to avoid positional binding ambiguity."""
    result = _exec_branch(INT32)
    assert result["calls"], "get_rope_index was never called"
    call = result["calls"][0]
    kw = set(call["kwargs"].keys())
    n_pos = len(call["args"])
    # Must use zero positional args and all keyword args
    assert n_pos == 0, (
        f"get_rope_index should use keyword-only args, got {n_pos} positional"
    )
    # All 4 params must be keyword args
    for expected in ("input_ids", "image_grid_thw", "video_grid_thw", "attention_mask"):
        assert expected in kw, f"Missing keyword arg '{expected}', got kwargs={kw}"


# [pr_diff] fail_to_pass
def test_keyword_args_with_int64_input():
    """get_rope_index uses keyword args even when input_ids is already int64."""
    for dtype in (INT64, LONG):
        result = _exec_branch(dtype)
        assert result["calls"], "get_rope_index was never called"
        call = result["calls"][0]
        n_pos = len(call["args"])
        assert n_pos == 0 and len(call["kwargs"]) >= 2, (
            f"get_rope_index should use keyword-only args for {dtype}, "
            f"got {n_pos} positional, kwargs={set(call['kwargs'].keys())}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_noop_int64_input():
    """When input_ids is already int64, code must not crash or change dtype."""
    result = _exec_branch(INT64)
    final = result["input_"]["input_ids"]
    assert final.dtype in (LONG, INT64), (
        f"int64 input_ids should be preserved, got {final.dtype}"
    )


# [pr_diff] pass_to_pass
def test_noop_long_input():
    """When input_ids is already torch.long, code must not crash or change dtype."""
    result = _exec_branch(LONG)
    final = result["input_"]["input_ids"]
    assert final.dtype in (LONG, INT64), (
        f"torch.long input_ids should be preserved, got {final.dtype}"
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
# AST-only because: checking module-level code structure, not runtime behavior
def test_no_global_process_groups():
    """No global process group creation at module level in fsdp_engine.py."""
    source = open(FILE).read()
    tree = ast.parse(source)
    pg_funcs = {"new_group", "init_process_group"}
    for node in tree.body:
        # Only check module-level statements (not inside functions/classes)
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            # Check for dist.new_group() or dist.init_process_group() at module level
            if isinstance(call.func, ast.Attribute) and call.func.attr in pg_funcs:
                raise AssertionError(
                    f"Global process group creation at module level: {call.func.attr}()"
                )
