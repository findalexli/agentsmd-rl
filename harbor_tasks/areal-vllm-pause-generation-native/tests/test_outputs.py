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


def test_syntax_check():
    """Modified file must parse without errors."""
    source = Path(FILE).read_text()
    ast.parse(source)


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
# Repo CI/CD checks (pass_to_pass)
# ---------------------------------------------------------------------------

def test_repo_ruff_lint():
    """Repo's Python linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_import_sorting():
    """Repo's Python imports are properly sorted (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--select", "I", FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import sorting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_py_compile():
    """Modified file compiles to bytecode successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", FILE],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Repo's Python formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_python_syntax():
    """Modified file has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{FILE}').read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax error:\n{r.stderr[-500:]}"


def test_repo_trailing_whitespace():
    """Modified file has no trailing whitespace (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"grep -q '[[:space:]]$' '{FILE}' && exit 1 || exit 0"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Trailing whitespace found in {FILE}"


def test_repo_eof_newline():
    """Modified file ends with a newline (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"[ -z \"$(tail -c1 '{FILE}')\" ] && exit 0 || exit 1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"File {FILE} does not end with newline"


def test_repo_yaml_valid():
    """CI workflow YAML files are syntactically valid (pass_to_pass)."""
    import yaml
    workflows_dir = Path(REPO) / ".github" / "workflows"
    if not workflows_dir.exists():
        pytest.skip("No .github/workflows directory")
    for yaml_file in workflows_dir.glob("*.yml"):
        try:
            yaml.safe_load(yaml_file.read_text())
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in {yaml_file}: {e}")


def test_repo_pyproject_toml_valid():
    """pyproject.toml is syntactically valid (pass_to_pass)."""
    try:
        import tomllib
        tomllib.load((Path(REPO) / "pyproject.toml").open("rb"))
    except Exception:
        # Fallback for Python < 3.11
        try:
            import tomli
            tomli.load((Path(REPO) / "pyproject.toml").open("rb"))
        except Exception as e:
            pytest.skip(f"Cannot validate pyproject.toml: {e}")


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_install_test_set_up_python():
    """pass_to_pass | CI job 'Install test' → step 'Set up Python'"""
    pytest.skip("Requires uv + heavy GPU deps (torch, vllm) not available in Docker env")

def test_ci_install_test_verify_package_import():
    """pass_to_pass | CI job 'Install test' → step 'Verify package import'"""
    pytest.skip("Requires uv + heavy GPU deps (torch, vllm) not available in Docker env")

def test_ci_install_test_verify_core_modules_are_importable():
    """pass_to_pass | CI job 'Install test' → step 'Verify core modules are importable'"""
    pytest.skip("Requires uv + heavy GPU deps (torch, vllm) not available in Docker env")

def test_ci_install_test_build_wheel():
    """pass_to_pass | CI job 'Install test' → step 'Build wheel'"""
    pytest.skip("Requires uv + heavy GPU deps (torch, vllm) not available in Docker env")

def test_ci_install_test_verify_wheel_artifact():
    """pass_to_pass | CI job 'Install test' → step 'Verify wheel artifact'"""
    pytest.skip("Requires wheel build from unavailable uv build step in Docker env")

def test_ci_build_build_the_book():
    """pass_to_pass | CI job 'build' → step 'Build the book'"""
    pytest.skip("Requires build_all.sh + heavy deps not available in Docker env")
