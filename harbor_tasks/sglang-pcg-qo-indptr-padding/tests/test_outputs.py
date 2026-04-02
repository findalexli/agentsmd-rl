"""
Task: sglang-pcg-qo-indptr-padding
Repo: sgl-project/sglang @ efebcab43ed851405bd41cfdf206245945dbb8ee
PR:   #21452

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import types
from pathlib import Path

REPO = "/workspace/sglang"

CTX_MGR = f"{REPO}/python/sglang/srt/compilation/piecewise_context_manager.py"
FLASH_BE = f"{REPO}/python/sglang/srt/layers/attention/flashinfer_backend.py"
PCG_RUN = f"{REPO}/python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py"


def _load_context_manager():
    """Load piecewise_context_manager.py with mocked torch (no GPU needed)."""
    mock_torch = types.ModuleType("torch")
    mock_cuda = types.ModuleType("torch.cuda")

    class _MockStream:
        pass

    mock_cuda.Stream = _MockStream
    mock_torch.cuda = mock_cuda
    sys.modules["torch"] = mock_torch
    sys.modules["torch.cuda"] = mock_cuda

    for pkg in [
        "sglang",
        "sglang.srt",
        "sglang.srt.compilation",
        "sglang.srt.model_executor",
    ]:
        m = types.ModuleType(pkg)
        m.__path__ = [f"{REPO}/python/{pkg.replace('.', '/')}"]
        sys.modules[pkg] = m

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "sglang.srt.compilation.piecewise_context_manager",
        CTX_MGR,
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """All three modified files must parse without syntax errors."""
    for path in [CTX_MGR, FLASH_BE, PCG_RUN]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_forward_context_has_num_tokens():
    """ForwardContext must have a num_tokens attribute; set_forward_context must accept it."""
    mod = _load_context_manager()
    FC = mod.ForwardContext
    sfc = mod.set_forward_context

    # ForwardContext instances must have num_tokens
    fc = FC()
    assert hasattr(fc, "num_tokens"), "ForwardContext missing num_tokens attribute"

    # set_forward_context must accept num_tokens keyword
    import inspect

    sig = inspect.signature(sfc)
    assert "num_tokens" in sig.parameters, (
        "set_forward_context does not accept num_tokens parameter"
    )


# [pr_diff] fail_to_pass
def test_num_tokens_propagation():
    """num_tokens value propagates through set_forward_context and varies with input."""
    mod = _load_context_manager()
    sfc = mod.set_forward_context
    gfc = mod.get_forward_context

    # Propagate num_tokens=42
    with sfc(None, None, None, [], [], num_tokens=42):
        fwd = gfc()
        assert fwd is not None, "get_forward_context() returned None inside context"
        assert fwd.num_tokens == 42, f"expected num_tokens=42, got {fwd.num_tokens}"

    # Different value propagates (not hardcoded)
    with sfc(None, None, None, [], [], num_tokens=256):
        fwd2 = gfc()
        assert fwd2.num_tokens == 256, f"expected num_tokens=256, got {fwd2.num_tokens}"

    # Default (no num_tokens) gives None
    with sfc(None, None, None, [], []):
        fwd3 = gfc()
        assert fwd3.num_tokens is None, (
            f"default num_tokens should be None, got {fwd3.num_tokens}"
        )


# [pr_diff] fail_to_pass
def test_replay_num_tokens_and_ordering():
    # AST-only because: piecewise_cuda_graph_runner.py imports torch, bisect,
    # CUDA graph APIs, ModelRunner, ForwardBatch — cannot be imported without GPU.
    """replay() passes num_tokens to set_forward_context and calls
    init_forward_metadata inside the context block (ordering fix)."""
    source = Path(PCG_RUN).read_text()
    tree = ast.parse(source)

    replay_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "replay":
            replay_func = node
            break
    assert replay_func is not None, "replay method not found"

    # set_forward_context called with num_tokens keyword
    found_kwarg = False
    for node in ast.walk(replay_func):
        calls = []
        if isinstance(node, ast.Call):
            calls.append(node)
        if isinstance(node, ast.withitem) and isinstance(node.context_expr, ast.Call):
            calls.append(node.context_expr)
        for call in calls:
            cname = ""
            if isinstance(call.func, ast.Name):
                cname = call.func.id
            elif isinstance(call.func, ast.Attribute):
                cname = call.func.attr
            if cname == "set_forward_context":
                kw_names = [kw.arg for kw in call.keywords]
                if "num_tokens" in kw_names:
                    found_kwarg = True
    assert found_kwarg, "replay does not pass num_tokens keyword to set_forward_context"

    # init_forward_metadata called INSIDE the set_forward_context with-block
    found_inside = False
    for node in ast.walk(replay_func):
        if isinstance(node, ast.With):
            for item in node.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Call):
                    cname = ""
                    if isinstance(ctx.func, ast.Name):
                        cname = ctx.func.id
                    elif isinstance(ctx.func, ast.Attribute):
                        cname = ctx.func.attr
                    if cname == "set_forward_context":
                        with_src = "\n".join(
                            source.splitlines()[node.lineno - 1 : node.end_lineno]
                        )
                        if "init_forward_metadata" in with_src:
                            found_inside = True
    assert found_inside, (
        "init_forward_metadata not called inside set_forward_context with-block"
    )


# [pr_diff] fail_to_pass
def test_call_begin_forward_pcg_padding():
    # AST-only because: flashinfer_backend.py imports torch, flashinfer C++ bindings,
    # ModelRunner, and dozens of sglang internals — cannot be imported without GPU.
    """call_begin_forward extends qo_indptr/kv_indptr for PCG padding tokens."""
    source = Path(FLASH_BE).read_text()
    tree = ast.parse(source)

    func_nodes = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "call_begin_forward"
    ]
    assert func_nodes, "call_begin_forward not found"

    concat_ops = ["torch.cat", ".cat(", "concat", "torch.concatenate", "append"]
    found_padding = False
    for func_node in func_nodes:
        func_src = "\n".join(
            source.splitlines()[func_node.lineno - 1 : func_node.end_lineno]
        )
        if "get_forward_context" not in func_src:
            continue
        has_qo = "qo_indptr" in func_src and any(op in func_src for op in concat_ops)
        has_kv = "kv_indptr" in func_src and any(op in func_src for op in concat_ops)
        if not (has_qo and has_kv):
            continue
        if "num_tokens" not in func_src:
            continue
        # Must have conditional guard for padding
        has_guard = False
        for inner in ast.walk(func_node):
            if isinstance(inner, ast.If):
                if_src = "\n".join(
                    source.splitlines()[inner.lineno - 1 : inner.end_lineno]
                )
                if any(kw in if_src for kw in ["num_tokens", "token", "pad", "pcg"]):
                    has_guard = True
                    break
        if not has_guard:
            continue
        # Anti-stub: must be substantial
        if func_node.end_lineno - func_node.lineno + 1 < 30:
            continue
        found_padding = True
        break

    assert found_padding, (
        "no call_begin_forward has PCG padding logic "
        "(get_forward_context + qo/kv_indptr extension + num_tokens + conditional guard)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_context_manager_api():
    """Original ForwardContext attributes and context manager preserved."""
    mod = _load_context_manager()
    FC = mod.ForwardContext
    sfc = mod.set_forward_context
    gfc = mod.get_forward_context

    # Required exports exist
    for name in [
        "set_forward_context",
        "get_forward_context",
        "is_in_piecewise_cuda_graph",
        "enable_piecewise_cuda_graph",
    ]:
        assert getattr(mod, name, None) is not None, f"missing export: {name}"

    # ForwardContext retains original attributes
    fc = FC()
    for attr in ["forward_batch", "quant_config", "moe_layers", "moe_fusions"]:
        assert hasattr(fc, attr), f"ForwardContext missing attr: {attr}"

    # get_forward_context returns None outside any context
    assert gfc() is None, "get_forward_context should return None outside context"

    # Context manager round-trip (without num_tokens, backwards compat)
    with sfc(None, None, None, [], []):
        inside = gfc()
        assert inside is not None, "get_forward_context returned None inside context"
        assert hasattr(inside, "forward_batch"), "context missing forward_batch"
    assert gfc() is None, "forward context not cleared after exiting"


# [static] pass_to_pass
def test_files_not_stubbed():
    """Modified files retain expected content and are not hollowed out."""
    checks = [
        (
            CTX_MGR,
            50,
            [
                "ForwardContext",
                "set_forward_context",
                "get_forward_context",
                "_forward_context",
            ],
        ),
        (
            FLASH_BE,
            500,
            [
                "FlashInferAttnBackend",
                "call_begin_forward",
                "kv_indptr",
                "qo_indptr",
                "kv_indices",
            ],
        ),
        (
            PCG_RUN,
            200,
            [
                "PiecewiseCudaGraphRunner",
                "replay",
                "set_forward_context",
                "capture_num_tokens",
            ],
        ),
    ]
    for path, min_lines, required_symbols in checks:
        content = Path(path).read_text()
        lines = len(content.splitlines())
        fname = Path(path).name
        assert lines >= min_lines, f"{fname} has only {lines} lines (min {min_lines})"
        missing = [s for s in required_symbols if s not in content]
        assert not missing, f"{fname} missing: {missing}"
