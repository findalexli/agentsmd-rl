"""
Task: vllm-mamba-cudagraph-cache-raise
Repo: vllm-project/vllm @ 03ac6ca8954d491dc39ae169c2623e8ccffba7c6
PR:   #38270

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

REPO = "/workspace/vllm"
RUNNER = f"{REPO}/vllm/v1/worker/gpu_model_runner.py"
CONFIG = f"{REPO}/vllm/config/compilation.py"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _find_method(tree, source, method_name, *, file_label="file"):
    """Return (node, source_text) for a method/function by name."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == method_name:
                text = "\n".join(source.splitlines()[node.lineno - 1 : node.end_lineno])
                return node, text
    raise AssertionError(f"{method_name} not found in {file_label}")


def _find_class(tree, class_name, *, file_label="file"):
    """Return class node by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    raise AssertionError(f"{class_name} not found in {file_label}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [RUNNER, CONFIG]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: vllm requires torch/CUDA/GPU — unavailable in test container
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_silent_capping_method_removed():
    """adjust_cudagraph_sizes_for_mamba_cache must not exist in CompilationConfig.

    The buggy code silently caps cudagraph_capture_sizes for both prefill and
    decode via this method. The fix removes it entirely because the constraint
    only applies to FULL decode graphs and should raise, not silently cap.
    """
    # AST-only because: CompilationConfig requires torch/pydantic/vllm internals
    source = Path(CONFIG).read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "CompilationConfig", file_label="compilation.py")
    method_names = [
        item.name
        for item in cls.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "adjust_cudagraph_sizes_for_mamba_cache" not in method_names, (
        "CompilationConfig still has adjust_cudagraph_sizes_for_mamba_cache — "
        "silent capping not eliminated"
    )


# [pr_diff] fail_to_pass
def test_raises_on_insufficient_mamba_blocks():
    """_check_and_update_cudagraph_mode must raise when max_num_seqs > num_blocks.

    On the buggy baseline, this function calls adjust_cudagraph_sizes_for_mamba_cache
    which silently caps sizes. The fix must raise an informative error instead.
    """
    # AST-only because: method requires torch, CUDA backends, full vllm init
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)
    node, func_text = _find_method(
        tree, source, "_check_and_update_cudagraph_mode", file_label="gpu_model_runner.py"
    )

    # Must NOT call the silent capping method
    assert "adjust_cudagraph_sizes_for_mamba_cache" not in func_text, (
        "Still calls adjust_cudagraph_sizes_for_mamba_cache (silent capping)"
    )

    # Must have a Raise referencing mamba/blocks
    has_raise = False
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            raise_text = "\n".join(
                source.splitlines()[child.lineno - 1 : child.end_lineno]
            )
            if "block" in raise_text.lower() or "mamba" in raise_text.lower():
                has_raise = True
                break
    assert has_raise, "No error raised for insufficient Mamba cache blocks"


# [pr_diff] fail_to_pass
def test_profiling_skips_mamba_validation():
    """_init_minimal_kv_cache_for_profiling must signal profiling to skip validation.

    The buggy code calls initialize_kv_cache(minimal_config) with no profiling
    signal, causing false errors with artificially small cache during profiling.
    The fix must thread a profiling indicator through the call chain.
    """
    # AST-only because: method requires full GPU model runner + CUDA
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)
    node, _ = _find_method(
        tree, source, "_init_minimal_kv_cache_for_profiling", file_label="gpu_model_runner.py"
    )

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and func.attr == "initialize_kv_cache":
                # Buggy: exactly 1 positional arg, no keywords
                # Fixed: extra arg or keyword signaling profiling
                has_extra = len(child.args) > 1 or len(child.keywords) > 0
                assert has_extra, (
                    "initialize_kv_cache called without profiling signal — "
                    "buggy pattern unchanged"
                )
                return
    raise AssertionError(
        "No call to initialize_kv_cache found in _init_minimal_kv_cache_for_profiling"
    )


# [pr_diff] fail_to_pass
def test_no_silent_cap_reference_in_runner():
    """gpu_model_runner.py must not reference adjust_cudagraph_sizes_for_mamba_cache.

    On the buggy baseline, the runner calls this method. After the fix, all
    references should be removed since the approach changed to raising an error.
    """
    content = Path(RUNNER).read_text()
    assert "adjust_cudagraph_sizes_for_mamba_cache" not in content, (
        "Runner still references adjust_cudagraph_sizes_for_mamba_cache"
    )


# [pr_diff] fail_to_pass
def test_is_profiling_param_threaded():
    """is_profiling parameter must be accepted by all 3 methods in the call chain.

    The fix threads is_profiling through: initialize_kv_cache ->
    initialize_attn_backend -> _check_and_update_cudagraph_mode.
    On the base commit, none of these methods accept a profiling parameter.
    """
    # AST-only because: methods require torch/CUDA/vllm internals
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)

    target_methods = {
        "initialize_kv_cache",
        "initialize_attn_backend",
        "_check_and_update_cudagraph_mode",
    }
    found = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in target_methods:
                all_params = (
                    [a.arg for a in node.args.args]
                    + [a.arg for a in node.args.kwonlyargs]
                )
                found[node.name] = any("profil" in p for p in all_params)

    missing = target_methods - set(found.keys())
    assert not missing, f"Methods not found: {missing}"

    no_profiling = [m for m, has in found.items() if not has]
    assert not no_profiling, (
        f"Methods missing profiling parameter: {no_profiling}"
    )


# [pr_diff] fail_to_pass
def test_kv_cache_forwards_profiling_to_attn_backend():
    """initialize_kv_cache must forward profiling signal to initialize_attn_backend.

    On base, initialize_kv_cache calls initialize_attn_backend(kv_cache_config)
    with no profiling arg. The fix must forward the profiling state.
    """
    # AST-only because: methods require torch/CUDA/vllm internals
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)
    node, _ = _find_method(
        tree, source, "initialize_kv_cache", file_label="gpu_model_runner.py"
    )

    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Attribute) and func.attr == "initialize_attn_backend":
                has_extra = len(child.args) > 1 or len(child.keywords) > 0
                assert has_extra, (
                    "initialize_attn_backend called without profiling signal "
                    "in initialize_kv_cache"
                )
                return
    raise AssertionError(
        "No call to initialize_attn_backend found in initialize_kv_cache"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_spec_decode_adjustment_preserved():
    """adjust_cudagraph_sizes_for_spec_decode must still exist and function.

    This is an unrelated method on CompilationConfig that must not be
    accidentally removed or broken by the fix.
    """
    source = Path(CONFIG).read_text()
    tree = ast.parse(source)
    cls = _find_class(tree, "CompilationConfig", file_label="compilation.py")
    method_names = [
        item.name
        for item in cls.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "adjust_cudagraph_sizes_for_spec_decode" in method_names, (
        "adjust_cudagraph_sizes_for_spec_decode was removed"
    )


# [static] pass_to_pass
def test_core_methods_preserved():
    """Key methods in gpu_model_runner.py must still exist."""
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)

    required = {
        "_check_and_update_cudagraph_mode",
        "initialize_kv_cache",
        "initialize_attn_backend",
        "_init_minimal_kv_cache_for_profiling",
    }
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in required:
                found.add(node.name)

    missing = required - found
    assert not missing, f"Missing methods: {missing}"


# [static] pass_to_pass
def test_check_cudagraph_mode_not_stub():
    """_check_and_update_cudagraph_mode must have real logic, not be a stub."""
    source = Path(RUNNER).read_text()
    tree = ast.parse(source)
    node, _ = _find_method(
        tree, source, "_check_and_update_cudagraph_mode", file_label="gpu_model_runner.py"
    )

    meaningful = sum(
        1
        for child in ast.walk(node)
        if isinstance(
            child,
            (ast.Assign, ast.AugAssign, ast.AnnAssign,
             ast.If, ast.For, ast.While, ast.Return,
             ast.Raise, ast.Expr),
        )
    )
    assert meaningful >= 10, (
        f"_check_and_update_cudagraph_mode appears stubbed "
        f"({meaningful} statements, expected >=10)"
    )
