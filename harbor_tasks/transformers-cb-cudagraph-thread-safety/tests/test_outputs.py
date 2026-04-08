"""
Task: transformers-cb-cudagraph-thread-safety
Repo: huggingface/transformers @ e5ad3946209fb96db5e9965b3eb67d69cc3749e0
PR:   44924

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/transformers/generation/continuous_batching/continuous_api.py"

# ---------------------------------------------------------------------------
# Behavioral subprocess script — mocks torch, extracts _generation_step via
# AST, executes it, and reports the kwargs passed to torch.cuda.graph().
# ---------------------------------------------------------------------------

_BEHAVIORAL_SCRIPT = textwrap.dedent("""\
    import ast, sys, types, textwrap, json
    import unittest.mock as mock
    from pathlib import Path

    TARGET = "/repo/src/transformers/generation/continuous_batching/continuous_api.py"

    # --- Build fake torch that records cuda.graph() calls ---
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
    cuda_mod.stream = lambda *a, **kw: _FakeGraphCtx()
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

    sys.modules["torch"] = torch_mod
    sys.modules["torch.cuda"] = cuda_mod
    sys.modules["torch.nn"] = nn_mod

    # --- Extract _generation_step from source via AST ---
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    gen_step = None

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
            gen_step = ns["_generation_step"]
            break

    if gen_step is None:
        print(json.dumps({"error": "_generation_step not found"}))
        sys.exit(1)

    # --- Invoke with mocks that trigger the graph-creation branch ---
    mock_self = mock.MagicMock()
    mock_self.use_cuda_graph = True
    mock_self.graph_pool = mock.MagicMock()
    mock_self.inputs_and_outputs.get_graph.return_value = None
    mock_self.inputs_and_outputs.compute_stream = mock.MagicMock()
    mock_self.inputs_and_outputs.get_cb_kwargs.return_value = (
        mock.MagicMock(), mock.MagicMock(), mock.MagicMock()
    )
    try:
        gen_step(mock_self, mock.MagicMock(), mock.MagicMock(), True)
    except Exception:
        pass  # downstream mock gaps are fine; we only need the cuda.graph call

    # --- Report captured kwargs ---
    if not captured_graph_calls:
        print(json.dumps({"error": "torch.cuda.graph() was never called"}))
        sys.exit(1)

    kwargs = captured_graph_calls[0]["kwargs"]
    print(json.dumps({"capture_error_mode": kwargs.get("capture_error_mode")}))
""")


def _get_capture_kwargs() -> dict:
    """Run behavioral script in subprocess, return captured kwargs from torch.cuda.graph()."""
    r = subprocess.run(
        ["python3", "-c", _BEHAVIORAL_SCRIPT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Behavioral script failed: {r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_capture_error_mode_thread_safe():
    """torch.cuda.graph() must be called with a non-global capture_error_mode."""
    result = _get_capture_kwargs()
    mode = result["capture_error_mode"]
    assert mode is not None, "capture_error_mode not passed to torch.cuda.graph()"
    assert mode != "global", f"capture_error_mode={mode!r} is not thread-safe"


# [pr_diff] fail_to_pass
def test_capture_error_mode_recognized_safe():
    """capture_error_mode must be a recognized thread-safe mode (thread_local or relaxed)."""
    THREAD_SAFE_MODES = {"thread_local", "relaxed"}
    result = _get_capture_kwargs()
    mode = result["capture_error_mode"]
    assert isinstance(mode, str), (
        f"capture_error_mode should be a string, got {type(mode).__name__}"
    )
    assert mode in THREAD_SAFE_MODES, (
        f"capture_error_mode={mode!r} is not a recognized thread-safe mode "
        f"(expected one of {THREAD_SAFE_MODES})"
    )


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
    source = Path(TARGET).read_text()
    bare_pattern = re.compile(r"#\s*type:\s*ignore\s*(?:\s*#|$)")
    for i, line in enumerate(source.splitlines(), 1):
        if bare_pattern.search(line):
            if not re.search(r"#\s*type:\s*ignore\[", line):
                raise AssertionError(
                    f"Line {i}: bare '# type: ignore' without error code: {line.strip()}"
                )


# [agent_config] pass_to_pass
def test_no_getattr_torch_dynamic_backend():
    """Do not use getattr(torch, 'backend') for dynamic device backends; use type guards."""
    source = Path(TARGET).read_text()
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
    source = Path(TARGET).read_text()
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
