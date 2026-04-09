"""
Task: vllm-conv3d-torch-version-check
Repo: vllm-project/vllm @ bea23536f627b2b4153f2e672753b6034b78dedb
PR:   #38487

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import types
import torch
import torch.nn as nn
from packaging import version as pkg_version
from unittest.mock import patch

REPO = "/repo"

# ---------------------------------------------------------------------------
# Mock preamble: set up minimal vllm stubs so Conv3dLayer can be imported
# ---------------------------------------------------------------------------

_PACKAGE_PATHS = {
    "vllm": [f"{REPO}/vllm"],
    "vllm.model_executor": [f"{REPO}/vllm/model_executor"],
    "vllm.model_executor.layers": [f"{REPO}/vllm/model_executor/layers"],
    "vllm.utils": [f"{REPO}/vllm/utils"],
}

for mod_name in [
    "vllm", "vllm.envs", "vllm.logger", "vllm.platforms",
    "vllm.sequence", "vllm.model_executor",
    "vllm.model_executor.custom_op", "vllm.model_executor.layers",
    "vllm.utils",
]:
    if mod_name not in sys.modules:
        m = types.ModuleType(mod_name)
        if mod_name in _PACKAGE_PATHS:
            m.__path__ = _PACKAGE_PATHS[mod_name]
        sys.modules[mod_name] = m


class FakeCustomOp(nn.Module):
    @classmethod
    def register(cls, name):
        return lambda c: c


sys.modules["vllm.model_executor.custom_op"].CustomOp = FakeCustomOp

# Provide real version-check functions in fake torch_utils
tu = types.ModuleType("vllm.utils.torch_utils")


def _is_torch_equal_or_newer(torch_version, target):
    return pkg_version.parse(torch_version) >= pkg_version.parse(target)


def is_torch_equal_or_newer(target):
    return _is_torch_equal_or_newer(str(torch.__version__), target)


def _is_torch_equal(target):
    assert target.count(".") == 2
    tv = pkg_version.parse(str(torch.__version__))
    return tv >= pkg_version.parse(target) and pkg_version.parse(target + ".1") > tv


def is_torch_equal(target):
    return _is_torch_equal(target)


tu.is_torch_equal_or_newer = is_torch_equal_or_newer
tu._is_torch_equal_or_newer = _is_torch_equal_or_newer
tu.is_torch_equal = is_torch_equal
tu._is_torch_equal = _is_torch_equal
sys.modules["vllm.utils.torch_utils"] = tu


class FakeLogger:
    def __getattr__(self, name):
        return lambda *a, **kw: None


sys.modules["vllm.logger"].init_logger = lambda name: FakeLogger()
sys.modules["vllm.envs"].CUDA_VISIBLE_DEVICES = None

sys.path.insert(0, REPO)
from vllm.model_executor.layers.conv import Conv3dLayer  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_layer(enable_linear=True):
    """Create a Conv3dLayer with deterministic weights."""
    if enable_linear:
        layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=2, stride=2)
    else:
        layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=3, stride=1, padding=1)
    torch.manual_seed(42)
    nn.init.normal_(layer.weight)
    nn.init.zeros_(layer.bias)
    return layer


def _get_path_taken(layer, x, version):
    """Run forward_cuda with a spoofed torch version, return which path was taken."""
    original = torch.__version__
    torch.__version__ = version
    try:
        with patch.object(layer, '_forward_mulmat', wraps=layer._forward_mulmat) as mock_mm, \
             patch.object(layer, '_forward_conv', wraps=layer._forward_conv) as mock_cv:
            layer.forward_cuda(x)
            if mock_mm.called:
                return "mulmat"
            elif mock_cv.called:
                return "conv"
            else:
                return "unknown"
    finally:
        torch.__version__ = original


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """conv.py must be valid Python."""
    import ast
    src = (REPO + "/vllm/model_executor/layers/conv.py")
    ast.parse(open(src).read())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_torch_2_10_uses_mulmat():
    """forward_cuda uses mulmat path for torch 2.10.0 (>= 2.9.0)."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.10.0") == "mulmat", \
        "forward_cuda should use mulmat for torch 2.10.0"


# [pr_diff] fail_to_pass
def test_torch_2_15_dev_uses_mulmat():
    """forward_cuda uses mulmat path for future dev versions (>= 2.9.0)."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.15.0.dev20260101") == "mulmat", \
        "forward_cuda should use mulmat for torch 2.15.0.dev"


# [pr_diff] fail_to_pass
def test_torch_2_9_2_uses_mulmat():
    """forward_cuda uses mulmat path for torch 2.9.2 (>= 2.9.0 but not exact 2.9.0/2.9.1)."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.9.2") == "mulmat", \
        "forward_cuda should use mulmat for torch 2.9.2"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — boundary & regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_torch_2_9_0_uses_mulmat():
    """forward_cuda uses mulmat path for torch 2.9.0 (exact lower boundary)."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.9.0") == "mulmat", \
        "forward_cuda should use mulmat for torch 2.9.0"


# [pr_diff] pass_to_pass
def test_torch_2_8_uses_conv():
    """forward_cuda uses conv path for torch < 2.9.0 (not affected by CUDNN bug)."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.8.0") == "conv", \
        "forward_cuda should use conv for torch 2.8.0"


# [pr_diff] pass_to_pass
def test_torch_2_8_1_uses_conv():
    """forward_cuda uses conv path for torch 2.8.1."""
    layer = _make_layer()
    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.8.1") == "conv", \
        "forward_cuda should use conv for torch 2.8.1"


# [pr_diff] pass_to_pass
def test_enable_linear_false_uses_conv():
    """forward_cuda uses conv path when enable_linear=False regardless of torch version."""
    layer = _make_layer(enable_linear=False)
    assert not layer.enable_linear, "enable_linear should be False for kernel_size != stride"

    x = torch.randn(1, 2, 4, 4, 4)
    assert _get_path_taken(layer, x, "2.10.0") == "conv", \
        "forward_cuda should use conv when enable_linear=False"


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """forward_cuda has conditional logic with multiple return paths (not stubbed)."""
    import ast

    src = open(REPO + "/vllm/model_executor/layers/conv.py").read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Conv3dLayer":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "forward_cuda":
                    has_if = any(isinstance(n, ast.If) for n in ast.walk(item))
                    returns = [n for n in ast.walk(item) if isinstance(n, ast.Return)]
                    assert has_if, "forward_cuda must contain conditional logic"
                    assert len(returns) >= 2, "forward_cuda must have multiple return paths"
                    return
    raise AssertionError("Conv3dLayer.forward_cuda not found")


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests (p2p_enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_conv():
    """Repo's ruff linting passes on conv.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "vllm/model_executor/layers/conv.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_conv():
    """Repo's ruff format check passes on conv.py (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "vllm/model_executor/layers/conv.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"
