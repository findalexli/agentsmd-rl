"""
Task: slime-fla-gradient-inflation
Repo: THUDM/slime @ 051e91a33093cf3201acbbf96ca6748193a7eb1b
PR:   1748

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Modified code depends on megatron-core, torch.distributed, FLA which
cannot be imported in the test container. Pure-Python functions are extracted
via AST and tested behaviorally. Distributed-dependent code uses AST checks.
"""

import ast
import json
import os
import sys
import tempfile
import textwrap
import types
from pathlib import Path

REPO = "/workspace/slime"
HF_ATTN = f"{REPO}/slime_plugins/models/hf_attention.py"
QWEN35 = f"{REPO}/slime_plugins/models/qwen3_5.py"
QWEN3N = f"{REPO}/slime_plugins/models/qwen3_next.py"
RELOAD_PG = f"{REPO}/slime/utils/reloadable_process_group.py"
ALL_MODIFIED = [HF_ATTN, QWEN35, QWEN3N, RELOAD_PG]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without syntax errors."""
    for fpath in ALL_MODIFIED:
        src = Path(fpath).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core gradient inflation fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sp_gather_uses_false_output_grad():
    """SP gather must use tensor_parallel_output_grad=False to prevent gradient inflation by TP."""
    # AST-only because: gather_from_sequence_parallel_region is a megatron-core API
    # called inside HuggingfaceAttention.forward() which depends on distributed state
    src = Path(HF_ATTN).read_text()
    tree = ast.parse(src)

    for cls in ast.walk(tree):
        if not (isinstance(cls, ast.ClassDef) and cls.name == "HuggingfaceAttention"):
            continue
        for method in cls.body:
            if not (isinstance(method, ast.FunctionDef) and method.name == "forward"):
                continue
            for node in ast.walk(method):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                name = getattr(fn, "attr", getattr(fn, "id", ""))
                if name != "gather_from_sequence_parallel_region":
                    continue
                for kw in node.keywords:
                    if kw.arg == "tensor_parallel_output_grad":
                        assert (
                            isinstance(kw.value, ast.Constant) and kw.value.value is False
                        ), "tensor_parallel_output_grad must be explicitly False"
                        return
                assert False, "gather call missing tensor_parallel_output_grad keyword"
    assert False, "HuggingfaceAttention.forward with gather call not found"


# [pr_diff] fail_to_pass
def test_cp_custom_autograd_function():
    """CP gather must use a custom autograd.Function (not dist.nn.all_gather) to avoid gradient inflation."""
    # AST-only because: HuggingfaceAttention.forward depends on megatron mpu and
    # torch.distributed process groups that cannot be initialized in the test container
    src = Path(HF_ATTN).read_text()
    tree = ast.parse(src)

    # Verify a class inheriting from torch.autograd.Function exists with forward + backward
    found_autograd_class = False
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        is_function_subclass = any("Function" in ast.dump(base) for base in node.bases)
        if not is_function_subclass:
            continue
        methods = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
        if "forward" in methods and "backward" in methods:
            found_autograd_class = True
            break

    assert found_autograd_class, (
        "No torch.autograd.Function subclass with forward/backward in hf_attention.py"
    )

    # Verify forward() no longer calls dist.nn.all_gather
    for cls in ast.walk(tree):
        if not (isinstance(cls, ast.ClassDef) and cls.name == "HuggingfaceAttention"):
            continue
        for method in cls.body:
            if not (isinstance(method, ast.FunctionDef) and method.name == "forward"):
                continue
            for node in ast.walk(method):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                if (
                    isinstance(fn, ast.Attribute)
                    and fn.attr == "all_gather"
                    and isinstance(fn.value, ast.Attribute)
                    and fn.value.attr == "nn"
                ):
                    assert False, "forward() still uses dist.nn.all_gather"
            return
    assert False, "HuggingfaceAttention.forward not found"


# [pr_diff] fail_to_pass
def test_autograd_backward_returns_local_slice():
    """Custom autograd backward must return only the local rank's gradient (no reduce)."""
    src = Path(HF_ATTN).read_text()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)

    # Find the autograd.Function subclass and extract its backward method
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any("Function" in ast.dump(base) for base in node.bases):
            continue
        methods = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
        if "forward" not in methods or "backward" not in methods:
            continue

        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "backward"):
                continue
            bwd_src = "".join(lines[item.lineno - 1 : item.end_lineno])
            # Strip decorators (@staticmethod) and dedent
            bwd_lines = [
                ln for ln in bwd_src.strip().splitlines()
                if not ln.strip().startswith("@")
            ]
            bwd_clean = textwrap.dedent("\n".join(bwd_lines))

            ns = {}
            exec(bwd_clean, ns)
            backward_fn = ns["backward"]

            # Test with multiple ranks and world sizes — the backward must return
            # only the gradient at the caller's rank index, not a sum
            for world_size in [2, 4, 8]:
                grads = [f"grad_{i}" for i in range(world_size)]
                for rank in range(world_size):
                    ctx = types.SimpleNamespace(rank=rank, group=None)
                    result = backward_fn(ctx, *grads)
                    assert result[0] == f"grad_{rank}", (
                        f"backward(rank={rank}, ws={world_size}) returned "
                        f"{result[0]}, expected grad_{rank}"
                    )
                    assert result[1] is None, (
                        "backward must return None for the group parameter gradient"
                    )
            return

    assert False, "No autograd.Function subclass with backward found in hf_attention.py"


# [pr_diff] fail_to_pass
def test_load_hf_config_fallback_behavior():
    """_load_hf_config fallback must correctly load config.json as namespace when AutoConfig fails."""
    src = Path(HF_ATTN).read_text()
    tree = ast.parse(src)
    file_lines = src.splitlines(keepends=True)

    # Extract _load_hf_config function source
    func_src = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_load_hf_config":
            func_src = "".join(file_lines[node.lineno - 1 : node.end_lineno])
            break
    assert func_src is not None, "_load_hf_config not found in hf_attention.py"

    # Build mock environment so the function can execute
    mock_torch = types.ModuleType("torch")
    mock_torch.bfloat16 = "BF16"
    mock_torch.float16 = "FP16"
    mock_torch.float32 = "FP32"

    mock_transformers = types.ModuleType("transformers")

    class _FakeAutoConfig:
        @staticmethod
        def from_pretrained(*a, **kw):
            raise ValueError("unsupported model type")

    mock_transformers.AutoConfig = _FakeAutoConfig

    old_transformers = sys.modules.get("transformers")
    sys.modules["transformers"] = mock_transformers
    try:
        fn_globals = {"__builtins__": __builtins__, "torch": mock_torch, "os": os, "json": json}
        exec(func_src, fn_globals)
        load_fn = fn_globals["_load_hf_config"]

        # Case 1: simple config
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "config.json"), "w") as f:
                json.dump({"hidden_size": 1024, "num_hidden_layers": 32}, f)
            cfg = load_fn(d)
            assert cfg.hidden_size == 1024, f"hidden_size={cfg.hidden_size}, expected 1024"
            assert cfg.num_hidden_layers == 32

        # Case 2: config with nested text_config
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "config.json"), "w") as f:
                json.dump({
                    "hidden_size": 2048,
                    "text_config": {"hidden_size": 512, "num_attention_heads": 8},
                }, f)
            cfg = load_fn(d)
            assert cfg.hidden_size == 2048
            assert hasattr(cfg, "text_config"), "text_config sub-namespace missing"
            assert cfg.text_config.hidden_size == 512
            assert cfg.text_config.num_attention_heads == 8

        # Case 3: torch_dtype string gets mapped to mock torch dtype
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "config.json"), "w") as f:
                json.dump({"hidden_size": 768, "torch_dtype": "bfloat16"}, f)
            cfg = load_fn(d)
            assert cfg.torch_dtype == "BF16", (
                f"torch_dtype not mapped correctly: got {cfg.torch_dtype}"
            )
    finally:
        if old_transformers is not None:
            sys.modules["transformers"] = old_transformers
        else:
            sys.modules.pop("transformers", None)


# [pr_diff] fail_to_pass
def test_layer_types_fallback_qwen35():
    """qwen3_5.py must compute layer_types from full_attention_interval when config lacks it."""
    _check_layer_types_fallback(QWEN35, "get_qwen3_5_spec")


# [pr_diff] fail_to_pass
def test_layer_types_fallback_qwen3next():
    """qwen3_next.py must compute layer_types from full_attention_interval when config lacks it."""
    _check_layer_types_fallback(QWEN3N, "get_qwen3_next_spec")


def _check_layer_types_fallback(filepath, func_name):
    """Verify func has hasattr/getattr check for layer_types + full_attention_interval usage."""
    # AST-only because: get_qwen3_*_spec depends on megatron config, vp_stage, and
    # transformer spec objects that cannot be constructed in the test container
    src = Path(filepath).read_text()
    tree = ast.parse(src)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_node = node
            break
    assert func_node is not None, f"{func_name} not found in {filepath}"

    has_layer_types_check = False
    has_interval_ref = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("hasattr", "getattr"):
                if any(
                    isinstance(a, ast.Constant) and a.value == "layer_types"
                    for a in node.args
                ):
                    has_layer_types_check = True
        if isinstance(node, ast.Attribute) and node.attr == "full_attention_interval":
            has_interval_ref = True
        if isinstance(node, ast.Constant) and node.value == "full_attention_interval":
            has_interval_ref = True

    assert has_layer_types_check, f"No layer_types hasattr/getattr check in {func_name}"
    assert has_interval_ref, f"No full_attention_interval reference in {func_name}"


# [pr_diff] fail_to_pass
def test_qwen_files_import_shared_load_hf_config():
    """qwen3_5 and qwen3_next must import _load_hf_config from hf_attention, not define locally."""
    # AST-only because: checking import structure, not runtime behavior
    for fpath in [QWEN35, QWEN3N]:
        src = Path(fpath).read_text()
        tree = ast.parse(src)
        name = Path(fpath).name

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_load_hf_config":
                assert False, f"{name} defines _load_hf_config locally instead of importing"

        found_import = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and "hf_attention" in node.module:
                if any(alias.name == "_load_hf_config" for alias in node.names):
                    found_import = True
        assert found_import, f"{name} does not import _load_hf_config from hf_attention"


# [pr_diff] fail_to_pass
def test_memory_threshold_lowered():
    """reloadable_process_group.py memory threshold must be lowered from 5 to 3 GB."""
    # AST-only because: _wrap_low_level_call uses available_memory() and clear_memory()
    # which require GPU/system runtime that is not available in the test container
    src = Path(RELOAD_PG).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not (len(node.ops) == 1 and isinstance(node.ops[0], ast.Lt)):
            continue
        if not (len(node.comparators) == 1 and isinstance(node.comparators[0], ast.Constant)):
            continue
        # Check if left side is mem_info["free_GB"]
        left = node.left
        if not isinstance(left, ast.Subscript):
            continue
        slice_node = left.slice
        if isinstance(slice_node, ast.Constant) and slice_node.value == "free_GB":
            threshold = node.comparators[0].value
            assert threshold <= 3, (
                f"Memory threshold is {threshold} GB, expected <= 3 GB"
            )
            return

    assert False, 'free_GB < N comparison not found in reloadable_process_group.py'


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports in modified production files."""
    for fpath in [HF_ATTN, QWEN35, QWEN3N]:
        src = Path(fpath).read_text()
        tree = ast.parse(src)
        name = Path(fpath).name
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", (
                        f"Wildcard import in {name}: from {node.module} import *"
                    )


# [static] pass_to_pass
def test_no_bare_print():
    """No bare print() calls in modified production files."""
    for fpath in [HF_ATTN, QWEN35, QWEN3N]:
        src = Path(fpath).read_text()
        tree = ast.parse(src)
        name = Path(fpath).name
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "print"
            ):
                assert False, f"Bare print() call in {name}"
