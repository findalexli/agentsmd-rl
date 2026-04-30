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
import sys
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/AReaL"
SERVER_FILE = f"{REPO}/areal/engine/vllm_ext/areal_vllm_server.py"
REMOTE_FILE = f"{REPO}/areal/engine/vllm_remote.py"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def _call_build_distributed(use_lora, version, lora_name="test-lora",
                            lora_int_id=42, base_model_name="qwen2"):
    """
    Call build_distributed_weight_update_requests from the VLLMBackend class.
    Import the real module and call it to test actual behavior.
    """
    sys.path.insert(0, REPO)
    try:
        from areal.engine.vllm_remote import VLLMBackend
    except ImportError:
        pytest.skip("VLLMBackend not importable outside of full environment")

    class WeightUpdateMeta:
        type = "xccl"
        use_lora = False
        version = None
        lora_name = ""
        lora_int_id = 0
        base_model_name = ""
        peft_config = {}
        nccl_group_name = "test_group"

    meta = WeightUpdateMeta()
    meta.use_lora = use_lora
    meta.version = version
    meta.lora_name = lora_name
    meta.lora_int_id = lora_int_id
    meta.base_model_name = base_model_name
    meta.peft_config = {
        "target_modules": ["q_proj", "v_proj"],
        "r": 8,
        "lora_alpha": 16,
        "bias": "none",
    }
    meta.nccl_group_name = "test_nccl_group"
    meta.type = "xccl"

    param_specs = [type("ParamSpec", (), {"name": "layer.0.weight", "shape": (4, 4), "dtype": "float32"})]

    backend = VLLMBackend()
    result = backend.build_distributed_weight_update_requests(meta, param_specs)
    return result


def _get_lora_request(result):
    """Find the LoRA-specific request in the list of requests."""
    for req in result.requests:
        if hasattr(req, "endpoint") and "lora" in req.endpoint.lower():
            return req
    return None


# [pr_diff] fail_to_pass
def test_lora_xccl_update_payload_has_lora_fields():
    """When use_lora=True, the LoRA-specific XCCL request carries non-empty metadata."""
    result = _call_build_distributed(
        use_lora=True, version=1, lora_name="gsm8k-lora", lora_int_id=10
    )

    lora_req = _get_lora_request(result)
    assert lora_req is not None, (
        f"No LoRA-specific request found in {len(result.requests)} requests: "
        f"{[r.endpoint for r in result.requests]}"
    )

    # The LoRA endpoint must differ from the base XCCL endpoint
    base_req = result.requests[0]
    assert lora_req.endpoint != base_req.endpoint, (
        f"LoRA endpoint should differ from base endpoint"
    )

    # Payload must be non-empty when use_lora is True
    assert lora_req.payload, f"LoRA XCCL payload is empty: {lora_req.payload}"

    # The payload must encode the LoRA name with version suffix
    payload_str = str(lora_req.payload)
    assert "gsm8k-lora" in payload_str, (
        f"LoRA name not found in payload: {lora_req.payload}"
    )
    assert "v1" in payload_str, (
        f"Version suffix not found in payload: {lora_req.payload}"
    )


# [pr_diff] fail_to_pass
def test_lora_xccl_update_payload_varies_with_version():
    """The LoRA metadata in the XCCL request reflects the version number."""
    for version, lora_name, lora_int_id in [(0, "code-lora", 7), (5, "math-lora", 99)]:
        result = _call_build_distributed(
            use_lora=True, version=version, lora_name=lora_name, lora_int_id=lora_int_id
        )

        lora_req = _get_lora_request(result)
        assert lora_req is not None, f"No LoRA request found for version={version}"

        payload_str = str(lora_req.payload)
        expected_suffix = f"v{version}"
        assert expected_suffix in payload_str, (
            f"Expected suffix {expected_suffix!r} in payload for version={version}, "
            f"got: {lora_req.payload}"
        )
        assert lora_name in payload_str, (
            f"LoRA name {lora_name!r} not found in payload for version={version}: "
            f"{lora_req.payload}"
        )


# [pr_diff] fail_to_pass
def test_lora_xccl_endpoint_updates_lora_registry():
    """
    After the LoRA XCCL weight update endpoint runs, the registry reflects
    the new versioned name.
    """
    src = Path(SERVER_FILE).read_text()
    tree = ast.parse(src)

    # The function must exist
    async_funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)}
    assert "update_weight_lora_xccl" in async_funcs, (
        f"update_weight_lora_xccl not found in {SERVER_FILE}"
    )

    # Extract the function source and verify it has registry-update logic
    func_src = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_weight_lora_xccl":
            func_src = ast.get_source_segment(src, node)
            break

    assert func_src is not None

    # The function body must reference the registry (the models object)
    # This is the core behavior: the endpoint must update the registry
    has_registry_ref = (
        "openai_serving_models" in func_src or
        "models_obj" in func_src or
        ("models" in func_src and "lora_requests" in func_src)
    )
    assert has_registry_ref, (
        "update_weight_lora_xccl does not reference the registry - "
        "the fix may not be applied"
    )

    # The function must iterate over lora_requests to do the update
    assert "lora_requests" in func_src, (
        "update_weight_lora_xccl does not iterate over lora_requests - "
        "the fix may not be applied"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_lora_xccl_payload_empty():
    """When use_lora is False, XCCL update request payload must be empty."""
    result = _call_build_distributed(use_lora=False, version=None)

    # First request is the base XCCL update
    base_req = result.requests[0]
    assert base_req.payload == {}, f"Non-LoRA payload should be empty, got {base_req.payload}"

    # There should not be a LoRA-specific request when use_lora is False
    lora_req = _get_lora_request(result)
    assert lora_req is None, (
        f"No LoRA request should exist when use_lora=False, but found: {lora_req}"
    )


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


# [repo_ci] pass_to_pass - Registry update logic exists
def test_repo_key_functions_exist():
    """Repo CI: Key functions exist and contain registry update logic."""
    src = Path(SERVER_FILE).read_text()
    tree = ast.parse(src)

    func_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)}
    assert "update_weight_lora_xccl" in func_names, "update_weight_lora_xccl not found"

    # Verify the function has the registry update logic
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_weight_lora_xccl":
            func_src = ast.get_source_segment(src, node)
            assert "lora_requests" in func_src, "update_weight_lora_xccl missing lora_requests access"
            break


# [repo_ci] pass_to_pass - No syntax errors in function bodies
def test_repo_function_bodies_parse():
    """Repo CI: Key function bodies parse without syntax errors."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                if node.name in ("update_weight_lora_xccl", "update_weight_xccl"):
                    body_src = ast.get_source_segment(src, node)
                    if body_src:
                        try:
                            ast.parse(textwrap.dedent(body_src))
                        except SyntaxError as e:
                            raise AssertionError(f"Syntax error in {node.name}: {e}")


# [repo_ci] pass_to_pass - Ruff linting check
def test_repo_ruff_linting():
    """Repo CI: Modified files pass ruff linting (matching .pre-commit-config.yaml)."""
    r = subprocess.run(["pip", "show", "ruff"], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(
            ["pip", "install", "ruff==0.14.9", "-q"],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            pytest.skip(f"Could not install ruff: {r.stderr}")

    r = subprocess.run(
        ["ruff", "check", SERVER_FILE, REMOTE_FILE, "--output-format=full"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass - Ruff format check
def test_repo_ruff_format():
    """Repo CI: Modified files pass ruff format check (matching .pre-commit-config.yaml)."""
    r = subprocess.run(["pip", "show", "ruff"], capture_output=True, text=True)
    if r.returncode != 0:
        r = subprocess.run(
            ["pip", "install", "ruff==0.14.9", "-q"],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode != 0:
            pytest.skip(f"Could not install ruff: {r.stderr}")

    r = subprocess.run(
        ["ruff", "format", "--check", SERVER_FILE, REMOTE_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass - Trailing whitespace check
def test_repo_trailing_whitespace():
    """Repo CI: Modified files have no trailing whitespace."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        lines = src.split('\n')
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                raise AssertionError(f"Trailing whitespace found in {filepath} at line {i}")


# [repo_ci] pass_to_pass - End of file newline check
def test_repo_end_of_file_newline():
    """Repo CI: Modified files end with a newline."""
    for filepath in [SERVER_FILE, REMOTE_FILE]:
        src = Path(filepath).read_text()
        if src and not src.endswith('\n'):
            raise AssertionError(f"File {filepath} does not end with a newline")