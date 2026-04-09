"""
Task: sglang-eagle3-piecewise-cuda-crash
Repo: sgl-project/sglang @ aa9177152ec7057dff4fd8f210dd6a42e96dac5d
PR:   21565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
import types
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = f"{REPO}/python/sglang/srt/model_executor/model_runner.py"


def _run_script(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python script to a temp file and execute it via subprocess."""
    script = Path(REPO) / "_eval_tmp_test.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# Shared harness code injected into subprocess scripts.
# Extracts init_piecewise_cuda_graphs via AST (cannot import module — needs CUDA)
# and executes it with mock objects.
_HARNESS = textwrap.dedent("""\
    import ast, textwrap, types, sys

    TARGET = "/workspace/sglang/python/sglang/srt/model_executor/model_runner.py"

    def extract_func(name="init_piecewise_cuda_graphs"):
        source = open(TARGET).read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
                lines = source.splitlines(keepends=True)
                return textwrap.dedent("".join(lines[node.lineno - 1 : node.end_lineno]))
        raise RuntimeError(f"{name} not found")

    class MockLogger:
        def __init__(self):
            self.warnings = []
        def error(self, *a, **kw): pass
        def info(self, *a, **kw): pass
        def warning(self, msg, *a, **kw): self.warnings.append(msg)
        def warning_once(self, msg, *a, **kw): self.warnings.append(msg)
        def debug(self, *a, **kw): pass

    class ServerArgs:
        disable_piecewise_cuda_graph = False
        piecewise_cuda_graph_tokens = [128, 256]

    def run_func(mock_self):
        func_src = extract_func()
        logger = MockLogger()
        exec_globals = {
            "resolve_language_model": lambda m: m.model,
            "logger": logger,
            "__builtins__": __builtins__,
        }
        exec(func_src, exec_globals)
        exec_globals["init_piecewise_cuda_graphs"](mock_self)
        return logger

    def make_layerless_model():
        class Inner: pass
        class Model:
            def __init__(self):
                self.model = Inner()
        return Model()

    def make_layered_model(n_layers=3):
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
""")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# [static] pass_to_pass — repo CI lint check
def test_repo_ruff_check():
    """Repo's ruff lint check passes (F401, F821) on target file (pass_to_pass)."""
    # Install ruff if not available
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "--select=F401,F821", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_crash_missing_layers():
    """Model without 'layers' attr must not raise AttributeError."""
    r = _run_script(_HARNESS + textwrap.dedent("""\
        # Test 3 layerless model variants to prevent hardcoding
        variants = [
            make_layerless_model(),                                    # bare
            make_layerless_model(),                                    # eagle3-style
            make_layerless_model(),                                    # alt naming
        ]
        # Add different attributes to variants to vary the models
        setattr(variants[1].model, "midlayer", object())
        setattr(variants[2].model, "blocks", [1, 2, 3])

        for i, model in enumerate(variants):
            mock_self = types.SimpleNamespace(
                model=model,
                server_args=ServerArgs(),
                attention_layers=[],
                moe_layers=[],
                moe_fusions=[],
            )
            try:
                run_func(mock_self)
            except AttributeError as e:
                if "layers" in str(e):
                    print(f"FAIL variant {i}: crashed on missing 'layers': {e}", file=sys.stderr)
                    sys.exit(1)
            except Exception:
                pass  # Other errors (e.g. CUDA stubs missing) are OK

        print("PASS")
    """))
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_no_spurious_extraction_layerless():
    """Layerless model must not produce populated attention_layers."""
    r = _run_script(_HARNESS + textwrap.dedent("""\
        SENTINEL = "SENTINEL_UNCHANGED"
        mock_self = types.SimpleNamespace(
            model=make_layerless_model(),
            server_args=ServerArgs(),
            attention_layers=SENTINEL,
            moe_layers=SENTINEL,
            moe_fusions=SENTINEL,
        )
        try:
            run_func(mock_self)
        except AttributeError as e:
            if "layers" in str(e):
                print(f"FAIL: crashed on missing 'layers': {e}", file=sys.stderr)
                sys.exit(1)
        except Exception:
            pass  # Other errors are OK

        attn = mock_self.attention_layers
        # Valid: SENTINEL (early return), None, or empty list
        # Invalid: list with actual layer objects
        if isinstance(attn, list) and len(attn) > 0:
            print(f"FAIL: attention_layers has {len(attn)} entries but model has no layers", file=sys.stderr)
            sys.exit(1)

        print("PASS")
    """))
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_layers_extracted_standard_model():
    """Model WITH layers must still get attention layers extracted."""
    r = _run_script(_HARNESS + textwrap.dedent("""\
        for n_layers in (2, 4, 6):
            mock_self = types.SimpleNamespace(
                model=make_layered_model(n_layers=n_layers),
                server_args=ServerArgs(),
                attention_layers=None,
                moe_layers=None,
                moe_fusions=None,
            )
            try:
                run_func(mock_self)
            except Exception:
                pass  # May fail on downstream CUDA parts; we check layer extraction

            attn = mock_self.attention_layers
            if attn is None:
                print(f"FAIL n_layers={n_layers}: attention_layers still None after execution", file=sys.stderr)
                sys.exit(1)
            if not isinstance(attn, list):
                print(f"FAIL n_layers={n_layers}: attention_layers is {type(attn)}, not list", file=sys.stderr)
                sys.exit(1)

        print("PASS")
    """))
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# [static] pass_to_pass
def test_not_stub():
    """init_piecewise_cuda_graphs must have real logic, not be stubbed out."""
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
