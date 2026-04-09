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
_CALL_SCRIPT = """\
import sys, json
from unittest.mock import MagicMock

mock_torch = MagicMock()
mock_torch.cuda.current_device.return_value = 0
mock_torch.cuda.mem_get_info.return_value = (4 * 1024**3, 8 * 1024**3)
mock_torch.cuda.memory_allocated.return_value = 2 * 1024**3
mock_torch.cuda.memory_reserved.return_value = 3 * 1024**3

sys.modules['torch'] = mock_torch
sys.modules['torch.cuda'] = mock_torch.cuda
sys.modules['torch.distributed'] = mock_torch.distributed

sys.path.insert(0, '.')
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
