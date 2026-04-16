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


# [repo_tests] pass_to_pass -- Repo CI: isort import ordering check on modified files
def test_repo_isort():
    """Repo CI: isort import ordering check passes on modified files."""
    # Install isort if needed
    r = subprocess.run([sys.executable, "-m", "pip", "install", "isort", "--quiet"], capture_output=True, timeout=120)
    # Run isort check on modified files with black profile (per pyproject.toml)
    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check", "--profile=black", "slime_plugins/mbridge/glm4moe_lite.py", "slime/backends/megatron_utils/model_provider.py"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr}"


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
    """_weight_to_hf_format produces both base and MTP-layer names for shared weights.

    Base commit: shared weights produce wrong layer index (hardcoded 61 from DeepseekV3Bridge).
    Gold patch: uses dynamic num_hidden_layers (47 for GLM-4.7-Flash).
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

    # Test embedding weight: should produce TWO entries (base + MTP layer)
    embed_names, embed_tensors = bridge._weight_to_hf_format("embedding.word_embeddings.weight", tensor)
    assert len(embed_names) == 2, f"Expected 2 names for embedding, got {len(embed_names)}: {embed_names}"
    assert len(embed_tensors) == 2, f"Expected 2 tensors for embedding, got {len(embed_tensors)}"

    # At least one name should reference the dynamic layer index
    layer_refs = [n for n in embed_names if f"model.layers.{n_layers}" in n]
    assert len(layer_refs) >= 1, f"Expected at least one name with layer {n_layers} in {embed_names}"
    print(f"PASS: embedding produces 2 names including layer-{n_layers} ref: {embed_names}")

    # Test output weight: should also produce TWO entries
    out_names, out_tensors = bridge._weight_to_hf_format("output_layer.weight", tensor)
    assert len(out_names) == 2, f"Expected 2 names for output, got {len(out_names)}: {out_names}"

    # At least one name should reference the dynamic layer index
    layer_refs_out = [n for n in out_names if f"model.layers.{n_layers}" in n]
    assert len(layer_refs_out) >= 1, f"Expected at least one name with layer {n_layers} in {out_names}"
    print(f"PASS: output produces 2 names including layer-{n_layers} ref: {out_names}")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_convert_mtp_direct_names():
    """_weight_to_hf_format correctly maps MTP direct param names with dynamic layer count.

    Base commit: MTP direct params don't map correctly (wrong layer or missing mapping).
    Gold patch: MTP direct params (enorm, hnorm, eh_proj, final_layernorm) map correctly.
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

    # MTP direct params that should be mapped to the correct dynamic layer
    mtp_params = [
        "mtp.layers.0.enorm.weight",
        "mtp.layers.0.hnorm.weight",
        "mtp.layers.0.eh_proj.weight",
        "mtp.layers.0.final_layernorm.weight",
    ]

    for mtp_name in mtp_params:
        names, tensors = bridge._weight_to_hf_format(mtp_name, tensor)
        # Each should produce exactly 1 output name
        assert len(names) == 1, f"{mtp_name} -> expected 1 name, got {len(names)}: {names}"
        hf_name = names[0]
        # The HF name must reference the correct dynamic layer index, not hardcoded 61
        assert f"model.layers.{n_layers}" in hf_name, f"{mtp_name} -> expected layer {n_layers} in '{hf_name}'"
        # Must NOT reference hardcoded 61
        assert ".layers.61." not in hf_name, f"{mtp_name} -> found hardcoded layer 61 in '{hf_name}'"
        print(f"PASS: {mtp_name} -> {hf_name}")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_convert_mtp_transformer_delegation():
    """_weight_to_hf_format delegates transformer-layer MTP params via attention/MLP mappings.

    Base commit: transformer MTP params don't route correctly.
    Gold patch: delegates to parent's attention/MLP weight mapping methods.
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

    # Transformer-layer attention param - should map through attention mapping
    attn_mtp_name = "mtp.layers.0.transformer_layer.self_attention.linear_proj.weight"
    attn_names, _ = bridge._weight_to_hf_format(attn_mtp_name, tensor)
    assert len(attn_names) == 1, f"Expected 1 attention output, got {len(attn_names)}: {attn_names}"
    # Should reference the dynamic layer and contain attention projection
    assert f"model.layers.{n_layers}" in attn_names[0], f"Expected layer {n_layers} in {attn_names[0]}"
    assert "self_attn" in attn_names[0] or "attention" in attn_names[0].lower(), f"Expected attention-related name, got {attn_names[0]}"
    print(f"PASS: attention MTP param -> {attn_names}")

    # Transformer-layer MLP param - should map through MLP mapping
    mlp_mtp_name = "mtp.layers.0.transformer_layer.mlp.linear_fc2.weight"
    mlp_names, _ = bridge._weight_to_hf_format(mlp_mtp_name, tensor)
    assert len(mlp_names) == 1, f"Expected 1 MLP output, got {len(mlp_names)}: {mlp_names}"
    # Should reference the dynamic layer and contain MLP-related name
    assert f"model.layers.{n_layers}" in mlp_names[0], f"Expected layer {n_layers} in {mlp_names[0]}"
    print(f"PASS: MLP MTP param -> {mlp_names}")

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

bridge = object.__new__(GLM4MoELiteBridge)
bridge.dtype = torch.bfloat16

# Create a temp directory to act as the weights path
with tempfile.TemporaryDirectory() as tmpdir:
    # Mock _get_actual_hf_path to return the temp dir
    bridge._get_actual_hf_path = lambda path: tmpdir

    io = bridge._get_safetensor_io(tmpdir)

    # Must be standard SafeTensorIO, NOT FP8SafeTensorIO
    # Check via module path rather than exact class name to avoid gold-specific coupling
    io_module = type(io).__module__
    io_classname = type(io).__name__
    # Standard SafeTensorIO should NOT have 'fp8' in its class name
    assert 'fp8' not in io_classname.lower(), f"Expected non-FP8 IO class, got {io_classname}"
    # And should be a SafeTensorIO subclass
    assert 'SafeTensor' in io_classname, f"Expected SafeTensor IO, got {io_classname}"
    print(f"PASS: _get_safetensor_io returns {io_classname} (non-FP8 SafeTensor)")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"


# [pr_diff] fail_to_pass
def test_weight_to_hf_shared():
    """_weight_to_hf_format returns both base and MTP-layer names for shared weights.

    Base commit: shared weights may produce wrong count or wrong layer index.
    Gold patch: correctly handles shared weights with dynamic layer count.
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

    # Test embedding weight: verifies base name AND MTP-layer name are both present
    names, tensors = bridge._weight_to_hf_format("embedding.word_embeddings.weight", tensor)
    # Should have 2 entries
    assert len(names) == 2, f"Expected 2 names, got {len(names)}: {names}"
    assert len(tensors) == 2, f"Expected 2 tensors, got {len(tensors)}"
    # Both tensors should be the same object (not copies)
    # At least one name should be the base model name (no layer index or layer 0)
    base_names = [n for n in names if ".layers." not in n or ".layers.0." in n]
    assert len(base_names) >= 1, f"Expected base name (no layer or layer 0) in {names}"
    # At least one name should reference the dynamic MTP layer
    mtp_names = [n for n in names if f"model.layers.{n_layers}" in n]
    assert len(mtp_names) >= 1, f"Expected MTP layer name (layer {n_layers}) in {names}"
    print(f"PASS: embedding weight returns 2 names: base={base_names}, mtp={mtp_names}")

    # Test output weight similarly
    names_out, _ = bridge._weight_to_hf_format("output_layer.weight", tensor)
    assert len(names_out) == 2, f"Expected 2 names for output, got {len(names_out)}: {names_out}"
    mtp_names_out = [n for n in names_out if f"model.layers.{n_layers}" in n]
    assert len(mtp_names_out) >= 1, f"Expected MTP layer name (layer {n_layers}) in {names_out}"
    print(f"PASS: output weight returns 2 names including layer-{n_layers} ref")

print("ALL_PASS")
"""
    result = _run_python_test(code)
    assert result.returncode == 0, f"Test failed: {result.stderr}"
    assert "ALL_PASS" in result.stdout, f"Expected ALL_PASS, got: {result.stdout}"
