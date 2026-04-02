"""
Task: slime-sglang-epd-encoder-support
Repo: THUDM/slime @ 5182e2d85c06827d57d0bbce98b5d39efeb5ae45
PR:   1704

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import py_compile
from pathlib import Path

REPO = "/workspace/slime"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for rel in [
        "slime/backends/sglang_utils/sglang_config.py",
        "slime/backends/sglang_utils/sglang_engine.py",
        "slime/ray/rollout.py",
    ]:
        py_compile.compile(f"{REPO}/{rel}", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_encoder_worker_type_accepted():
    """ServerGroupConfig accepts 'encoder' as a valid worker_type."""
    import sys
    sys.path.insert(0, REPO)
    from slime.backends.sglang_utils.sglang_config import ServerGroupConfig

    # Various GPU configurations to avoid single-value testing
    for num_gpus, per_engine in [(8, 4), (4, 2), (16, 8)]:
        cfg = ServerGroupConfig(
            worker_type="encoder", num_gpus=num_gpus, num_gpus_per_engine=per_engine
        )
        assert cfg.worker_type == "encoder"
        assert cfg.num_gpus == num_gpus
        assert cfg.num_gpus_per_engine == per_engine


# [pr_diff] fail_to_pass
def test_has_encoder_disaggregation_positive():
    """has_encoder_disaggregation returns True when encoder groups are present."""
    import sys
    sys.path.insert(0, REPO)
    # has_encoder_disaggregation is on ModelConfig (same class as has_pd_disaggregation)
    from slime.backends.sglang_utils.sglang_config import ModelConfig, ServerGroupConfig

    # EPD config: encoder + prefill + decode
    cfg_epd = ModelConfig(
        name="epd",
        server_groups=[
            ServerGroupConfig(worker_type="encoder", num_gpus=8, num_gpus_per_engine=4),
            ServerGroupConfig(worker_type="prefill", num_gpus=8, num_gpus_per_engine=4),
            ServerGroupConfig(worker_type="decode", num_gpus=16, num_gpus_per_engine=4),
        ],
    )
    assert cfg_epd.has_encoder_disaggregation is True

    # Encoder-only config
    cfg_enc_only = ModelConfig(
        name="enc_only",
        server_groups=[
            ServerGroupConfig(worker_type="encoder", num_gpus=4, num_gpus_per_engine=2),
        ],
    )
    assert cfg_enc_only.has_encoder_disaggregation is True


# [pr_diff] fail_to_pass
def test_has_encoder_disaggregation_negative():
    """has_encoder_disaggregation returns False when no encoder groups exist."""
    import sys
    sys.path.insert(0, REPO)
    from slime.backends.sglang_utils.sglang_config import ModelConfig, ServerGroupConfig

    # PD-only config (no encoder)
    cfg_pd = ModelConfig(
        name="pd",
        server_groups=[
            ServerGroupConfig(worker_type="prefill", num_gpus=8, num_gpus_per_engine=4),
            ServerGroupConfig(worker_type="decode", num_gpus=8, num_gpus_per_engine=4),
        ],
    )
    assert cfg_pd.has_encoder_disaggregation is False

    # Regular-only config
    cfg_reg = ModelConfig(
        name="regular",
        server_groups=[
            ServerGroupConfig(worker_type="regular", num_gpus=4, num_gpus_per_engine=4),
        ],
    )
    assert cfg_reg.has_encoder_disaggregation is False


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_worker_types_valid():
    """All pre-existing worker_type values are still accepted."""
    import sys
    sys.path.insert(0, REPO)
    from slime.backends.sglang_utils.sglang_config import ServerGroupConfig

    for wt in ["regular", "prefill", "decode", "placeholder"]:
        cfg = ServerGroupConfig(worker_type=wt, num_gpus=4, num_gpus_per_engine=4)
        assert cfg.worker_type == wt


# [repo_tests] pass_to_pass
def test_invalid_worker_type_rejected():
    """Invalid worker_type values still raise AssertionError."""
    import sys
    sys.path.insert(0, REPO)
    from slime.backends.sglang_utils.sglang_config import ServerGroupConfig
    import pytest

    for bad in ["unknown", "gpu", "encoder_only", ""]:
        with pytest.raises(AssertionError):
            ServerGroupConfig(worker_type=bad, num_gpus=4, num_gpus_per_engine=4)


# [repo_tests] pass_to_pass
def test_has_pd_disaggregation_unaffected():
    """has_pd_disaggregation still works correctly after encoder changes."""
    import sys
    sys.path.insert(0, REPO)
    # has_pd_disaggregation is on ModelConfig
    from slime.backends.sglang_utils.sglang_config import ModelConfig, ServerGroupConfig

    cfg_pd = ModelConfig(
        name="pd",
        server_groups=[
            ServerGroupConfig(worker_type="prefill", num_gpus=8, num_gpus_per_engine=4),
            ServerGroupConfig(worker_type="decode", num_gpus=8, num_gpus_per_engine=4),
        ],
    )
    assert cfg_pd.has_pd_disaggregation is True

    cfg_regular = ModelConfig(
        name="regular",
        server_groups=[
            ServerGroupConfig(worker_type="regular", num_gpus=4, num_gpus_per_engine=4),
        ],
    )
    assert cfg_regular.has_pd_disaggregation is False

    cfg_only_regular = ModelConfig(
        name="multi_regular",
        server_groups=[
            ServerGroupConfig(worker_type="regular", num_gpus=4, num_gpus_per_engine=4),
            ServerGroupConfig(worker_type="regular", num_gpus=8, num_gpus_per_engine=4),
        ],
    )
    assert cfg_only_regular.has_pd_disaggregation is False


# ---------------------------------------------------------------------------
# Structural (pr_diff) — AST-based, justified by torch/CUDA import barrier
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_compute_server_args_encoder_handling():
    """_compute_server_args sets encoder_only=True for encoder worker_type.

    AST-only because: _compute_server_args imports sglang.srt.server_args.ServerArgs
    which transitively requires torch/CUDA — cannot call in CPU-only container.
    """
    src = Path(f"{REPO}/slime/backends/sglang_utils/sglang_engine.py").read_text()
    tree = ast.parse(src)

    found_func = False
    handles_encoder = False
    sets_encoder_only = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_compute_server_args":
            found_func = True
            for child in ast.walk(node):
                if isinstance(child, ast.Constant) and child.value == "encoder":
                    handles_encoder = True
                if isinstance(child, ast.Subscript) and isinstance(child.slice, ast.Constant):
                    if child.slice.value == "encoder_only":
                        sets_encoder_only = True
            break

    assert found_func, "_compute_server_args function not found"
    assert handles_encoder, "no encoder handling in _compute_server_args"
    assert sets_encoder_only, "encoder_only not set in kwargs"


# [pr_diff] fail_to_pass
def test_override_key_normalization():
    """_compute_server_args normalizes override keys (hyphens → underscores).

    AST-only because: same torch/CUDA import constraint as above.
    """
    src = Path(f"{REPO}/slime/backends/sglang_utils/sglang_engine.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_compute_server_args":
            for child in ast.walk(node):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                    if child.func.attr == "replace" and len(child.args) >= 2:
                        vals = [
                            a.value for a in child.args[:2] if isinstance(a, ast.Constant)
                        ]
                        if "-" in vals and "_" in vals:
                            found = True
                            break
            break

    assert found, "no hyphen-to-underscore key normalization in _compute_server_args"


# [pr_diff] fail_to_pass
def test_rollout_phased_startup():
    """start_rollout_servers implements phased EPD startup (encoders first).

    AST-only because: rollout.py uses ray and sglang infrastructure requiring GPU cluster.
    """
    src = Path(f"{REPO}/slime/ray/rollout.py").read_text()
    tree = ast.parse(src)

    found_func = False
    has_epd_check = False
    has_encoder_urls = False
    has_encoder_phase = False

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "start_rollout_servers":
            found_func = True
            for child in ast.walk(node):
                if isinstance(child, ast.Attribute) and child.attr == "has_encoder_disaggregation":
                    has_epd_check = True
                if isinstance(child, ast.Name) and "encoder_url" in child.id.lower():
                    has_encoder_urls = True
                if isinstance(child, ast.Constant) and child.value == "encoder":
                    has_encoder_phase = True
            break

    assert found_func, "start_rollout_servers not found"
    assert has_epd_check, "no has_encoder_disaggregation check"
    assert has_encoder_urls, "no encoder URL collection"
    assert has_encoder_phase, "no encoder phase separation"
