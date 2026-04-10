"""
Task: sglang-pcg-qo-indptr-padding
Repo: sgl-project/sglang @ efebcab43ed851405bd41cfdf206245945dbb8ee
PR:   #21452

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"

CTX_MGR = f"{REPO}/python/sglang/srt/compilation/piecewise_context_manager.py"
FLASH_BE = f"{REPO}/python/sglang/srt/layers/attention/flashinfer_backend.py"
PCG_RUN = f"{REPO}/python/sglang/srt/model_executor/piecewise_cuda_graph_runner.py"


def _run_ctx_mgr_test(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Python code that tests piecewise_context_manager.py with mocked torch."""
    script = Path(REPO) / "_eval_ctx_mgr_test.py"
    setup = (
        "import sys, types\n"
        "\n"
        "REPO = " + repr(REPO) + "\n"
        "\n"
        "# Mock torch (no GPU needed)\n"
        "mock_torch = types.ModuleType('torch')\n"
        "mock_cuda = types.ModuleType('torch.cuda')\n"
        "class _MockStream: pass\n"
        "mock_cuda.Stream = _MockStream\n"
        "mock_torch.cuda = mock_cuda\n"
        "sys.modules['torch'] = mock_torch\n"
        "sys.modules['torch.cuda'] = mock_cuda\n"
        "\n"
        "for pkg in ['sglang', 'sglang.srt', 'sglang.srt.compilation', 'sglang.srt.model_executor']:\n"
        "    m = types.ModuleType(pkg)\n"
        "    m.__path__ = [REPO + '/python/' + pkg.replace('.', '/')]\n"
        "    sys.modules[pkg] = m\n"
        "\n"
        "import importlib.util\n"
        "spec = importlib.util.spec_from_file_location(\n"
        "    'sglang.srt.compilation.piecewise_context_manager',\n"
        "    REPO + '/python/sglang/srt/compilation/piecewise_context_manager.py',\n"
        ")\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "sys.modules[spec.name] = mod\n"
        "spec.loader.exec_module(mod)\n"
    )
    script.write_text(setup + "\n" + code)
    try:
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """All three modified files must parse without syntax errors."""
    for path in [CTX_MGR, FLASH_BE, PCG_RUN]:
        src = Path(path).read_text()
        ast.parse(src)  # raises SyntaxError on failure


# [repo_tests] pass_to_pass
def test_repo_python_ast():
    """Repo CI: All modified files pass Python AST validation (check-ast)."""
    for path in [CTX_MGR, FLASH_BE, PCG_RUN]:
        r = subprocess.run(
            ["python3", "-m", "py_compile", path],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"AST check failed for {path}: {r.stderr}"


# [static] pass_to_pass
def test_repo_no_trailing_whitespace():
    """Modified files have no trailing whitespace (static check)."""
    for path in [CTX_MGR, FLASH_BE, PCG_RUN]:
        content = Path(path).read_text()
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            assert not line.endswith(" "), f"{path}:{i} has trailing whitespace"
            assert not line.endswith("\t"), f"{path}:{i} has trailing tabs"


# [static] pass_to_pass
def test_repo_no_debug_statements():
    """Modified files have no debug statements (static check)."""
    debug_patterns = ["import pdb", "from pdb import", "breakpoint()", "pdb.set_trace"]
    for path in [CTX_MGR, FLASH_BE, PCG_RUN]:
        content = Path(path).read_text()
        for pattern in debug_patterns:
            assert pattern not in content, f"{path} contains debug statement: {pattern}"


# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Repo CI: Ruff linter passes on modified files (F401, F821)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"
    r = subprocess.run(
        ["ruff", "check", "--select=F401,F821", CTX_MGR, FLASH_BE, PCG_RUN],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo CI: Import sorting check passes on modified files."""
    r = subprocess.run(
        ["pip", "install", "isort", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr}"
    r = subprocess.run(
        ["isort", "--check-only", CTX_MGR, FLASH_BE, PCG_RUN],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black():
    """Repo CI: Black formatting check passes on modified files."""
    r = subprocess.run(
        ["pip", "install", "black", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr}"
    r = subprocess.run(
        ["black", "--check", CTX_MGR, FLASH_BE, PCG_RUN],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_forward_context_has_num_tokens():
    """ForwardContext must have a num_tokens attribute; set_forward_context must accept it."""
    r = _run_ctx_mgr_test(
        "import inspect\n"
        "\n"
        "FC = mod.ForwardContext\n"
        "sfc = mod.set_forward_context\n"
        "\n"
        "# ForwardContext instances must have num_tokens\n"
        "fc = FC()\n"
        'assert hasattr(fc, "num_tokens"), "ForwardContext missing num_tokens attribute"\n'
        "\n"
        "# set_forward_context must accept num_tokens keyword\n"
        "sig = inspect.signature(sfc)\n"
        'assert "num_tokens" in sig.parameters, "set_forward_context does not accept num_tokens"\n'
        'print("PASS")\n'
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_num_tokens_propagation():
    """num_tokens value propagates through set_forward_context and varies with input."""
    r = _run_ctx_mgr_test(
        "sfc = mod.set_forward_context\n"
        "gfc = mod.get_forward_context\n"
        "\n"
        "# Propagate num_tokens=42\n"
        "with sfc(None, None, None, [], [], num_tokens=42):\n"
        "    fwd = gfc()\n"
        '    assert fwd is not None, "get_forward_context() returned None inside context"\n'
        '    assert fwd.num_tokens == 42, f"expected 42, got {fwd.num_tokens}"\n'
        "\n"
        "# Different value propagates (not hardcoded)\n"
        "with sfc(None, None, None, [], [], num_tokens=256):\n"
        "    fwd2 = gfc()\n"
        '    assert fwd2.num_tokens == 256, f"expected 256, got {fwd2.num_tokens}"\n'
        "\n"
        "# Default (no num_tokens) gives None\n"
        "with sfc(None, None, None, [], []):\n"
        "    fwd3 = gfc()\n"
        '    assert fwd3.num_tokens is None, f"default should be None, got {fwd3.num_tokens}"\n'
        "\n"
        'print("PASS")\n'
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_replay_num_tokens_and_ordering():
    # AST-only: piecewise_cuda_graph_runner.py imports torch, bisect,
    # CUDA graph APIs, ModelRunner, ForwardBatch -- cannot be imported without GPU.
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
    # AST-only: flashinfer_backend.py imports torch, flashinfer C++ bindings,
    # ModelRunner, and dozens of sglang internals -- cannot be imported without GPU.
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
# Pass-to-pass -- regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_context_manager_api():
    """Original ForwardContext attributes and context manager preserved."""
    r = _run_ctx_mgr_test(
        "FC = mod.ForwardContext\n"
        "sfc = mod.set_forward_context\n"
        "gfc = mod.get_forward_context\n"
        "\n"
        "# Required exports exist\n"
        "for name in ['set_forward_context', 'get_forward_context',\n"
        "             'is_in_piecewise_cuda_graph', 'enable_piecewise_cuda_graph']:\n"
        '    assert getattr(mod, name, None) is not None, f"missing export: {name}"\n'
        "\n"
        "# ForwardContext retains original attributes\n"
        "fc = FC()\n"
        "for attr in ['forward_batch', 'quant_config', 'moe_layers', 'moe_fusions']:\n"
        '    assert hasattr(fc, attr), f"ForwardContext missing attr: {attr}"\n'
        "\n"
        "# get_forward_context returns None outside any context\n"
        'assert gfc() is None, "should return None outside context"\n'
        "\n"
        "# Context manager round-trip (without num_tokens, backwards compat)\n"
        "with sfc(None, None, None, [], []):\n"
        "    inside = gfc()\n"
        '    assert inside is not None, "returned None inside context"\n'
        '    assert hasattr(inside, "forward_batch"), "context missing forward_batch"\n'
        'assert gfc() is None, "not cleared after exiting"\n'
        "\n"
        'print("PASS")\n'
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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
