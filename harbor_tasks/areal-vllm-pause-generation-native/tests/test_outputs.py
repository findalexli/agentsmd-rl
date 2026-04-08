"""
Task: areal-vllm-pause-generation-native
Repo: inclusionAI/AReaL @ 45e805ba8d274ec2c3cbb0699658449c2c6e163a
PR:   1091

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import subprocess
import textwrap
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

REPO = "/workspace/AReaL"
FILE = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess in the repo environment."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(textwrap.dedent(code))
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _extract_async_func(func_name: str):
    """Extract async function from source, exec with mocks, return callable + AST node."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            func_node = node
            break

    assert func_node is not None, f"async function '{func_name}' not found"

    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

    ns = {
        "__builtins__": __builtins__,
        "logger": MagicMock(),
        "build_response": lambda x: x,
        "to_json_response": lambda *a, **kw: {"ok": True},
        "_generation_run_event": MagicMock(),
        "_register_runtime_lora_name": lambda *a, **kw: None,
        "asyncio": asyncio,
    }
    for tname in [
        "UpdateWeightsRequest", "UpdateWeightsRequestLora",
        "UpdateGroupRequest", "UpdateWeightsFromXcclRequest",
        "UpdateWeightsFromXcclRequestLora", "Request",
    ]:
        ns[tname] = MagicMock()

    exec(compile(func_src, FILE, "exec"), ns)
    func = ns[func_name]
    assert callable(func), f"{func_name} not callable after exec"
    return func, func_node


def _make_tracked_client():
    """Create AsyncMock engine client that logs pause/rpc/resume calls."""
    client = AsyncMock()
    call_log = []

    async def _pause(*a, **kw):
        call_log.append("pause")

    async def _resume(*a, **kw):
        call_log.append("resume")

    async def _rpc(*a, **kw):
        call_log.append("rpc")
        return [(True, "ok")]

    client.pause_generation.side_effect = _pause
    client.resume_generation.side_effect = _resume
    client.collective_rpc.side_effect = _rpc
    return client, call_log


def _invoke(func, func_node, client):
    """Call extracted function with mock raw_request wired to client."""
    raw_request = MagicMock()
    raw_request.app.state.engine_client = client
    request = MagicMock()
    request.model_path = "/test/model"
    request.lora_model_path = "/test/lora"
    request.lora_name = "test_lora"
    request.lora_int_id = 1
    request.base_model_name = "base_model"

    nparams = len(func_node.args.args)
    if nparams >= 2:
        return asyncio.run(func(request, raw_request))
    else:
        return asyncio.run(func(raw_request))


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must parse without errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests (exec-based)
# ---------------------------------------------------------------------------

WEIGHT_UPDATE_ENDPOINTS = [
    "areal_update_weight",
    "areal_update_weight_lora",
    "areal_update_weight_xccl",
    "areal_update_weight_lora_xccl",
]


@pytest.mark.parametrize("func_name", WEIGHT_UPDATE_ENDPOINTS)
def test_weight_update_call_ordering(func_name):
    """Weight update must call pause_generation -> collective_rpc -> resume_generation."""
    func, func_node = _extract_async_func(func_name)
    client, call_log = _make_tracked_client()
    _invoke(func, func_node, client)

    assert "pause" in call_log, "pause_generation() never called"
    assert "rpc" in call_log, "collective_rpc() never called"
    assert "resume" in call_log, "resume_generation() never called"
    assert call_log.index("pause") < call_log.index("rpc"), (
        f"pause must precede rpc: {call_log}"
    )
    assert call_log.index("rpc") < call_log.index("resume"), (
        f"rpc must precede resume: {call_log}"
    )


@pytest.mark.parametrize("func_name", WEIGHT_UPDATE_ENDPOINTS)
def test_weight_update_pause_kwargs(func_name):
    """pause_generation must be called with wait_for_inflight_requests=False, clear_cache=True."""
    func, func_node = _extract_async_func(func_name)
    client, _ = _make_tracked_client()
    _invoke(func, func_node, client)

    client.pause_generation.assert_called_once()
    _, kwargs = client.pause_generation.call_args
    assert kwargs.get("wait_for_inflight_requests") is False, (
        f"Expected wait_for_inflight_requests=False, got {kwargs}"
    )
    assert kwargs.get("clear_cache") is True, (
        f"Expected clear_cache=True, got {kwargs}"
    )


@pytest.mark.parametrize("func_name", WEIGHT_UPDATE_ENDPOINTS)
def test_weight_update_error_resilience(func_name):
    """resume_generation must be called even when collective_rpc raises."""
    func, func_node = _extract_async_func(func_name)
    client, call_log = _make_tracked_client()

    async def _rpc_raise(*a, **kw):
        call_log.append("rpc")
        raise RuntimeError("simulated RPC failure")

    client.collective_rpc.side_effect = _rpc_raise

    raw_request = MagicMock()
    raw_request.app.state.engine_client = client
    request = MagicMock()

    nparams = len(func_node.args.args)
    try:
        if nparams >= 2:
            asyncio.run(func(request, raw_request))
        else:
            asyncio.run(func(raw_request))
    except RuntimeError:
        pass

    assert "pause" in call_log, "pause_generation NOT called before RPC attempt"
    assert "resume" in call_log, "resume_generation NOT called after RPC failure"


def test_pause_endpoint_uses_native_api():
    """areal_pause_generation must call llm.pause_generation, not abort_all_reqs."""
    func, _ = _extract_async_func("areal_pause_generation")
    client, call_log = _make_tracked_client()
    client.engine_core = MagicMock()
    client.engine_core.call_utility_async = AsyncMock()

    raw_request = MagicMock()
    raw_request.app.state.engine_client = client
    asyncio.run(func(raw_request))

    assert "pause" in call_log, "pause_generation() never called"
    assert not client.engine_core.call_utility_async.called, (
        "still calls abort via engine_core.call_utility_async"
    )


def test_continue_endpoint_calls_resume():
    """areal_continue_generation must call llm.resume_generation."""
    func, _ = _extract_async_func("areal_continue_generation")
    client = AsyncMock()
    resume_called = []

    async def _resume(*a, **kw):
        resume_called.append(True)

    client.resume_generation.side_effect = _resume

    raw_request = MagicMock()
    raw_request.app.state.engine_client = client
    asyncio.run(func(raw_request))

    assert resume_called, "resume_generation() never called"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-based structural checks
# ---------------------------------------------------------------------------

def test_no_monkey_patching():
    """setattr(EngineCore, ...) and hook() function must be removed."""
    r = _run_python(f"""
        import ast, sys
        source = open("{FILE}").read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "setattr"
                    and node.args
                    and isinstance(node.args[0], ast.Name)
                    and node.args[0].id == "EngineCore"):
                print("FAIL: setattr(EngineCore) found", file=sys.stderr)
                sys.exit(1)
            if isinstance(node, ast.FunctionDef) and node.name == "hook":
                print("FAIL: hook() defined", file=sys.stderr)
                sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Monkey-patching still present: {r.stderr}"
    assert "PASS" in r.stdout


def test_no_abort_all_reqs_function():
    """Standalone abort_all_reqs function must be removed."""
    r = _run_python(f"""
        import ast, sys
        source = open("{FILE}").read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "abort_all_reqs":
                    print("FAIL: abort_all_reqs defined", file=sys.stderr)
                    sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"abort_all_reqs still defined: {r.stderr}"
    assert "PASS" in r.stdout


def test_removed_vllm_internals_imports():
    """Imports of EngineCore and related vllm.v1 internals must be removed."""
    r = _run_python(f"""
        import ast, sys
        source = open("{FILE}").read()
        tree = ast.parse(source)
        removed = {{"EngineCore", "EngineCoreOutput", "EngineCoreOutputs",
                    "FinishReason", "RequestStatus", "LoRARequestStates"}}
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    actual = alias.asname or alias.name
                    if actual in removed:
                        found.add(actual)
        if found:
            print(f"FAIL: still imported: {{found}}", file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"vllm internals still imported: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

def test_routes_preserved():
    """All original API route paths must still be declared."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    route_strings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    for arg in dec.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            route_strings.add(arg.value)

    required = {
        "/areal_update_weights", "/areal_update_weights_lora",
        "/areal_update_weights_xccl", "/areal_update_weights_lora_xccl",
        "/areal_init_weights_update_group",
        "/areal_set_update_weight_meta", "/areal_set_update_weight_meta_lora",
        "/areal_pause_generation", "/areal_continue_generation",
        "/v1/completions",
    }
    missing = required - route_strings
    assert not missing, f"Missing routes: {missing}"


def test_request_models_preserved():
    """Pydantic request model classes must still be defined."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    required = {
        "UpdateWeightsRequest", "UpdateWeightsRequestLora",
        "UpdateGroupRequest", "UpdateWeightsFromXcclRequest",
        "UpdateWeightsFromXcclRequestLora",
    }
    found = {
        n.name for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef) and n.name in required
    }
    missing = required - found
    assert not missing, f"Missing model classes: {missing}"


# ---------------------------------------------------------------------------
# Agent config (pass_to_pass)
# ---------------------------------------------------------------------------

def test_no_wildcard_imports():
    """No wildcard imports (from x import *)."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    pytest.fail(f"Wildcard import: from {node.module} import *")


def test_endpoint_functions_typed():
    """Async endpoint functions have explicit type annotations on all parameters."""
    source = Path(FILE).read_text()
    tree = ast.parse(source)

    endpoint_names = {
        "areal_update_weight", "areal_update_weight_lora",
        "areal_update_weight_xccl", "areal_update_weight_lora_xccl",
        "areal_pause_generation", "areal_continue_generation",
    }

    untyped = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name in endpoint_names:
            for arg in node.args.args:
                if arg.annotation is None:
                    untyped.append(f"{node.name}:{arg.arg}")

    assert not untyped, f"Parameters missing type annotations: {untyped}"
