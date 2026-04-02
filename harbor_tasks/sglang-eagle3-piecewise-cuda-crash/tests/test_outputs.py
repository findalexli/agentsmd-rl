"""
Task: sglang-eagle3-piecewise-cuda-crash
Repo: sgl-project/sglang @ aa9177152ec7057dff4fd8f210dd6a42e96dac5d
PR:   21565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
import types
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/srt/model_executor/model_runner.py"


def _extract_func(name="init_piecewise_cuda_graphs"):
    """Extract a function's source from the target file by AST lookup."""
    # AST-only because: module imports torch, triton, CUDA — cannot import
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            lines = source.splitlines(keepends=True)
            return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
    raise AssertionError(f"{name} not found in {TARGET}")


class _MockLogger:
    def __init__(self):
        self.warnings = []

    def error(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def warning(self, msg, *a, **kw): self.warnings.append(msg)
    def warning_once(self, msg, *a, **kw): self.warnings.append(msg)
    def debug(self, *a, **kw): pass


def _run_func(mock_self, resolve_fn=None):
    """Compile and execute init_piecewise_cuda_graphs with the given mock self."""
    func_src = _extract_func()
    mock_logger = _MockLogger()
    resolve_calls = []

    def default_resolve(m):
        resolve_calls.append(True)
        return m.model

    exec_globals = {
        "resolve_language_model": resolve_fn or default_resolve,
        "logger": mock_logger,
        "__builtins__": __builtins__,
    }
    exec(func_src, exec_globals)
    exec_globals["init_piecewise_cuda_graphs"](mock_self)
    return resolve_calls, mock_logger


def _make_layerless_model(extra_attr=None):
    """Model WITHOUT 'layers' — simulates eagle3 draft model."""
    class Inner:
        pass

    class Model:
        def __init__(self):
            self.model = Inner()

    m = Model()
    if extra_attr:
        setattr(m.model, extra_attr[0], extra_attr[1])
    return m


def _make_layered_model(n_layers=3):
    """Model WITH standard 'layers' attribute."""
    class FakeLayer:
        def __init__(self):
            self.self_attn = types.SimpleNamespace(attn=object())

    class Inner:
        def __init__(self):
            self.layers = [FakeLayer() for _ in range(n_layers)]

    class Model:
        def __init__(self):
            self.model = Inner()

    return Model()


class _ServerArgs:
    disable_piecewise_cuda_graph = False
    piecewise_cuda_graph_tokens = [128, 256]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_crash_missing_layers():
    """Model without 'layers' attr must not raise AttributeError."""
    # Test with 3 different layerless model variants to prevent hardcoding
    variants = [
        _make_layerless_model(),                              # bare inner model
        _make_layerless_model(("midlayer", object())),        # eagle3-style single midlayer
        _make_layerless_model(("blocks", [1, 2, 3])),         # alternative block naming
    ]
    for i, model in enumerate(variants):
        mock_self = types.SimpleNamespace(
            model=model,
            server_args=_ServerArgs(),
            attention_layers=[],
            moe_layers=[],
            moe_fusions=[],
        )
        try:
            resolve_calls, _ = _run_func(mock_self)
        except AttributeError as e:
            if "layers" in str(e):
                raise AssertionError(f"Variant {i}: crashed on missing 'layers': {e}") from e
            # Other AttributeErrors from downstream CUDA code are OK
            resolve_calls = [True]
        except Exception:
            # Other errors (e.g. CUDA stubs missing) are acceptable —
            # key is no AttributeError on 'layers'
            resolve_calls = [True]

        assert resolve_calls, f"Variant {i}: resolve_language_model never called — function is likely stubbed"


# [pr_diff] fail_to_pass
def test_no_spurious_extraction_layerless():
    """Layerless model must not produce populated attention_layers."""
    SENTINEL = object()
    mock_self = types.SimpleNamespace(
        model=_make_layerless_model(),
        server_args=_ServerArgs(),
        attention_layers=SENTINEL,
        moe_layers=SENTINEL,
        moe_fusions=SENTINEL,
    )
    try:
        resolve_calls, _ = _run_func(mock_self)
    except AttributeError as e:
        if "layers" in str(e):
            raise AssertionError(f"Crashed on missing 'layers': {e}") from e
        resolve_calls = [True]
    except Exception:
        resolve_calls = [True]

    assert resolve_calls, "resolve_language_model never called — function is likely stubbed"

    attn = mock_self.attention_layers
    # Valid: SENTINEL (early return), None, or empty list
    # Invalid: list with actual layer objects
    if isinstance(attn, list) and len(attn) > 0:
        raise AssertionError(
            f"attention_layers has {len(attn)} entries but model has no layers"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_layers_extracted_standard_model():
    """Model WITH layers must still get attention layers extracted."""
    # Test with multiple layer counts to prevent hardcoding
    for n_layers in (2, 4, 6):
        mock_self = types.SimpleNamespace(
            model=_make_layered_model(n_layers=n_layers),
            server_args=_ServerArgs(),
            attention_layers=None,
            moe_layers=None,
            moe_fusions=None,
        )
        try:
            _run_func(mock_self)
        except Exception:
            pass  # May fail on downstream CUDA parts; we check layer extraction

        attn = mock_self.attention_layers
        assert attn is not None, (
            f"n_layers={n_layers}: Model with layers did not proceed to layer extraction"
        )
        assert isinstance(attn, list), (
            f"n_layers={n_layers}: attention_layers should be a list, got {type(attn)}"
        )


# [static] pass_to_pass
def test_not_stub():
    """init_piecewise_cuda_graphs must have real logic, not be stubbed out."""
    # AST-only because: module imports torch, triton, CUDA — cannot import
    source = Path(TARGET).read_text()

    for sym in ["init_piecewise_cuda_graphs", "resolve_language_model",
                "language_model", "attention_layers", "ModelRunner"]:
        assert sym in source, f"File missing expected symbol: {sym}"

    assert len(source.splitlines()) >= 500, "File too short — looks like a stub"

    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "init_piecewise_cuda_graphs":
            meaningful = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                      ast.For, ast.While, ast.If, ast.With,
                                      ast.Try, ast.Return, ast.Call))
            )
            assert meaningful >= 5, (
                f"Function has only {meaningful} meaningful statements — looks stubbed"
            )
            return

    raise AssertionError("init_piecewise_cuda_graphs not found")
