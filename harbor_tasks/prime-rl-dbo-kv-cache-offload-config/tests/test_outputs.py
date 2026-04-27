"""
Task: prime-rl-dbo-kv-cache-offload-config
Repo: prime-rl @ 2648c19e21f949812afbf6e42a42c57decbf4b94
PR:   2225

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/prime-rl"

# ---------------------------------------------------------------------------
# Mock GPU-only dependencies before importing project code.
# CPU torch + pydantic + wandb + transformers are installed in the container;
# vllm, triton, ring_flash_attn, etc. are not.
# ---------------------------------------------------------------------------
_GPU_ONLY = [
    "vllm", "vllm.triton_utils", "vllm.logger", "vllm.config",
    "vllm.config.lora", "vllm.lora", "vllm.lora.layers",
    "vllm.lora.layers.column_parallel_linear", "vllm.lora.layers.utils",
    "vllm.model_executor", "vllm.model_executor.models",
    "vllm.model_executor.models.qwen3_5",
    "vllm.model_executor.layers", "vllm.model_executor.layers.fused_moe",
    "vllm.model_executor.layers.fused_moe.deep_gemm_utils",
    "ring_flash_attn", "flash_attn", "liger_kernel",
    "deep_ep", "deep_gemm", "nixl", "tilelang", "flash_linear_attention",
    "torchdata", "torchtitan", "verifiers", "dion", "prime",
    "jaxtyping", "beartype",
    "pyarrow", "datasets", "openai", "aiolimiter", "tenacity",
    "setproctitle", "uvloop", "pyzmq", "zmq", "rich",
    "pynvml",
]
for _m in _GPU_ONLY:
    sys.modules.setdefault(_m, MagicMock())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    files = [
        f"{REPO}/src/prime_rl/configs/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/rl.py",
    ]
    for fpath in files:
        py_compile.compile(fpath, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kv_cache_offload_config_defaults():
    """KVCacheOffloadConfig exists with correct default values."""
    from prime_rl.configs.inference import KVCacheOffloadConfig

    cfg = KVCacheOffloadConfig()
    assert cfg.block_size == 64, f"Expected block_size=64, got {cfg.block_size}"
    assert cfg.cpu_bytes == 1_000_000_000, f"Expected cpu_bytes=1000000000, got {cfg.cpu_bytes}"


# [pr_diff] fail_to_pass
def test_enable_dbo_field_and_default():
    """InferenceConfig has enable_dbo field with default False."""
    from prime_rl.configs.inference import InferenceConfig

    cfg = InferenceConfig()
    assert hasattr(cfg, "enable_dbo"), "InferenceConfig missing enable_dbo field"
    assert cfg.enable_dbo is False, f"Expected enable_dbo=False, got {cfg.enable_dbo}"

    cfg_on = InferenceConfig(enable_dbo=True)
    assert cfg_on.enable_dbo is True


# [pr_diff] fail_to_pass
def test_enable_dbo_in_vllm_namespace():
    """to_vllm() namespace includes enable_dbo attribute."""
    from prime_rl.configs.inference import InferenceConfig

    for dbo_val in (False, True):
        cfg = InferenceConfig(enable_dbo=dbo_val)
        ns = cfg.to_vllm()
        assert hasattr(ns, "enable_dbo"), "vLLM namespace missing enable_dbo"
        assert ns.enable_dbo is dbo_val, (
            f"Expected enable_dbo={dbo_val} in namespace, got {ns.enable_dbo}"
        )


# [pr_diff] fail_to_pass
def test_disaggregated_kv_cache_offload_field():
    """DisaggregatedInferenceDeploymentConfig has kv_cache_offload field, default None."""
    from prime_rl.configs.inference import (
        DisaggregatedInferenceDeploymentConfig,
        KVCacheOffloadConfig,
    )

    cfg = DisaggregatedInferenceDeploymentConfig()
    assert hasattr(cfg, "kv_cache_offload"), "Missing kv_cache_offload field"
    assert cfg.kv_cache_offload is None, (
        f"Expected default None, got {cfg.kv_cache_offload}"
    )

    cfg_on = DisaggregatedInferenceDeploymentConfig(
        kv_cache_offload=KVCacheOffloadConfig(block_size=32, cpu_bytes=500_000_000)
    )
    assert cfg_on.kv_cache_offload is not None
    assert cfg_on.kv_cache_offload.block_size == 32
    assert cfg_on.kv_cache_offload.cpu_bytes == 500_000_000


# [pr_diff] fail_to_pass
def test_kv_cache_offload_custom_values():
    """KVCacheOffloadConfig accepts various valid custom values."""
    from prime_rl.configs.inference import KVCacheOffloadConfig

    test_cases = [
        (1, 0),
        (128, 2_000_000_000),
        (256, 10_000_000_000),
        (64, 1),
    ]
    for bs, cb in test_cases:
        cfg = KVCacheOffloadConfig(block_size=bs, cpu_bytes=cb)
        assert cfg.block_size == bs, f"block_size: expected {bs}, got {cfg.block_size}"
        assert cfg.cpu_bytes == cb, f"cpu_bytes: expected {cb}, got {cfg.cpu_bytes}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from skills/config/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — skills/config/SKILL.md:72
def test_kv_cache_offload_rejects_invalid_block_size():
    """Config fails early on invalid block_size (ge=1 constraint)."""
    from pydantic import ValidationError

    from prime_rl.configs.inference import KVCacheOffloadConfig

    for bad_bs in (0, -1, -100):
        try:
            KVCacheOffloadConfig(block_size=bad_bs)
            raise AssertionError(
                f"KVCacheOffloadConfig(block_size={bad_bs}) should raise ValidationError"
            )
        except ValidationError:
            pass  # expected


# [agent_config] fail_to_pass — skills/config/SKILL.md:72
def test_kv_cache_offload_forbids_extra_fields():
    """Config rejects unknown fields (extra='forbid')."""
    from pydantic import ValidationError

    from prime_rl.configs.inference import KVCacheOffloadConfig

    try:
        KVCacheOffloadConfig(unknown_field="surprise")
        raise AssertionError(
            "KVCacheOffloadConfig should reject unknown fields"
        )
    except ValidationError:
        pass  # expected


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_ruff_check_modified_files():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    files = [
        f"{REPO}/src/prime_rl/configs/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/rl.py",
    ]
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", f"{REPO}/pyproject.toml"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_check_configs():
    """Repo's ruff linting passes on configs directory (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/configs/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_configs_import():
    """Configs module imports work (pass_to_pass)."""
    from prime_rl.configs.inference import InferenceConfig, DisaggregatedInferenceDeploymentConfig

    # Verify basic instantiation works
    cfg = InferenceConfig()
    assert cfg is not None

    disagg_cfg = DisaggregatedInferenceDeploymentConfig()
    assert disagg_cfg is not None


# [repo_tests] pass_to_pass
def test_ruff_format_modified_files():
    """Repo's ruff format check passes on modified files (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    files = [
        f"{REPO}/src/prime_rl/configs/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/inference.py",
        f"{REPO}/src/prime_rl/entrypoints/rl.py",
    ]
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--config", f"{REPO}/pyproject.toml"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_format_configs():
    """Repo's ruff format check passes on configs directory (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/configs/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_check_entrypoints():
    """Repo's ruff linting passes on entrypoints directory (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/entrypoints/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_format_entrypoints():
    """Repo's ruff format check passes on entrypoints directory (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/entrypoints/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_pytest_unit_configs():
    """Repo's unit tests for configs pass (pass_to_pass)."""
    import subprocess
    import sys
    import os

    # Install test dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "tomli_w", "psutil", "setproctitle", "tomli", "-q"],
        check=True, capture_output=True
    )

    # Temporarily rename conftest.py to avoid pkill requirement
    conftest = f"{REPO}/tests/conftest.py"
    conftest_bak = f"{REPO}/tests/conftest.py.bak"

    try:
        if os.path.exists(conftest):
            os.rename(conftest, conftest_bak)

        r = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/unit/test_configs.py::test_defaults",
                "tests/unit/test_configs.py::test_toml_partial_nested_override",
                "tests/unit/test_configs.py::test_cli_overrides_defaults",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Pytest failed:\n{r.stdout}\n{r.stderr}"
    finally:
        # Restore conftest.py
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# [repo_tests] pass_to_pass
def test_ruff_check_combined():
    """Repo's ruff linting passes on configs and entrypoints (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/configs/", f"{REPO}/src/prime_rl/entrypoints/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_format_combined():
    """Repo's ruff format check passes on configs and entrypoints (pass_to_pass)."""
    import subprocess
    import sys

    # Ensure ruff is installed
    subprocess.run([sys.executable, "-m", "pip", "install", "ruff", "-q"], check=True, capture_output=True)

    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--config", f"{REPO}/pyproject.toml", f"{REPO}/src/prime_rl/configs/", f"{REPO}/src/prime_rl/entrypoints/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_load_configs():
    """All repo TOML config files can be loaded by their config classes (pass_to_pass)."""
    import subprocess
    import sys
    import os

    # Install test dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "tomli_w", "psutil", "setproctitle", "tomli", "-q"],
        check=True, capture_output=True
    )

    # Temporarily rename conftest.py to avoid pkill requirement
    conftest = f"{REPO}/tests/conftest.py"
    conftest_bak = f"{REPO}/tests/conftest.py.bak"

    try:
        if os.path.exists(conftest):
            os.rename(conftest, conftest_bak)

        r = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/unit/test_configs.py::test_load_configs",
                "-v",
                "--tb=short",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Pytest test_load_configs failed:\n{r.stdout}\n{r.stderr}"
    finally:
        # Restore conftest.py
        if os.path.exists(conftest_bak):
            os.rename(conftest_bak, conftest)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_inference_config_existing_fields():
    """Existing InferenceConfig fields still work after adding new ones."""
    from prime_rl.configs.inference import InferenceConfig

    cfg = InferenceConfig(
        enable_lora=True,
        gpu_memory_utilization=0.85,
        seed=42,
        enable_expert_parallel=True,
    )
    assert cfg.enable_lora is True
    assert cfg.gpu_memory_utilization == 0.85
    assert cfg.seed == 42
    assert cfg.enable_expert_parallel is True

    ns = cfg.to_vllm()
    assert ns.enable_lora is True
    assert ns.seed == 42


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — entrypoint and template behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_inference_entrypoint_passes_kv_offload_params():
    """Inference entrypoint passes KV offload params to template context via slurm script."""
    import tempfile
    from prime_rl.configs.inference import InferenceConfig, DisaggregatedInferenceDeploymentConfig, KVCacheOffloadConfig, ServerConfig
    from prime_rl.configs.shared import SlurmConfig
    from pathlib import Path

    # Create a config with disaggregated deployment and slurm with template
    cfg = InferenceConfig(
        server=ServerConfig(),
        slurm=SlurmConfig(
            template_path=Path("/workspace/prime-rl/src/prime_rl/templates/inference.sbatch.j2"),
        ),
        deployment=DisaggregatedInferenceDeploymentConfig(
            num_prefill_nodes=1,
            num_decode_nodes=1,
            prefill_port=8000,
            decode_port=8001,
            router_port=8002,
            kv_cache_offload=KVCacheOffloadConfig(block_size=32, cpu_bytes=500_000_000),
        ),
        output_dir=Path("/tmp/test_output"),
    )

    # Write the slurm script and check its content
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.toml"
        script_path = Path(tmpdir) / "script.sbatch"

        from prime_rl.entrypoints import inference
        inference.write_slurm_script(cfg, config_path, script_path)

        script_content = script_path.read_text()

        # Should contain MultiConnector with OffloadingConnector in PREFILL_KV_CFG
        # Note: kv_offload is a Jinja2 variable that controls the conditional; the literal string
        # "kv_offload" doesn't appear in the rendered script - only the result of the conditional
        assert "MultiConnector" in script_content, "Script should use MultiConnector for kv offload"
        assert "OffloadingConnector" in script_content, "Script should use OffloadingConnector for kv offload"


# [pr_diff] fail_to_pass
def test_rl_entrypoint_passes_kv_offload_params():
    """RL entrypoint passes KV offload params to template context via slurm script."""
    import tempfile
    from pathlib import Path

    from prime_rl.configs.rl import RLConfig, MultiNodeDeploymentConfig
    from prime_rl.configs.trainer import TrainerConfig
    from prime_rl.configs.orchestrator import OrchestratorConfig
    from prime_rl.configs.inference import InferenceConfig, DisaggregatedInferenceDeploymentConfig, KVCacheOffloadConfig
    from prime_rl.configs.shared import SlurmConfig

    # Create minimal required configs
    tc = TrainerConfig()
    oc = OrchestratorConfig()

    # Create inference config with disaggregated deployment and kv_cache_offload
    inf = InferenceConfig(
        deployment=DisaggregatedInferenceDeploymentConfig(
            num_prefill_nodes=1,
            num_decode_nodes=1,
            prefill_port=8000,
            decode_port=8001,
            router_port=8002,
            kv_cache_offload=KVCacheOffloadConfig(block_size=128, cpu_bytes=2_000_000_000),
        ),
        slurm=None,
    )

    # Create the RLConfig
    cfg = RLConfig(trainer=tc, orchestrator=oc, inference=inf)

    # Override output_dir and slurm for this test
    cfg.output_dir = Path("/tmp/test_output")
    cfg.slurm = SlurmConfig(
        template_path=Path("/workspace/prime-rl/src/prime_rl/templates/multi_node_rl.sbatch.j2"),
    )
    # Set multi_node deployment type (this is RLConfig's own deployment, not inference.deployment)
    cfg.deployment = MultiNodeDeploymentConfig(
        type="multi_node",
        num_train_nodes=1,
        num_infer_nodes=1,
        gpus_per_node=8,
    )

    # Write the slurm script and check its content
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.toml"
        script_path = Path(tmpdir) / "script.sbatch"

        from prime_rl.entrypoints import rl
        rl.write_slurm_script(cfg, config_path, script_path)

        script_content = script_path.read_text()

        # Should contain kv_offload reference and MultiConnector
        # Note: kv_offload is a Jinja2 variable that controls the conditional; the literal string
        # "kv_offload" doesn't appear in the rendered script - only the result of the conditional
        assert "MultiConnector" in script_content, "Script should use MultiConnector for kv offload"
        assert "OffloadingConnector" in script_content, "Script should use OffloadingConnector for kv offload"


# [pr_diff] fail_to_pass
def test_inference_template_uses_separate_kv_cfgs():
    """Inference template uses PREFILL_KV_CFG and DECODE_KV_CFG instead of single KV_CFG."""
    template_path = f"{REPO}/src/prime_rl/templates/inference.sbatch.j2"
    with open(template_path) as f:
        content = f.read()

    # Must define PREFILL_KV_CFG
    assert "PREFILL_KV_CFG" in content, "Template missing PREFILL_KV_CFG variable"
    # Must define DECODE_KV_CFG
    assert "DECODE_KV_CFG" in content, "Template missing DECODE_KV_CFG variable"


# [pr_diff] fail_to_pass
def test_inference_template_multiconnector_when_offload():
    """Inference template uses MultiConnector for prefill when kv_offload is enabled."""
    template_path = f"{REPO}/src/prime_rl/templates/inference.sbatch.j2"
    with open(template_path) as f:
        content = f.read()

    # When kv_offload is True, should use MultiConnector with OffloadingConnector
    assert "kv_offload" in content, "Template should check kv_offload flag"
    assert "MultiConnector" in content, "Template should use MultiConnector when offload enabled"
    assert "OffloadingConnector" in content, "Template should use OffloadingConnector"


# [pr_diff] fail_to_pass
def test_multi_node_rl_template_uses_separate_kv_cfgs():
    """Multi-node RL template uses PREFILL_KV_CFG and DECODE_KV_CFG instead of single KV_CFG."""
    template_path = f"{REPO}/src/prime_rl/templates/multi_node_rl.sbatch.j2"
    with open(template_path) as f:
        content = f.read()

    # Must define PREFILL_KV_CFG
    assert "PREFILL_KV_CFG" in content, "Multi-node RL template missing PREFILL_KV_CFG variable"
    # Must define DECODE_KV_CFG
    assert "DECODE_KV_CFG" in content, "Multi-node RL template missing DECODE_KV_CFG variable"


# [pr_diff] fail_to_pass
def test_multi_node_rl_template_multiconnector_when_offload():
    """Multi-node RL template uses MultiConnector for prefill when kv_offload is enabled."""
    template_path = f"{REPO}/src/prime_rl/templates/multi_node_rl.sbatch.j2"
    with open(template_path) as f:
        content = f.read()

    # When kv_offload is True, should use MultiConnector with OffloadingConnector
    assert "kv_offload" in content, "Multi-node RL template should check kv_offload flag"
    assert "MultiConnector" in content, "Multi-node RL template should use MultiConnector when offload enabled"
    assert "OffloadingConnector" in content, "Multi-node RL template should use OffloadingConnector"
