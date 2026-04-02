"""
Task: vllm-conch-3d-input-reshape
Repo: vllm-project/vllm @ b9dbc5c4ab2b01f626376ffaeb68e575e70ff58c
PR:   38178

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
import types
import torch
from unittest.mock import MagicMock

FILE = "/workspace/vllm/model_executor/kernels/linear/mixed_precision/conch.py"
OUT_N = 64


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

class FakeConfig:
    def __init__(self):
        wt = MagicMock()
        wt.size_bits = 4
        wt.bias = 0
        self.weight_type = wt
        self.group_size = 128
        self.zero_points = False
        self.partition_weight_shape = (128, OUT_N)


class FakeMPLinearKernel:
    def __init__(self):
        self.config = FakeConfig()
        self.w_q_name = "w_q"
        self.w_s_name = "w_s"
        self.w_zp_name = "w_zp"

    def _get_weight_params(self, layer):
        return (layer.w_q, layer.w_s, None, None)

    @classmethod
    def get_min_capability(cls):
        return 80

    def _transform_param(self, layer, name, fn):
        pass


class FakeLayerConfig:
    pass


def setup_mock_gemm(gemm_fn):
    """Register a mock conch GEMM and return the module namespace."""
    conch_gemm = types.ModuleType("conch.ops.quantization.gemm")
    conch_gemm.mixed_precision_gemm = gemm_fn
    sys.modules["conch"] = types.ModuleType("conch")
    sys.modules["conch.ops"] = types.ModuleType("conch.ops")
    sys.modules["conch.ops.quantization"] = types.ModuleType("conch.ops.quantization")
    sys.modules["conch.ops.quantization.gemm"] = conch_gemm


def load_conch_kernel():
    """Load ConchLinearKernel from the source file with mocked imports."""
    with open(FILE) as f:
        source = f.read()
    source = source.replace("from importlib.util import find_spec", "")
    source = source.replace(
        "from vllm.model_executor.parameter import BasevLLMParameter, permute_param_layout_",
        "BasevLLMParameter = object; permute_param_layout_ = lambda *a, **k: None",
    )
    source = source.replace(
        "from vllm.scalar_type import scalar_types",
        "from unittest.mock import MagicMock; scalar_types = MagicMock()",
    )
    source = source.replace(
        "from .MPLinearKernel import MPLinearKernel, MPLinearLayerConfig",
        "",
    )
    ns = {
        "__builtins__": __builtins__,
        "torch": torch,
        "find_spec": lambda x: True,
        "Final": type,
        "MPLinearKernel": FakeMPLinearKernel,
        "MPLinearLayerConfig": FakeLayerConfig,
    }
    exec(compile(source, FILE, "exec"), ns)
    return ns["ConchLinearKernel"]


def make_layer():
    """Create a mock layer with weight tensors."""
    layer = MagicMock()
    layer.w_q = MagicMock()
    layer.w_q.data = torch.randn(32, OUT_N)
    layer.w_s = MagicMock()
    layer.w_s.data = torch.randn(1, OUT_N)
    return layer


def _default_mock_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
    return torch.randn(x.shape[0], OUT_N)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """conch.py must be valid Python."""
    import ast

    with open(FILE) as f:
        source = f.read()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_3d_input_produces_3d_output():
    """3D input (batch, seq_len, hidden) must produce 3D output with correct shape."""
    setup_mock_gemm(_default_mock_gemm)
    ConchLinearKernel = load_conch_kernel()
    kernel = ConchLinearKernel()
    layer = make_layer()

    # Test multiple 3D shapes
    for batch, seq_len, hidden in [(2, 3, 128), (1, 7, 128), (4, 1, 128)]:
        x_3d = torch.randn(batch, seq_len, hidden)
        out = kernel.apply_weights(layer, x_3d)
        assert out.shape == (batch, seq_len, OUT_N), (
            f"Expected ({batch}, {seq_len}, {OUT_N}), got {tuple(out.shape)}"
        )


# [pr_diff] fail_to_pass
def test_gemm_receives_flattened_2d():
    """mixed_precision_gemm must receive a 2D tensor even for 3D input."""
    gemm_record = {}

    def recording_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
        gemm_record["x_shape"] = tuple(x.shape)
        gemm_record["x_ndim"] = x.ndim
        return torch.randn(x.shape[0], OUT_N)

    setup_mock_gemm(recording_gemm)
    ConchLinearKernel = load_conch_kernel()
    kernel = ConchLinearKernel()
    layer = make_layer()

    for batch, seq_len in [(2, 3), (1, 5), (3, 4)]:
        x_3d = torch.randn(batch, seq_len, 128)
        kernel.apply_weights(layer, x_3d)
        assert gemm_record["x_ndim"] == 2, (
            f"GEMM got {gemm_record['x_ndim']}D input, expected 2D"
        )
        expected_m = batch * seq_len
        assert gemm_record["x_shape"][0] == expected_m, (
            f"Expected M={expected_m}, got {gemm_record['x_shape'][0]}"
        )


# [pr_diff] fail_to_pass
def test_value_preservation_through_reshape():
    """Reshape round-trip must preserve output values in correct positions."""

    def deterministic_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
        M = x.shape[0]
        return torch.arange(M).float().unsqueeze(1).expand(M, OUT_N).clone()

    setup_mock_gemm(deterministic_gemm)
    ConchLinearKernel = load_conch_kernel()
    kernel = ConchLinearKernel()
    layer = make_layer()

    for batch, seq_len in [(2, 4), (3, 2)]:
        x_3d = torch.randn(batch, seq_len, 128)
        out = kernel.apply_weights(layer, x_3d)
        assert out.shape == (batch, seq_len, OUT_N)

        for b in range(batch):
            for s in range(seq_len):
                expected_val = float(b * seq_len + s)
                row = out[b, s, :]
                assert torch.allclose(row, torch.full((OUT_N,), expected_val)), (
                    f"out[{b},{s},:] expected {expected_val}, got {row[0].item()}"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass -- regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_2d_input_still_works():
    """2D input (M, K) must still produce correct 2D output (backward compat)."""
    setup_mock_gemm(_default_mock_gemm)
    ConchLinearKernel = load_conch_kernel()
    kernel = ConchLinearKernel()
    layer = make_layer()

    for m in [1, 6, 16]:
        x_2d = torch.randn(m, 128)
        out = kernel.apply_weights(layer, x_2d)
        assert out.shape == (m, OUT_N), (
            f"Expected ({m}, {OUT_N}), got {tuple(out.shape)}"
        )
        assert out.ndim == 2, f"Expected 2D output, got {out.ndim}D"


# [static] pass_to_pass
def test_not_stub():
    """apply_weights must contain real reshape logic, not a stub."""
    import ast

    with open(FILE) as f:
        source = f.read()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "apply_weights":
            body_stmts = [
                s for s in node.body
                if not isinstance(s, (ast.Pass, ast.Expr))
            ]
            assert len(body_stmts) >= 3, "apply_weights body is too short to be a real implementation"
            return

    assert False, "apply_weights function not found in conch.py"
