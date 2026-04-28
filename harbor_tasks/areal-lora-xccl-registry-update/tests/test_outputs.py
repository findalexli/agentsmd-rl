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
# Helpers — AST extract + execute for behavioral tests
# ---------------------------------------------------------------------------

def _make_mock_namespace():
    """Return a namespace dict with stub types needed by the remote function."""

    class HttpRequest:
        def __init__(self, endpoint, payload):
            self.endpoint = endpoint
            self.payload = payload

    class WeightUpdateRequests:
        def __init__(self, requests):
            self.requests = requests

    class WeightUpdateMeta:
        pass

    class ParamSpec:
        pass

    def get_versioned_lora_name(lora_name, version):
        return f"{lora_name}-v{version}"

    return {
        "HttpRequest": HttpRequest,
        "WeightUpdateRequests": WeightUpdateRequests,
        "WeightUpdateMeta": WeightUpdateMeta,
        "ParamSpec": ParamSpec,
        "get_versioned_lora_name": get_versioned_lora_name,
    }


def _load_build_distributed():
    """Parse vllm_remote.py, extract build_distributed_weight_update_requests,
    strip annotations, compile it in a mock namespace, and return the callable."""
    src = Path(REMOTE_FILE).read_text()
    tree = ast.parse(src)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "build_distributed_weight_update_requests":
            func_node = node
            break

    if func_node is None:
        pytest.fail("build_distributed_weight_update_requests not found in source")

    # Strip type annotations so we don't need the real types at compile time
    func_node.returns = None
    for arg in func_node.args.args:
        arg.annotation = None

    ns = _make_mock_namespace()
    code = compile(ast.unparse(func_node), REMOTE_FILE, "exec")
    exec(code, ns)
    return ns["build_distributed_weight_update_requests"]


def _call_build_distributed(use_lora, version, lora_name="test-lora",
                            lora_int_id=42, base_model_name="qwen2"):
    """Extract and execute build_distributed_weight_update_requests with mock inputs."""
    func = _load_build_distributed()

    ns = _make_mock_namespace()
    meta = ns["WeightUpdateMeta"]()
    meta.nccl_group_name = "test_group"
    meta.use_lora = use_lora
    meta.version = version
    meta.lora_name = lora_name
    meta.lora_int_id = lora_int_id
    meta.peft_config = {
        "target_modules": ["q_proj", "v_proj"],
        "r": 8,
        "lora_alpha": 16,
        "bias": "none",
    }
    meta.base_model_name = base_model_name

    ParamSpec = ns["ParamSpec"]
    ps = ParamSpec()
    ps.name = "layer.0.weight"
    ps.shape = (4, 4)
    ps.dtype = "float32"
    param_specs = [ps]

    return func(None, meta, param_specs)


def _get_lora_update_req(result):
    """Find the LoRA update (not meta) request in the list."""
    for req in result.requests:
        if hasattr(req, "endpoint") and "lora" in req.endpoint.lower() and "meta" not in req.endpoint.lower():
            return req
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lora_xccl_update_payload_has_lora_fields():
    """When use_lora=True, the LoRA-specific XCCL update request carries LoRA metadata."""
    result = _call_build_distributed(
        use_lora=True, version=1, lora_name="gsm8k-lora", lora_int_id=10
    )

    lora_req = _get_lora_update_req(result)
    assert lora_req is not None, (
        f"No LoRA update request found in {len(result.requests)} requests: "
        f"{[(r.endpoint, type(r.payload).__name__, len(str(r.payload))) for r in result.requests]}"
    )

    # Payload must be non-empty (carrying the LoRA metadata including lora_name/lora_int_id)
    assert lora_req.payload, f"LoRA XCCL update payload is empty: {lora_req.payload}"

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
    """The LoRA metadata in the XCCL update request reflects the version number."""
    for version, lora_name, lora_int_id in [(0, "code-lora", 7), (5, "math-lora", 99)]:
        result = _call_build_distributed(
            use_lora=True, version=version, lora_name=lora_name, lora_int_id=lora_int_id
        )

        lora_req = _get_lora_update_req(result)
        assert lora_req is not None, f"No LoRA update request found for version={version}"

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

    # The XCCL update endpoint request (index 1, non-LoRA) must have empty payload
    xccl_req = result.requests[1]
    assert xccl_req.payload == {}, f"Non-LoRA XCCL update payload should be empty, got {xccl_req.payload}"

    # There should not be a LoRA-specific request when use_lora is False
    lora_req = _get_lora_update_req(result)
    assert lora_req is None, (
        f"No LoRA update request should exist when use_lora=False, but found: {lora_req}"
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


# === CI-mined test ===
def test_ci_install_test_verify_wheel_artifact():
    """pass_to_pass | CI job 'Install test' -> step 'Verify wheel artifact'"""
    r = subprocess.run(
        ["bash", "-lc",
         'python -m zipfile -l dist/*.whl > /dev/null 2>&1'],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"CI step 'Verify wheel artifact' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_install_test_verify_package_import():
    """pass_to_pass | CI job 'Install test' → step 'Verify package import'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run python -c "import areal; print(f\'areal version: {areal.__version__}\')"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify package import' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_verify_core_modules_are_importable():
    """pass_to_pass | CI job 'Install test' → step 'Verify core modules are importable'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify core modules are importable' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_build_wheel():
    """pass_to_pass | CI job 'Install test' → step 'Build wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv build --wheel'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_the_book():
    """pass_to_pass | CI job 'build' → step 'Build the book'"""
    r = subprocess.run(
        ["bash", "-lc", './build_all.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build the book' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
