"""
Task: slime-glm4-mtp-bridge
Repo: slime @ 57e76686346beeaaec4010ebefc56b9949686457
PR:   1712

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

These are BEHAVIORAL tests that execute actual code via subprocess.run().
They verify the functional behavior changes from the PR diff.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/slime"


def _run_python_test(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute Python test code in the repo environment via subprocess.

    This ensures we're actually executing code, not just checking structure.
    """
    # The mock transformer_engine package is already installed in site-packages.
    # No need for additional mocking.
    full_code = code

    # Write code to a temp file and execute it
    script = Path(REPO) / "_eval_test.py"
    script.write_text(full_code)
    try:
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
            env={
                **subprocess.os.environ,
                "PYTHONPATH": REPO,
            },
        )
    finally:
        script.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax check
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    import py_compile

    py_compile.compile(f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py", doraise=True)
    py_compile.compile(
        f"{REPO}/slime/backends/megatron_utils/model_provider.py", doraise=True
    )


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI/CD checks that must pass on base and fix
# -----------------------------------------------------------------------------

# [repo_tests] pass_to_pass -- Repo CI: Python syntax check for glm4moe_lite.py
def test_repo_syntax_glm4moe_lite():
    """Repo CI: glm4moe_lite.py must have valid Python syntax."""
    import py_compile

    py_compile.compile(f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py", doraise=True)


# [repo_tests] pass_to_pass -- Repo CI: Python syntax check for model_provider.py
def test_repo_syntax_model_provider():
    """Repo CI: model_provider.py must have valid Python syntax."""
    import py_compile

    py_compile.compile(
        f"{REPO}/slime/backends/megatron_utils/model_provider.py", doraise=True
    )


# [repo_tests] pass_to_pass -- Repo CI: ruff linting on modified files
def test_repo_ruff():
    """Repo CI: ruff check passes on modified files."""
    # Install ruff if needed
    r = subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "--quiet"], capture_output=True, timeout=120)
    # Run ruff check on modified files
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "slime_plugins/mbridge/glm4moe_lite.py", "slime/backends/megatron_utils/model_provider.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass -- Repo CI: black formatting check on modified files
def test_repo_black():
    """Repo CI: black formatting check passes on modified files."""
    # Install black if needed
    r = subprocess.run([sys.executable, "-m", "pip", "install", "black", "--quiet"], capture_output=True, timeout=120)
    # Run black check on modified files
    r = subprocess.run(
        [sys.executable, "-m", "black", "--check", "slime_plugins/mbridge/glm4moe_lite.py", "slime/backends/megatron_utils/model_provider.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"black check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass -- Repo CI: MTP bridge mapping tests pass
def test_repo_mtp_bridge_mapping():
    """Repo CI: MTP bridge mapping unit tests pass.

    These tests exercise the same MTP bridge functionality that the PR adds
    to GLM4MoELiteBridge (_convert_mtp_param, weight mappings, etc.).
    """
    # Install pytest if needed
    r = subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "--quiet"], capture_output=True, timeout=120)
    # Run pytest on the MTP bridge mapping tests
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_qwen3_5_mtp_bridge_mapping.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"MTP bridge mapping tests failed:\n{r.stdout}\n{r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests using subprocess.run()
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rope_theta_patched():
    """GLM4MoELiteBridge.__init__ extracts rope_theta from rope_parameters dict.

    Base commit: fails because rope_theta is not set from rope_parameters.
    Gold patch: extracts rope_theta from rope_parameters dict when needed.
    """
    code = """
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, '/workspace/slime')

from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge
from mbridge.core.bridge import Bridge

# Test 1: rope_theta extracted from rope_parameters
for theta_value in [500000, 1000000, 250000]:
    cfg = SimpleNamespace(
        rope_parameters={"rope_theta": theta_value},
        num_hidden_layers=47,
        num_nextn_predict_layers=1,
    )
    assert not hasattr(cfg, "rope_theta"), "precondition: no rope_theta yet"

    # Create bridge with mocked parent init
    with patch.object(Bridge, "__init__", lambda self, *a, **kw: None):
        bridge = GLM4MoELiteBridge(cfg)

    assert hasattr(cfg, "rope_theta"), f"rope_theta not set for theta={theta_value}"
    assert cfg.rope_theta == theta_value, f"Expected rope_theta={theta_value}, got {cfg.rope_theta}"
    print(f"PASS: rope_theta={theta_value} extracted from rope_parameters")

# Test 2: default rope_theta when rope_parameters missing
cfg_default = SimpleNamespace(
    num_hidden_layers=47,
    num_nextn_predict_layers=1,
)
with patch.object(Bridge, "__init__", lambda self, *a, **kw: None):
    bridge = GLM4MoELiteBridge(cfg_default)

assert cfg_default.rope_theta == 1000000, f"Expected default 1000000, got {cfg_default.rope_theta}"
print("PASS: default rope_theta=1000000 when rope_parameters missing")
print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_shared_mapping_dynamic_layers():
    """_SHARED_STATE_DICT_MAPPING uses dynamic num_hidden_layers instead of hardcoded 61.

    Base commit: uses hardcoded layer 61 (from DeepseekV3Bridge).
    Gold patch: uses hf_config.num_hidden_layers (47 for GLM-4.7-Flash).
    """
    code = """
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, '/workspace/slime')

from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge
from mbridge.core.bridge import Bridge

for n_layers in [47, 30, 60]:
    cfg = SimpleNamespace(
        rope_theta=1000000,
        num_hidden_layers=n_layers,
        num_nextn_predict_layers=1,
    )

    with patch.object(Bridge, "__init__", lambda self, *a, **kw: None):
        bridge = GLM4MoELiteBridge(cfg)

    mapping = bridge._SHARED_STATE_DICT_MAPPING

    # Check embedding mapping uses dynamic layer
    embed_names = mapping["embedding.word_embeddings.weight"]
    expected_embed = f"model.layers.{n_layers}.embed_tokens.weight"
    assert expected_embed in embed_names, f"Expected {expected_embed} in embed mapping, got {embed_names}"

    # Check output mapping uses dynamic layer
    output_names = mapping["output_layer.weight"]
    expected_output = f"model.layers.{n_layers}.shared_head.head.weight"
    assert expected_output in output_names, f"Expected {expected_output} in output mapping, got {output_names}"

    print(f"PASS: n_layers={n_layers} uses dynamic layer index")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_convert_mtp_direct_names():
    """_convert_mtp_param maps direct MTP param names with dynamic layer count.

    Base commit: method doesn't exist (inherited from DeepseekV3Bridge uses hardcoded 61).
    Gold patch: maps direct MTP names using self.config.num_layers.
    """
    code = """
import sys
from types import SimpleNamespace

sys.path.insert(0, '/workspace/slime')

from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge

for n_layers in [47, 30]:
    bridge = object.__new__(GLM4MoELiteBridge)
    bridge.config = SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)

    expected = {
        "mtp.layers.0.enorm.weight": [f"model.layers.{n_layers}.enorm.weight"],
        "mtp.layers.0.hnorm.weight": [f"model.layers.{n_layers}.hnorm.weight"],
        "mtp.layers.0.eh_proj.weight": [f"model.layers.{n_layers}.eh_proj.weight"],
        "mtp.layers.0.final_layernorm.weight": [f"model.layers.{n_layers}.shared_head.norm.weight"],
    }

    for mcore_name, hf_names in expected.items():
        result = bridge._convert_mtp_param(mcore_name)
        assert result == hf_names, f"n_layers={n_layers}, name={mcore_name}: expected {hf_names}, got {result}"
        print(f"PASS: {mcore_name} -> {result}")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_convert_mtp_transformer_delegation():
    """_convert_mtp_param delegates transformer-layer params via attention/mlp mappings.

    Base commit: method doesn't exist.
    Gold patch: delegates attention/mlp params through parent's mapping methods.
    """
    code = """
import sys
from types import SimpleNamespace

sys.path.insert(0, '/workspace/slime')

from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge

for n_layers in [47, 30]:
    bridge = object.__new__(GLM4MoELiteBridge)
    bridge.config = SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)

    # Attention param - maps through _weight_name_mapping_attention
    attn_result = bridge._convert_mtp_param(
        "mtp.layers.0.transformer_layer.self_attention.linear_proj.weight"
    )
    expected_attn = [f"model.layers.{n_layers}.self_attn.o_proj.weight"]
    assert attn_result == expected_attn, f"n_layers={n_layers}: expected {expected_attn}, got {attn_result}"
    print(f"PASS: attention param maps to {attn_result}")

    # MLP param - maps through _weight_name_mapping_mlp
    mlp_result = bridge._convert_mtp_param(
        "mtp.layers.0.transformer_layer.mlp.linear_fc2.weight"
    )
    expected_mlp = [f"model.layers.{n_layers}.mlp.down_proj.weight"]
    assert mlp_result == expected_mlp, f"n_layers={n_layers}: expected {expected_mlp}, got {mlp_result}"
    print(f"PASS: mlp param maps to {mlp_result}")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_safetensor_io_type():
    """_get_safetensor_io returns standard SafeTensorIO, not FP8 dequant.

    Base commit: inherits DeepseekV3Bridge._get_safetensor_io which returns FP8 dequant.
    Gold patch: overrides to return standard SafeTensorIO for bf16 safetensors.
    """
    code = """
import sys
import tempfile

sys.path.insert(0, '/workspace/slime')

import torch
from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge
from mbridge.core.safetensor_io import SafeTensorIO

bridge = object.__new__(GLM4MoELiteBridge)
bridge.dtype = torch.bfloat16

# Create a temp directory to act as the weights path
with tempfile.TemporaryDirectory() as tmpdir:
    # Mock _get_actual_hf_path to return the temp dir
    bridge._get_actual_hf_path = lambda path: tmpdir

    io = bridge._get_safetensor_io(tmpdir)

    # Must be standard SafeTensorIO, NOT FP8SafeTensorIO
    assert type(io) is SafeTensorIO, f"Expected SafeTensorIO, got {type(io).__name__}"
    print(f"PASS: _get_safetensor_io returns SafeTensorIO (not FP8)")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_weight_to_hf_shared():
    """_weight_to_hf_format returns both base and MTP-layer names for shared weights.

    Base commit: inherits DeepseekV3Bridge which checks for hardcoded 61 layers.
    Gold patch: handles shared weights with dynamic layer count.
    """
    code = """
import sys
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, '/workspace/slime')

import torch
from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge
from mbridge.core.bridge import Bridge

for n_layers in [47, 30]:
    # Create bridge with proper initialization
    cfg = SimpleNamespace(
        rope_theta=1000000,
        num_hidden_layers=n_layers,
        num_nextn_predict_layers=1,
    )

    with patch.object(Bridge, "__init__", lambda self, *a, **kw: None):
        bridge = GLM4MoELiteBridge(cfg)
        bridge.config = SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)
        bridge.make_vocab_size_divisible_by = None

    tensor = torch.ones(10)

    # Test embedding weight
    names, tensors = bridge._weight_to_hf_format("embedding.word_embeddings.weight", tensor)
    assert "model.embed_tokens.weight" in names, f"Missing base embed name in {names}"
    expected_mtp_embed = f"model.layers.{n_layers}.embed_tokens.weight"
    assert expected_mtp_embed in names, f"Missing MTP embed name {expected_mtp_embed} in {names}"
    assert len(tensors) == 2, f"Expected 2 tensors, got {len(tensors)}"
    print(f"PASS: embedding weight returns {names}")

    # Test output weight
    names_out, _ = bridge._weight_to_hf_format("output_layer.weight", tensor)
    assert "lm_head.weight" in names_out, f"Missing lm_head in {names_out}"
    expected_mtp_out = f"model.layers.{n_layers}.shared_head.head.weight"
    assert expected_mtp_out in names_out, f"Missing MTP output name {expected_mtp_out} in {names_out}"
    print(f"PASS: output weight returns {names_out}")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"
