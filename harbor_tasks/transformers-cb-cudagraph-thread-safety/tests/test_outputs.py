"""
Task: transformers-cb-cudagraph-thread-safety
Repo: huggingface/transformers @ e5ad3946209fb96db5e9965b3eb67d69cc3749e0
PR:   44924

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import textwrap
import types
import unittest.mock as mock
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/transformers/generation/continuous_batching/continuous_api.py"


# ---------------------------------------------------------------------------
# Helpers — extract _generation_step and exec it with a fake torch
# ---------------------------------------------------------------------------
# AST extraction + exec because: _generation_step depends on torch.cuda (GPU)
# but the function body is pure Python once torch is mocked.


def _build_fake_torch():
    """Build a minimal fake torch module so _generation_step can execute."""
    torch_mod = types.ModuleType("torch")
    cuda_mod = types.ModuleType("torch.cuda")
    nn_mod = types.ModuleType("torch.nn")

    captured_graph_calls = []

    class _FakeGraphCtx:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

    def fake_cuda_graph(*args, **kwargs):
        captured_graph_calls.append({"args": args, "kwargs": kwargs})
        return _FakeGraphCtx()

    cuda_mod.graph = fake_cuda_graph
    cuda_mod.stream = lambda *a, **kw: _FakeGraphCtx()  # warmup uses with torch.cuda.stream(...)
    cuda_mod.CUDAGraph = lambda: mock.MagicMock()
    cuda_mod.graph_pool_handle = lambda: mock.MagicMock()
    cuda_mod.current_stream = lambda *a, **kw: mock.MagicMock()
    cuda_mod.Stream = lambda *a, **kw: mock.MagicMock()
    cuda_mod.is_available = lambda: False
    torch_mod.cuda = cuda_mod
    torch_mod.nn = nn_mod
    nn_mod.Module = type("Module", (), {})
    torch_mod.no_grad = lambda: mock.MagicMock(
        __enter__=lambda s: None, __exit__=lambda s, *a: None
    )
    torch_mod.Tensor = mock.MagicMock
    torch_mod.inference_mode = lambda: mock.MagicMock(
        __enter__=lambda s: None, __exit__=lambda s, *a: None
    )

    return torch_mod, cuda_mod, nn_mod, captured_graph_calls


def _extract_generation_step(torch_mod, nn_mod):
    """Extract _generation_step from source via AST, exec it, return callable."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_generation_step":
            lines = source.splitlines(keepends=True)
            func_source = textwrap.dedent(
                "".join(lines[node.lineno - 1 : node.end_lineno])
            )
            import contextlib

            ns = {
                "torch": torch_mod,
                "nn": nn_mod,
                "gc": __import__("gc"),
                "contextlib": contextlib,
                "nullcontext": contextlib.nullcontext,
                "LogitsProcessorList": mock.MagicMock,
                "__builtins__": __builtins__,
            }
            exec(func_source, ns)
            return ns["_generation_step"]
    raise AssertionError("_generation_step not found in source")


def _invoke_generation_step(gen_step, captured_graph_calls):
    """Call _generation_step with mocks that trigger the graph-creation branch."""
    captured_graph_calls.clear()

    mock_self = mock.MagicMock()
    mock_self.use_cuda_graph = True
    mock_self.graph_pool = mock.MagicMock()
    # get_graph() returns None → forces new graph capture (else branch)
    mock_self.inputs_and_outputs.get_graph.return_value = None
    mock_self.inputs_and_outputs.compute_stream = mock.MagicMock()
    # get_cb_kwargs() returns a 3-tuple (carry_over_ids, prev_output_ids, output_ids)
    mock_self.inputs_and_outputs.get_cb_kwargs.return_value = (
        mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
    )

    mock_model = mock.MagicMock()
    mock_logit_proc = mock.MagicMock()

    try:
        gen_step(mock_self, mock_model, mock_logit_proc, True)
    except Exception:
        pass  # downstream mock gaps are fine; we only need the cuda.graph call


def _with_fake_torch(fn):
    """Context helper: inject fake torch into sys.modules, restore on exit."""
    torch_mod, cuda_mod, nn_mod, captured = _build_fake_torch()
    saved = {k: sys.modules.get(k) for k in ["torch", "torch.cuda", "torch.nn"]}
    sys.modules["torch"] = torch_mod
    sys.modules["torch.cuda"] = cuda_mod
    sys.modules["torch.nn"] = nn_mod
    try:
        return fn(torch_mod, nn_mod, captured)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_capture_error_mode_thread_safe():
    """torch.cuda.graph() must be called with a non-global capture_error_mode."""

    def check(torch_mod, nn_mod, captured):
        gen_step = _extract_generation_step(torch_mod, nn_mod)
        _invoke_generation_step(gen_step, captured)

        assert len(captured) > 0, "torch.cuda.graph() was never called"
        mode = captured[0]["kwargs"].get("capture_error_mode")
        assert mode is not None, "capture_error_mode not passed to torch.cuda.graph()"
        assert mode != "global", f"capture_error_mode={mode!r} is not thread-safe"

    _with_fake_torch(check)


# [pr_diff] fail_to_pass
def test_capture_error_mode_recognized_safe():
    """capture_error_mode must be a recognized thread-safe mode (not absent, not 'global')."""

    THREAD_SAFE_MODES = {"thread_local", "relaxed"}

    def check(torch_mod, nn_mod, captured):
        gen_step = _extract_generation_step(torch_mod, nn_mod)
        _invoke_generation_step(gen_step, captured)

        assert len(captured) > 0, "torch.cuda.graph() was never called"
        mode = captured[0]["kwargs"].get("capture_error_mode")
        assert isinstance(mode, str), (
            f"capture_error_mode should be a string, got {type(mode).__name__}"
        )
        assert mode in THREAD_SAFE_MODES, (
            f"capture_error_mode={mode!r} is not a recognized thread-safe mode "
            f"(expected one of {THREAD_SAFE_MODES})"
        )

    _with_fake_torch(check)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + style
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_generation_step_not_stub():
    """_generation_step has meaningful logic (not stubbed or deleted)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_generation_step":
            meaningful = 0
            for stmt in ast.walk(node):
                if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.If, ast.For,
                                     ast.While, ast.With, ast.Return, ast.Expr)):
                    if isinstance(stmt, ast.Expr) and isinstance(
                        stmt.value, ast.Constant
                    ):
                        continue
                    meaningful += 1
            assert meaningful >= 5, (
                f"_generation_step has only {meaningful} statements — likely stubbed"
            )
            return
    raise AssertionError("_generation_step not found in source")


# [static] pass_to_pass
def test_no_wildcard_imports():
    """No wildcard imports in the modified file."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names and node.names[0].name == "*":
            raise AssertionError(f"Wildcard import from {node.module}")


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — repo coding standards
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass
def test_no_bare_type_ignore():
    """Any # type: ignore must include a specific error code."""
    import re

    source = Path(TARGET).read_text()
    bare_pattern = re.compile(r"#\s*type:\s*ignore\s*(?:\s*#|$)")
    for i, line in enumerate(source.splitlines(), 1):
        if bare_pattern.search(line):
            # Check it doesn't have a bracketed code after it
            if not re.search(r"#\s*type:\s*ignore\[", line):
                raise AssertionError(
                    f"Line {i}: bare '# type: ignore' without error code: {line.strip()}"
                )


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:192-193 @ e5ad3946209fb96db5e9965b3eb67d69cc3749e0
def test_no_getattr_torch_dynamic_backend():
    """Do not use getattr(torch, 'backend') for dynamic device backends; use type guards."""
    import re

    source = Path(TARGET).read_text()
    # Backends that must be accessed via type guards, not getattr(torch, ...)
    dynamic_backends = {"npu", "xpu", "hpu", "musa", "mlu", "neuron", "compiler"}
    pattern = re.compile(r'getattr\s*\(\s*torch\s*,\s*["\'](\w+)["\']')
    for i, line in enumerate(source.splitlines(), 1):
        m = pattern.search(line)
        if m and m.group(1) in dynamic_backends:
            raise AssertionError(
                f"Line {i}: use a TypeGuard function instead of "
                f"getattr(torch, {m.group(1)!r}): {line.strip()}"
            )


# [agent_config] pass_to_pass
def test_no_assert_for_type_narrowing():
    """Do not use assert for type narrowing (e.g. assert x is not None)."""
    import re

    source = Path(TARGET).read_text()
    # Match assert patterns commonly used for type narrowing:
    # assert x is not None, assert isinstance(x, ...), assert x is None
    narrowing_patterns = [
        re.compile(r"^\s*assert\s+\w+\s+is\s+not\s+None\b"),
        re.compile(r"^\s*assert\s+\w+\s+is\s+None\b"),
        re.compile(r"^\s*assert\s+isinstance\("),
    ]
    for i, line in enumerate(source.splitlines(), 1):
        for pat in narrowing_patterns:
            if pat.search(line):
                raise AssertionError(
                    f"Line {i}: assert used for type narrowing (use 'if ...: raise' instead): {line.strip()}"
                )
