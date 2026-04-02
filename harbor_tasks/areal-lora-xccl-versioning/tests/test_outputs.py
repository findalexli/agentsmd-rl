"""
Task: areal-lora-xccl-versioning
Repo: inclusionAI/AReaL @ 1927decc369d30df0037854b5d58ec7a9ca2a3b7
PR:   1021

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from pathlib import Path
from types import SimpleNamespace

REPO = "/workspace/AReaL"
SERVER_FILE = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"
REMOTE_FILE = f"{REPO}/areal/engine/vllm_remote.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_function(filepath, func_name):
    """Find an async/sync function def by name."""
    src = Path(filepath).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)) and node.name == func_name:
            return node, src
    raise AssertionError(f"Function {func_name!r} not found in {filepath}")


def _find_method(filepath, class_name, method_name):
    """Find a method inside a class."""
    src = Path(filepath).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return item, src
    raise AssertionError(f"Method {class_name}.{method_name} not found in {filepath}")


def _extract_source(src, node):
    """Extract and dedent source lines for an AST node."""
    lines = src.splitlines()[node.lineno - 1 : node.end_lineno]
    return textwrap.dedent("\n".join(lines))


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for path in [SERVER_FILE, REMOTE_FILE]:
        py_compile.compile(path, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_endpoint_accepts_lora_request_param():
    """update_weight_lora_xccl must accept a typed LoRA request parameter."""
    # AST-only because: vLLM + FastAPI server internals cannot be imported
    node, src = _find_function(SERVER_FILE, "update_weight_lora_xccl")

    param_annotations = []
    for arg in node.args.args:
        if arg.annotation:
            ann = ast.get_source_segment(src, arg.annotation)
            if ann:
                param_annotations.append(ann)

    assert any("UpdateWeightsFromXcclRequestLora" in ann for ann in param_annotations), (
        f"Endpoint must accept UpdateWeightsFromXcclRequestLora parameter, "
        f"got annotations: {param_annotations}"
    )


# [pr_diff] fail_to_pass
def test_registry_update_renames_lora():
    """After LoRA XCCL update, lora_requests registry reflects the new name."""
    node, src = _find_function(SERVER_FILE, "update_weight_lora_xccl")
    func_src = _extract_source(src, node)

    # Convert async->sync, strip await so we can exec the registry logic
    func_src = func_src.replace("async def", "def")
    func_src = re.sub(r"\bawait\s+", "", func_src)

    class _MockLoraReq:
        def __init__(self, name, int_id):
            self.lora_name = name
            self.lora_int_id = int_id

    class _Noop:
        def __getattr__(self, _):
            return lambda *a, **k: None

    def _mock_build_response(ret_list):
        return {"success": True}

    ns = {
        "logger": _Noop(),
        "build_response": _mock_build_response,
        "UpdateWeightsFromXcclRequestLora": type("UpdateWeightsFromXcclRequestLora", (), {}),
        "Request": type("Request", (), {}),
    }
    exec(func_src, ns)
    fn = ns["update_weight_lora_xccl"]

    test_cases = [
        ("lora-gsm8k-v0", "lora-gsm8k-v1", 1),
        ("adapter-a-v0", "adapter-a-v5", 42),
        ("my-lora-v99", "my-lora-v100", 7),
    ]

    for old_name, new_name, lora_id in test_cases:
        lora_requests = {old_name: _MockLoraReq(old_name, lora_id)}
        models = SimpleNamespace(lora_requests=lora_requests)

        raw_request = SimpleNamespace(
            app=SimpleNamespace(
                state=SimpleNamespace(
                    engine_client=SimpleNamespace(
                        engine_core=SimpleNamespace(
                            call_utility_async=lambda *a, **k: [(True, "ok")]
                        )
                    ),
                    openai_serving_models=models,
                )
            )
        )
        request = SimpleNamespace(lora_name=new_name, lora_int_id=lora_id)

        fn(request=request, raw_request=raw_request)

        assert new_name in models.lora_requests, (
            f"Expected registry to contain {new_name!r}, "
            f"got {list(models.lora_requests.keys())}"
        )
        assert old_name not in models.lora_requests, (
            f"Old name {old_name!r} should be removed from registry"
        )
        assert models.lora_requests[new_name].lora_int_id == lora_id


# [pr_diff] fail_to_pass
def test_lora_payload_forwarded():
    """build_distributed_weight_update_requests forwards LoRA payload for XCCL update."""
    method_node, src = _find_method(
        REMOTE_FILE, "VLLMBackend", "build_distributed_weight_update_requests"
    )
    method_src = _extract_source(src, method_node)

    class HttpRequest:
        def __init__(self, endpoint, payload):
            self.endpoint = endpoint
            self.payload = payload

    class WeightUpdateRequests:
        def __init__(self, requests):
            self.requests = requests

    def get_versioned_lora_name(name, version):
        return f"{name}-v{version}"

    ns = {
        "HttpRequest": HttpRequest,
        "WeightUpdateRequests": WeightUpdateRequests,
        "get_versioned_lora_name": get_versioned_lora_name,
    }
    exec(method_src, ns)
    fn = ns["build_distributed_weight_update_requests"]

    test_cases = [
        ("test-lora", 1, 42, {"target_modules": ["q_proj"], "r": 8, "lora_alpha": 16, "bias": "none"}, "base-model"),
        ("adapter-b", 5, 99, {"target_modules": ["v_proj", "k_proj"], "r": 16, "lora_alpha": 32, "bias": "all"}, "llama-7b"),
        ("reward-lora", 0, 1, {"target_modules": ["o_proj"], "r": 4, "lora_alpha": 8, "bias": "none"}, "qwen-vl"),
    ]

    for lora_name, version, lora_int_id, peft_config, base_model in test_cases:
        meta = SimpleNamespace(
            use_lora=True,
            version=version,
            lora_name=lora_name,
            lora_int_id=lora_int_id,
            peft_config=peft_config,
            base_model_name=base_model,
            nccl_group_name="group0",
        )
        param_specs = [SimpleNamespace(name="w", dtype="float16", shape=[100, 200])]

        result = fn(None, meta, param_specs)
        update_req = result.requests[1]

        assert update_req.endpoint == "/areal_update_weights_lora_xccl"
        assert update_req.payload != {}, (
            f"LoRA XCCL update must forward payload, got empty dict "
            f"(lora_name={lora_name!r}, version={version})"
        )
        assert "lora_name" in update_req.payload, (
            f"Payload must contain lora_name, got keys: {list(update_req.payload.keys())}"
        )
        assert "lora_int_id" in update_req.payload
        assert update_req.payload["lora_int_id"] == lora_int_id


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — non-lora path unchanged
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_lora_payload_unchanged():
    """Non-LoRA XCCL update still sends empty payload."""
    method_node, src = _find_method(
        REMOTE_FILE, "VLLMBackend", "build_distributed_weight_update_requests"
    )
    method_src = _extract_source(src, method_node)

    class HttpRequest:
        def __init__(self, endpoint, payload):
            self.endpoint = endpoint
            self.payload = payload

    class WeightUpdateRequests:
        def __init__(self, requests):
            self.requests = requests

    def get_versioned_lora_name(name, version):
        return f"{name}-v{version}"

    ns = {
        "HttpRequest": HttpRequest,
        "WeightUpdateRequests": WeightUpdateRequests,
        "get_versioned_lora_name": get_versioned_lora_name,
    }
    exec(method_src, ns)
    fn = ns["build_distributed_weight_update_requests"]

    meta = SimpleNamespace(use_lora=False, nccl_group_name="group0")
    param_specs = [SimpleNamespace(name="w", dtype="float16", shape=[100, 200])]

    result = fn(None, meta, param_specs)
    update_req = result.requests[1]

    assert update_req.endpoint == "/areal_update_weights_xccl"
    assert update_req.payload == {}, (
        f"Non-LoRA XCCL update should have empty payload, got: {update_req.payload}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_endpoint_not_stub():
    """update_weight_lora_xccl has meaningful body (not just pass/return)."""
    # AST-only because: function uses vLLM internals
    node, _ = _find_function(SERVER_FILE, "update_weight_lora_xccl")
    stmts = [
        s for s in node.body
        if not isinstance(s, ast.Pass)
        and not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
    ]
    assert len(stmts) >= 3, (
        f"Function body must have >= 3 non-trivial statements, got {len(stmts)}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ 1927decc369d30df0037854b5d58ec7a9ca2a3b7
def test_no_wildcard_imports():
    """No wildcard imports (from x import *) in modified files."""
    for path in [SERVER_FILE, REMOTE_FILE]:
        for i, line in enumerate(Path(path).read_text().splitlines(), 1):
            assert not re.match(r"\s*from\s+\S+\s+import\s+\*", line), (
                f"{path}:{i} has wildcard import: {line.strip()}"
            )


# [agent_config] pass_to_pass — AGENTS.md:89-90 @ 1927decc369d30df0037854b5d58ec7a9ca2a3b7
def test_no_bare_print():
    """No bare print() in production code — use logger instead."""
    for path in [SERVER_FILE, REMOTE_FILE]:
        for i, line in enumerate(Path(path).read_text().splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("print(") and not stripped.startswith("#"):
                assert False, f"{path}:{i} uses print(): {stripped}"
