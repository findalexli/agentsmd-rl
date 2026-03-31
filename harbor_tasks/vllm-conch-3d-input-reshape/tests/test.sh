#!/usr/bin/env bash
set +e

SCORE=0
FILE="/workspace/vllm/model_executor/kernels/linear/mixed_precision/conch.py"

########################################################################
# Helper: shared mock setup written to a temp file to avoid duplication
########################################################################
cat > /tmp/conch_test_helpers.py << 'HELPEOF'
import sys, types, torch
from unittest.mock import MagicMock

FILE = "/workspace/vllm/model_executor/kernels/linear/mixed_precision/conch.py"
OUT_N = 64

def setup_mock_gemm(gemm_fn):
    """Register a mock conch GEMM and return the module namespace."""
    conch_gemm = types.ModuleType('conch.ops.quantization.gemm')
    conch_gemm.mixed_precision_gemm = gemm_fn
    sys.modules['conch'] = types.ModuleType('conch')
    sys.modules['conch.ops'] = types.ModuleType('conch.ops')
    sys.modules['conch.ops.quantization'] = types.ModuleType('conch.ops.quantization')
    sys.modules['conch.ops.quantization.gemm'] = conch_gemm

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
        self.w_q_name = 'w_q'
        self.w_s_name = 'w_s'
        self.w_zp_name = 'w_zp'
    def _get_weight_params(self, layer):
        return (layer.w_q, layer.w_s, None, None)
    @classmethod
    def get_min_capability(cls):
        return 80
    def _transform_param(self, layer, name, fn):
        pass

class FakeLayerConfig:
    pass

def load_conch_kernel():
    """Load ConchLinearKernel from the source file with mocked imports."""
    with open(FILE) as f:
        source = f.read()
    source = source.replace("from importlib.util import find_spec", "")
    source = source.replace(
        "from vllm.model_executor.parameter import BasevLLMParameter, permute_param_layout_",
        "BasevLLMParameter = object; permute_param_layout_ = lambda *a, **k: None"
    )
    source = source.replace(
        "from vllm.scalar_type import scalar_types",
        "from unittest.mock import MagicMock; scalar_types = MagicMock()"
    )
    source = source.replace(
        "from .MPLinearKernel import MPLinearKernel, MPLinearLayerConfig",
        ""
    )
    ns = {
        '__builtins__': __builtins__,
        'torch': torch,
        'find_spec': lambda x: True,
        'Final': type,
        'MPLinearKernel': FakeMPLinearKernel,
        'MPLinearLayerConfig': FakeLayerConfig,
    }
    exec(compile(source, FILE, 'exec'), ns)
    return ns['ConchLinearKernel']

def make_layer():
    """Create a mock layer with weight tensors."""
    layer = MagicMock()
    layer.w_q = MagicMock()
    layer.w_q.data = torch.randn(32, OUT_N)
    layer.w_s = MagicMock()
    layer.w_s.data = torch.randn(1, OUT_N)
    return layer
HELPEOF

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$FILE').read())"; then
    echo "GATE FAILED: syntax error in conch.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASSED: syntax OK"

########################################################################
# Behavioral test 1 (fail-to-pass): 3D input produces correct 3D output
########################################################################
# [pr_diff] (0.35): 3D input (batch, seq_len, hidden) must produce 3D output
RESULT=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
import torch
from conch_test_helpers import setup_mock_gemm, load_conch_kernel, make_layer, OUT_N

gemm_record = {}
def mock_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
    gemm_record['x_shape'] = tuple(x.shape)
    return torch.randn(x.shape[0], OUT_N)

setup_mock_gemm(mock_gemm)

try:
    ConchLinearKernel = load_conch_kernel()
except Exception as e:
    print(f"EXEC_FAIL: {e}")
    sys.exit(0)

kernel = ConchLinearKernel()
layer = make_layer()

# Test with 3D input: (batch=2, seq_len=3, hidden=128)
x_3d = torch.randn(2, 3, 128)
try:
    out = kernel.apply_weights(layer, x_3d)
    if out.shape == (2, 3, OUT_N):
        print("PASS_3D")
    else:
        print(f"WRONG_SHAPE: expected (2, 3, {OUT_N}), got {tuple(out.shape)}")
except Exception as e:
    print(f"FAIL_3D: {e}")
PYEOF
)

if [[ "$RESULT" == "PASS_3D" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.35)")
    echo "BEHAVIORAL 1 PASSED: 3D input produces correct 3D output"
else
    echo "BEHAVIORAL 1 FAILED: $RESULT"
fi

########################################################################
# Behavioral test 2 (fail-to-pass): GEMM receives flattened 2D input
########################################################################
# [pr_diff] (0.30): mixed_precision_gemm must receive a 2D tensor even for 3D input
RESULT2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
import torch
from conch_test_helpers import setup_mock_gemm, load_conch_kernel, make_layer, OUT_N

gemm_record = {}
def mock_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
    gemm_record['x_shape'] = tuple(x.shape)
    gemm_record['x_ndim'] = x.ndim
    return torch.randn(x.shape[0], OUT_N)

setup_mock_gemm(mock_gemm)

try:
    ConchLinearKernel = load_conch_kernel()
except Exception as e:
    print(f"EXEC_FAIL: {e}")
    sys.exit(0)

kernel = ConchLinearKernel()
layer = make_layer()

x_3d = torch.randn(2, 3, 128)
try:
    kernel.apply_weights(layer, x_3d)
    if gemm_record.get('x_ndim') == 2:
        expected_m = 2 * 3
        if gemm_record['x_shape'][0] == expected_m:
            print("PASS_2D")
        else:
            print(f"WRONG_M: expected M={expected_m}, got {gemm_record['x_shape'][0]}")
    else:
        print(f"FAIL_NDIM: GEMM got {gemm_record.get('x_ndim')}D input")
except Exception as e:
    print(f"FAIL_GEMM: {e}")
PYEOF
)

if [[ "$RESULT2" == "PASS_2D" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.30)")
    echo "BEHAVIORAL 2 PASSED: GEMM receives 2D input for 3D tensor"
else
    echo "BEHAVIORAL 2 FAILED: $RESULT2"
fi

########################################################################
# Pass-to-pass: 2D input still works correctly
########################################################################
# [pr_diff] (0.15): 2D input (M, K) must still produce correct 2D output
RESULT3=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
import torch
from conch_test_helpers import setup_mock_gemm, load_conch_kernel, make_layer, OUT_N

def mock_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
    return torch.randn(x.shape[0], OUT_N)

setup_mock_gemm(mock_gemm)

try:
    ConchLinearKernel = load_conch_kernel()
except Exception as e:
    print(f"EXEC_FAIL: {e}")
    sys.exit(0)

kernel = ConchLinearKernel()
layer = make_layer()

# 2D input: (M=6, K=128)
x_2d = torch.randn(6, 128)
try:
    out = kernel.apply_weights(layer, x_2d)
    if out.shape == (6, OUT_N):
        print("PASS_2D")
    else:
        print(f"WRONG_SHAPE: expected (6, {OUT_N}), got {tuple(out.shape)}")
except Exception as e:
    print(f"FAIL_2D: {e}")
PYEOF
)

if [[ "$RESULT3" == "PASS_2D" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "PASS-TO-PASS PASSED: 2D input still works"
else
    echo "PASS-TO-PASS FAILED: $RESULT3"
fi

########################################################################
# Behavioral test 3 (fail-to-pass): value preservation through reshape
# Tests that data is not corrupted by the flatten→GEMM→unflatten cycle.
# The mock GEMM returns a deterministic output; we verify the 3D result
# contains the correct values in the correct positions.
########################################################################
# [pr_diff] (0.20): reshape round-trip must preserve output values correctly
RESULT4=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
import torch
from conch_test_helpers import setup_mock_gemm, load_conch_kernel, make_layer, OUT_N

# GEMM returns row index as every element so we can verify reshape ordering
def mock_gemm(x, w_q_packed, w_s, w_zp, weight_size_bits, weight_bias, group_size):
    M = x.shape[0]
    # Return a tensor where row i is filled with float(i)
    return torch.arange(M).float().unsqueeze(1).expand(M, OUT_N).clone()

setup_mock_gemm(mock_gemm)

try:
    ConchLinearKernel = load_conch_kernel()
except Exception as e:
    print(f"EXEC_FAIL: {e}")
    sys.exit(0)

kernel = ConchLinearKernel()
layer = make_layer()

# 3D input: (batch=2, seq_len=4, hidden=128)
x_3d = torch.randn(2, 4, 128)
try:
    out = kernel.apply_weights(layer, x_3d)
    if out.ndim != 3 or out.shape != (2, 4, OUT_N):
        print(f"WRONG_SHAPE: {tuple(out.shape)}")
        sys.exit(0)

    # Verify values: out[b, s, :] should all equal (b * 4 + s)
    ok = True
    for b in range(2):
        for s in range(4):
            expected_val = float(b * 4 + s)
            row = out[b, s, :]
            if not torch.allclose(row, torch.full((OUT_N,), expected_val)):
                print(f"VALUE_MISMATCH: out[{b},{s},:] expected {expected_val}, got {row[0].item()}")
                ok = False
                break
        if not ok:
            break
    if ok:
        print("PASS_VALUES")
except Exception as e:
    print(f"FAIL_VALUES: {e}")
PYEOF
)

if [[ "$RESULT4" == "PASS_VALUES" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    echo "BEHAVIORAL 3 PASSED: value preservation through reshape"
else
    echo "BEHAVIORAL 3 FAILED: $RESULT4"
fi

########################################################################
# Final score
########################################################################
echo "---"
echo "Total score: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
