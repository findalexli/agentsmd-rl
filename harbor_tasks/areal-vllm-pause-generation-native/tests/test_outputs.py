"""
Task: areal-vllm-pause-generation-native
Repo: inclusionAI/AReaL @ 45e805ba8d274ec2c3cbb0699658449c2c6e163a
PR:   1091

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Behavioral test helper — written to repo dir so subprocess scripts can import it.
# Extracts async endpoint functions from source via AST, executes them with
# mocked engine clients, and tracks pause/rpc/resume call ordering.
# ---------------------------------------------------------------------------

_HELPER_CODE = '''\
import ast
import asyncio
from unittest.mock import AsyncMock, MagicMock

FILE = "/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py"


def extract_func(func_name):
    """Extract an async function from source, exec it with stubs, return (callable, ast_node)."""
    source = open(FILE).read()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            func_node = node
            break

    assert func_node is not None, f"{func_name} not found in {FILE}"

    lines = source.splitlines(keepends=True)
    func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

    ns = dict(
        __builtins__=__builtins__,
        logger=MagicMock(),
        build_response=lambda x: x,
        to_json_response=lambda *a, **kw: dict(ok=True),
        _generation_run_event=MagicMock(),
        _register_runtime_lora_name=lambda *a, **kw: None,
        asyncio=asyncio,
    )
    for tname in [
        "UpdateWeightsRequest", "UpdateWeightsRequestLora",
        "UpdateGroupRequest", "UpdateWeightsFromXcclRequest",
        "UpdateWeightsFromXcclRequestLora", "Request",
    ]:
        ns[tname] = MagicMock()

    exec(compile(func_src, FILE, "exec"), ns)
    return ns[func_name], func_node


def make_tracked_client(rpc_raises=False):
    """Create an AsyncMock engine client that logs pause/rpc/resume call order."""
    client = AsyncMock()
    call_log = []

    async def _pause(*a, **kw):
        call_log.append("pause")

    async def _resume(*a, **kw):
        call_log.append("resume")

    async def _rpc(*a, **kw):
        call_log.append("rpc")
        if rpc_raises:
            raise RuntimeError("simulated RPC failure")
        return [(True, "ok")]

    client.pause_generation.side_effect = _pause
    client.resume_generation.side_effect = _resume
    client.collective_rpc.side_effect = _rpc
    return client, call_log


def invoke(func, func_node, client, catch_errors=False):
    """Call extracted async endpoint function with mock request objects."""
    raw_request = MagicMock()
    raw_request.app.state.engine_client = client
    request = MagicMock()
    request.model_path = "/test/model"
    request.lora_model_path = "/test/lora"
    request.lora_name = "test_lora"
    request.lora_int_id = 1
    request.base_model_name = "base_model"

    nparams = len(func_node.args.args)
    try:
        if nparams >= 2:
            return asyncio.run(func(request, raw_request))
        else:
            return asyncio.run(func(raw_request))
    except Exception:
        if not catch_errors:
            raise
'''

_HELPER_PATH = Path(REPO) / "_eval_behavioral_helper.py"


@pytest.fixture(autouse=True, scope="session")
def _write_behavioral_helper():
    """Write shared helper module to repo directory for subprocess import."""
    _HELPER_PATH.write_text(_HELPER_CODE)
    yield
    _HELPER_PATH.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified file must parse without errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# Each test extracts the actual async endpoint function from source, executes
# it in an isolated subprocess with mocked engine clients, and verifies the
# call pattern (pause -> rpc -> resume).
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
    r = _run_python(f"""
        import sys
        from _eval_behavioral_helper import extract_func, make_tracked_client, invoke

        func, node = extract_func("{func_name}")
        client, log = make_tracked_client()
        invoke(func, node, client)

        if log != ["pause", "rpc", "resume"]:
            print("FAIL: expected [pause, rpc, resume], got " + str(log), file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Call ordering failed for {func_name}: {r.stderr}"
    assert "PASS" in r.stdout


@pytest.mark.parametrize("func_name", WEIGHT_UPDATE_ENDPOINTS)
def test_weight_update_pause_kwargs(func_name):
    """pause_generation must be called with wait_for_inflight_requests=False, clear_cache=True."""
    r = _run_python(f"""
        import sys
        from _eval_behavioral_helper import extract_func, make_tracked_client, invoke

        func, node = extract_func("{func_name}")
        client, _ = make_tracked_client()
        invoke(func, node, client)

        client.pause_generation.assert_called_once()
        _, kwargs = client.pause_generation.call_args
        if kwargs.get("wait_for_inflight_requests") is not False:
            print("FAIL: wait_for_inflight_requests should be False, got " + repr(kwargs), file=sys.stderr)
            sys.exit(1)
        if kwargs.get("clear_cache") is not True:
            print("FAIL: clear_cache should be True, got " + repr(kwargs), file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Pause kwargs failed for {func_name}: {r.stderr}"
    assert "PASS" in r.stdout


@pytest.mark.parametrize("func_name", WEIGHT_UPDATE_ENDPOINTS)
def test_weight_update_error_resilience(func_name):
    """resume_generation must be called even when collective_rpc raises."""
    r = _run_python(f"""
        import sys
        from _eval_behavioral_helper import extract_func, make_tracked_client, invoke

        func, node = extract_func("{func_name}")
        client, log = make_tracked_client(rpc_raises=True)
        invoke(func, node, client, catch_errors=True)

        if "pause" not in log:
            print("FAIL: pause_generation NOT called before RPC attempt", file=sys.stderr)
            sys.exit(1)
        if "resume" not in log:
            print("FAIL: resume_generation NOT called after RPC failure", file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Error resilience failed for {func_name}: {r.stderr}"
    assert "PASS" in r.stdout


def test_pause_endpoint_uses_native_api():
    """areal_pause_generation must call llm.pause_generation, not abort_all_reqs."""
    r = _run_python("""
        import sys, asyncio
        from unittest.mock import AsyncMock, MagicMock
        from _eval_behavioral_helper import extract_func

        func, _ = extract_func("areal_pause_generation")

        client = AsyncMock()
        called = []
        async def _pause(*a, **kw):
            called.append("pause")
        client.pause_generation.side_effect = _pause
        client.engine_core = MagicMock()
        client.engine_core.call_utility_async = AsyncMock()

        raw_request = MagicMock()
        raw_request.app.state.engine_client = client
        asyncio.run(func(raw_request))

        if "pause" not in called:
            print("FAIL: pause_generation() never called", file=sys.stderr)
            sys.exit(1)
        if client.engine_core.call_utility_async.called:
            print("FAIL: still calls abort via engine_core.call_utility_async", file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_continue_endpoint_calls_resume():
    """areal_continue_generation must call llm.resume_generation."""
    r = _run_python("""
        import sys, asyncio
        from unittest.mock import AsyncMock, MagicMock
        from _eval_behavioral_helper import extract_func

        func, _ = extract_func("areal_continue_generation")

        client = AsyncMock()
        called = []
        async def _resume(*a, **kw):
            called.append("resume")
        client.resume_generation.side_effect = _resume

        raw_request = MagicMock()
        raw_request.app.state.engine_client = client
        asyncio.run(func(raw_request))

        if "resume" not in called:
            print("FAIL: resume_generation() never called", file=sys.stderr)
            sys.exit(1)
        print("PASS")
    """)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess structural checks
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
