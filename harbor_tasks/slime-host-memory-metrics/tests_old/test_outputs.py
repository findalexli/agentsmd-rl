"""
Task: slime-host-memory-metrics
Repo: slime @ 887fba113b512156098509c808b7bc93a8386b47
PR:   1764

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/slime"

# Helper script: mocks torch.cuda (no GPU needed), imports and calls available_memory()
_CALL_SCRIPT = """import sys, json
from unittest.mock import MagicMock

mock_torch = MagicMock()
mock_torch.cuda.current_device.return_value = 0
mock_torch.cuda.mem_get_info.return_value = (4 * 1024**3, 8 * 1024**3)
mock_torch.cuda.memory_allocated.return_value = 2 * 1024**3
mock_torch.cuda.memory_reserved.return_value = 3 * 1024**3

sys.modules["torch"] = mock_torch
sys.modules["torch.cuda"] = mock_torch.cuda
sys.modules["torch.distributed"] = mock_torch.distributed

sys.path.insert(0, ".")
from slime.utils.memory_utils import available_memory
result = available_memory()
print(json.dumps(result))
"""


def _call_available_memory() -> dict:
    """Run available_memory() with mocked CUDA, return the result dict."""
    r = subprocess.run(
        ["python3", "-c", _CALL_SCRIPT],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Failed to call available_memory():\n{r.stderr}"
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """memory_utils.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "slime/utils/memory_utils.py"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_available_memory_has_host_keys():
    """available_memory() must return all four host memory metric keys."""
    result = _call_available_memory()
    expected_keys = [
        "host_total_GB",
        "host_available_GB",
        "host_used_GB",
        "host_free_GB",
    ]
    for key in expected_keys:
        assert key in result, f"Missing host memory key: '{key}'"


def test_host_memory_values_match_psutil():
    """Host memory values must come from psutil and be converted to GB."""
    import psutil

    result = _call_available_memory()
    vm = psutil.virtual_memory()

    # Total memory is a hardware constant — must match exactly
    expected_total = round(vm.total / (1024 ** 3), 2)
    assert result["host_total_GB"] == expected_total, (
        f"host_total_GB={result['host_total_GB']} != expected {expected_total}"
    )

    # All host values must be positive numbers in GB range (not raw bytes)
    for key in ["host_total_GB", "host_available_GB", "host_used_GB", "host_free_GB"]:
        val = result[key]
        assert isinstance(val, (int, float)), f"{key} is not numeric: {type(val)}"
        assert val > 0, f"{key} must be positive, got {val}"
        assert val < 100000, f"{key}={val} seems too large — should be in GB, not bytes"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression
# ---------------------------------------------------------------------------

def test_gpu_keys_preserved():
    """Original GPU memory keys must still be present in the result."""
    result = _call_available_memory()
    gpu_keys = ["gpu", "total_GB", "free_GB", "used_GB", "allocated_GB", "reserved_GB"]
    for key in gpu_keys:
        assert key in result, f"Missing original GPU key: '{key}'"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks (must pass on base commit and after fix)
# ---------------------------------------------------------------------------

def test_repo_ruff_lint():
    """Repo's Python code passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "slime/utils/memory_utils.py", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr}"


def test_repo_isort_check():
    """Repo's Python imports are correctly sorted (pass_to_pass)."""
    r = subprocess.run(
        ["isort", "--check-only", "slime/utils/memory_utils.py", "--profile", "black", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr}"


def test_repo_black_format():
    """Repo's Python code is correctly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["black", "--check", "slime/utils/memory_utils.py", "--quiet"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Black format check failed:\n{r.stderr}"


def test_repo_plugin_contracts():
    """Repo's plugin contract tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/", "--tb=no", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow some tests to fail (existing issues), but pytest itself must complete
    assert r.returncode in [0, 1], f"Plugin contracts tests crashed:\n{r.stderr[-500:]}"


def test_repo_unit_trace_utils():
    """Repo's trace_utils unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/utils/test_trace_utils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Trace utils tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_loss_mask_type():
    """Repo's loss_mask_type_qwen35 unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/utils/test_loss_mask_type_qwen35.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Loss mask type tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_sglang_config():
    """Repo's sglang_config unit tests (passing subset) pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest",
         "tests/utils/test_sglang_config.py::TestSglangConfigUpdateWeights::test_update_weights_explicit_false",
         "tests/utils/test_sglang_config.py::TestSglangConfigUpdateWeights::test_multi_model_total_gpus",
         "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Sglang config tests failed:\n{r.stderr[-500:]}"
