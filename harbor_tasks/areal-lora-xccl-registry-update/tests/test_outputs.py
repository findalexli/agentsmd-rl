"""
Task: areal-lora-xccl-registry-update
Repo: AReaL @ 1927decc369d30df0037854b5d58ec7a9ca2a3b7
PR:   1021

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/AReaL"
SERVER_FILE = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"
REMOTE_FILE = f"{REPO}/areal/engine/vllm_remote.py"


def _extract_function(filepath, class_name, func_name):
    """Extract a function/method source from a file using AST."""
    src = Path(filepath).read_text()
    tree = ast.parse(src)
    if class_name:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == func_name:
                        return ast.get_source_segment(src, item)
    else:
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return ast.get_source_segment(src, node)
    return None


def _build_method_test_env():
    """Build exec namespace with mock types for build_distributed_weight_update_requests."""
    from dataclasses import dataclass, field

    @dataclass
    class HttpRequest:
        endpoint: str
        payload: dict
        method: str = "POST"

    @dataclass
    class WeightUpdateRequests:
        requests: list

    @dataclass
    class ParamSpec:
        name: str
        shape: tuple
        dtype: str

    def get_versioned_lora_name(lora_name, version):
        return f"{lora_name}-v{version}"

    return {
        "HttpRequest": HttpRequest,
        "WeightUpdateRequests": WeightUpdateRequests,
        "ParamSpec": ParamSpec,
        "WeightUpdateMeta": type("WeightUpdateMeta", (), {}),
        "get_versioned_lora_name": get_versioned_lora_name,
    }


def _call_build_distributed(use_lora, version, lora_name="test-lora",
                            lora_int_id=42, base_model_name="qwen2"):
    """Extract and call build_distributed_weight_update_requests with given params."""
    from dataclasses import dataclass, field as dc_field

    env = _build_method_test_env()

    @dataclass
    class WeightUpdateMeta:
        type: str = "xccl"
        use_lora: bool = False
        version: int = None
        lora_name: str = ""
        lora_int_id: int = 0
        base_model_name: str = ""
        peft_config: dict = dc_field(default_factory=dict)
        nccl_group_name: str = "test_group"

    method_src = _extract_function(REMOTE_FILE, "VLLMBackend", "build_distributed_weight_update_requests")
    assert method_src is not None, "build_distributed_weight_update_requests not found in VLLMBackend"

    # Dedent the method so it can be exec'd at module level
    method_src = textwrap.dedent(method_src)
    exec(method_src, env)
    func = env["build_distributed_weight_update_requests"]

    meta = WeightUpdateMeta(
        use_lora=use_lora,
        version=version,
        lora_name=lora_name,
        lora_int_id=lora_int_id,
        base_model_name=base_model_name,
        peft_config={
            "target_modules": ["q_proj", "v_proj"],
            "r": 8,
            "lora_alpha": 16,
            "bias": "none",
        },
        nccl_group_name="test_nccl_group",
    )
    param_specs = [env["ParamSpec"](name="layer.0.weight", shape=(4, 4), dtype="float32")]

    return func(None, meta, param_specs)  # self is unused


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {filepath}: {e}")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lora_xccl_update_payload_has_lora_fields():
    """XCCL update request payload must contain lora_name/lora_int_id when use_lora=True."""
    result = _call_build_distributed(
        use_lora=True, version=1, lora_name="gsm8k-lora", lora_int_id=10
    )
    update_req = result.requests[1]
    assert update_req.endpoint == "/areal_update_weights_lora_xccl"
    assert "lora_name" in update_req.payload, (
        f"Update request payload missing lora_name: {update_req.payload}"
    )
    assert "lora_int_id" in update_req.payload, (
        f"Update request payload missing lora_int_id: {update_req.payload}"
    )
    assert update_req.payload["lora_name"] == "gsm8k-lora-v1"
    assert update_req.payload["lora_int_id"] == 10


# [pr_diff] fail_to_pass
def test_lora_xccl_update_payload_varies_with_version():
    """Versioned LoRA name in payload changes with version number."""
    for version, lora_name, lora_int_id in [(0, "code-lora", 7), (5, "math-lora", 99)]:
        result = _call_build_distributed(
            use_lora=True, version=version, lora_name=lora_name, lora_int_id=lora_int_id
        )
        update_req = result.requests[1]
        expected_name = f"{lora_name}-v{version}"
        assert update_req.payload["lora_name"] == expected_name, (
            f"Expected {expected_name}, got {update_req.payload.get('lora_name')}"
        )
        assert update_req.payload["lora_int_id"] == lora_int_id


# [pr_diff] fail_to_pass
def test_lora_xccl_endpoint_updates_lora_registry():
    """After LoRA XCCL weight update, openai_serving_models registry reflects new name."""
    func_src = _extract_function(SERVER_FILE, None, "update_weight_lora_xccl")
    assert func_src is not None, "update_weight_lora_xccl not found"

    # Also extract build_response and to_json_response helpers
    build_resp_src = _extract_function(SERVER_FILE, None, "build_response")
    to_json_src = _extract_function(SERVER_FILE, None, "to_json_response")

    class MockLogger:
        def info(self, msg): pass
        def warning(self, msg): pass

    class MockLoraReq:
        def __init__(self, name, int_id):
            self.lora_name = name
            self.lora_int_id = int_id

    class MockModels:
        def __init__(self):
            self.lora_requests = {
                "gsm8k-lora-v0": MockLoraReq("gsm8k-lora-v0", 42),
                "other-lora-v0": MockLoraReq("other-lora-v0", 99),
            }

    class MockEngineCore:
        async def call_utility_async(self, *args):
            return [(True, "success")]

    class MockLLM:
        engine_core = MockEngineCore()

    class MockAppState:
        def __init__(self):
            self.engine_client = MockLLM()
            self.openai_serving_models = MockModels()

    class MockApp:
        state = None

    class MockRawRequest:
        app = MockApp()

    class MockRequest:
        lora_name = "gsm8k-lora-v1"
        lora_int_id = 42

    MockRawRequest.app.state = MockAppState()

    # Provide type stubs for annotations referenced in function signatures
    ns = {
        "logger": MockLogger(),
        "Request": type("Request", (), {}),
        "UpdateWeightsFromXcclRequestLora": type("UpdateWeightsFromXcclRequestLora", (), {}),
        "JSONResponse": lambda content, status_code=200: {"content": content, "status_code": status_code},
    }

    # Load helper functions
    if to_json_src:
        exec(textwrap.dedent(to_json_src), ns)
    else:
        ns["to_json_response"] = lambda s, m: {"success": s, "message": m}

    if build_resp_src:
        exec(textwrap.dedent(build_resp_src), ns)
    else:
        ns["build_response"] = lambda r: {"success": True}

    # Load the endpoint function
    exec(textwrap.dedent(func_src), ns)
    endpoint_fn = ns["update_weight_lora_xccl"]

    # Run async function
    async def run():
        models = MockRawRequest.app.state.openai_serving_models
        assert "gsm8k-lora-v0" in models.lora_requests
        assert "gsm8k-lora-v1" not in models.lora_requests

        await endpoint_fn(MockRequest(), MockRawRequest())

        assert "gsm8k-lora-v1" in models.lora_requests, (
            f"New name not in registry: {list(models.lora_requests.keys())}"
        )
        assert "gsm8k-lora-v0" not in models.lora_requests, (
            f"Old name still in registry: {list(models.lora_requests.keys())}"
        )
        assert models.lora_requests["gsm8k-lora-v1"].lora_int_id == 42
        # Other LoRA must be untouched
        assert "other-lora-v0" in models.lora_requests

    asyncio.run(run())


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_lora_xccl_payload_empty():
    """When use_lora is False, XCCL update request payload must be empty."""
    result = _call_build_distributed(use_lora=False, version=None)
    update_req = result.requests[1]
    assert update_req.endpoint == "/areal_update_weights_xccl"
    assert update_req.payload == {}, f"Expected empty payload, got {update_req.payload}"


# [static] pass_to_pass
def test_no_wildcard_imports():
    """Modified files must not use wildcard imports (from x import *)."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", (
                        f"Wildcard import found in {filepath}: from {node.module} import *"
                    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI checks)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass - Python compilation check
def test_repo_python_compilation():
    """Repo CI: Modified Python files compile without errors."""
    import py_compile
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        try:
            py_compile.compile(filepath, doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"Compilation failed for {filepath}: {e}")


# [repo_ci] pass_to_pass - Function existence check
def test_repo_key_functions_exist():
    """Repo CI: Key functions modified in PR exist and are extractable."""
    # Check server file functions
    func_src = _extract_function(SERVER_FILE, None, "update_weight_lora_xccl")
    assert func_src is not None, "update_weight_lora_xccl not found in server file"

    # Check remote file method
    method_src = _extract_function(REMOTE_FILE, "VLLMBackend", "build_distributed_weight_update_requests")
    assert method_src is not None, "build_distributed_weight_update_requests not found in remote file"


# [repo_ci] pass_to_pass - No syntax errors in function bodies
def test_repo_function_bodies_parse():
    """Repo CI: Key function bodies parse without syntax errors."""
    # Test server function
    func_src = _extract_function(SERVER_FILE, None, "update_weight_lora_xccl")
    if func_src:
        try:
            ast.parse(textwrap.dedent(func_src))
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in update_weight_lora_xccl: {e}")

    # Test remote method
    method_src = _extract_function(REMOTE_FILE, "VLLMBackend", "build_distributed_weight_update_requests")
    if method_src:
        try:
            ast.parse(textwrap.dedent(method_src))
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in build_distributed_weight_update_requests: {e}")


# [repo_ci] pass_to_pass - Ruff linting check (matches repo's pre-commit v0.14.9)
def test_repo_ruff_linting():
    """Repo CI: Modified files pass ruff linting (matching .pre-commit-config.yaml)."""
    # Install ruff if not present (matches repo's ruff version 0.14.9)
    r = subprocess.run(["pip", "show", "ruff"], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(
            ["pip", "install", "ruff==0.14.9", "-q"],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            pytest.skip(f"Could not install ruff: {r.stderr}")

    # Run ruff check on modified files
    r = subprocess.run(
        ["ruff", "check", SERVER_FILE, REMOTE_FILE, "--output-format=full"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass - Ruff format check (matches repo's pre-commit v0.14.9)
def test_repo_ruff_format():
    """Repo CI: Modified files pass ruff format check (matching .pre-commit-config.yaml)."""
    # Install ruff if not present
    r = subprocess.run(["pip", "show", "ruff"], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(
            ["pip", "install", "ruff==0.14.9", "-q"],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            pytest.skip(f"Could not install ruff: {r.stderr}")

    # Run ruff format check on modified files
    r = subprocess.run(
        ["ruff", "format", "--check", SERVER_FILE, REMOTE_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass - Trailing whitespace check (matches repo's pre-commit)
def test_repo_trailing_whitespace():
    """Repo CI: Modified files have no trailing whitespace (matching .pre-commit-config.yaml)."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        lines = src.split('\n')
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                raise AssertionError(f"Trailing whitespace found in {filepath} at line {i}")


# [repo_ci] pass_to_pass - End of file newline check (matches repo's pre-commit)
def test_repo_end_of_file_newline():
    """Repo CI: Modified files end with a newline (matching .pre-commit-config.yaml)."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        if src and not src.endswith('\n'):
            raise AssertionError(f"File {filepath} does not end with a newline")
