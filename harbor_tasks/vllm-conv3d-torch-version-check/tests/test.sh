#!/usr/bin/env bash
set -euo pipefail

REPO="${REPO:-/repo}"
TOTAL=0.0
RESULTS="{}"
TARGET="$REPO/vllm/model_executor/layers/conv.py"

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (0.00): conv.py must be valid Python
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())"; then
    echo "GATE FAILED: $TARGET has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: syntax OK"

########################################################################
# Helper: run an inline Python test, capture exit code
########################################################################
run_py_test() {
    local desc="$1"
    local weight="$2"
    shift 2
    # remaining args are the python script via heredoc
    if python3 "$@" 2>&1; then
        echo "  PASS ($weight): $desc"
        TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    else
        echo "  FAIL ($weight): $desc"
    fi
}

########################################################################
# Behavioral tests: call forward_cuda with mocked torch versions
########################################################################
# We mock the vllm import chain so Conv3dLayer can be imported with
# CPU-only torch. Then we patch torch.__version__ before calling
# forward_cuda to simulate different PyTorch versions.

MOCK_PREAMBLE=$(cat <<'PYEOF'
import sys, types, math
import torch
import torch.nn as nn
import torch.nn.functional as F
from packaging import version as pkg_version

REPO = "/repo"
sys.path.insert(0, REPO)

# --- Mock heavy vllm imports ---
for mod_name in [
    "vllm", "vllm.envs", "vllm.logger", "vllm.platforms",
    "vllm.sequence", "vllm.model_executor",
    "vllm.model_executor.custom_op", "vllm.model_executor.layers",
    "vllm.utils",
]:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = types.ModuleType(mod_name)

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

# Provide a fake logger
class FakeLogger:
    def __getattr__(self, name):
        return lambda *a, **kw: None

sys.modules["vllm.logger"].init_logger = lambda name: FakeLogger()
sys.modules["vllm.envs"].CUDA_VISIBLE_DEVICES = None

# Now import conv module
from vllm.model_executor.layers.conv import Conv3dLayer
PYEOF
)

# --- F2P Test 1: torch 2.10.0 should use mulmat path ---
# [pr_diff] (0.40): Conv3d forward_cuda uses mulmat for torch >= 2.10.0
run_py_test "torch 2.10.0 -> mulmat path" 0.40 -c "$MOCK_PREAMBLE
import torch

# Create layer with enable_linear=True (kernel_size == stride, no padding, groups=1)
layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=2, stride=2)
# Initialize weights deterministically
torch.manual_seed(42)
nn.init.normal_(layer.weight)
nn.init.zeros_(layer.bias)

x = torch.randn(1, 2, 4, 4, 4)

# Get reference outputs
mulmat_ref = layer._forward_mulmat(x.clone())
conv_ref = layer._forward_conv(x.clone())

# Patch torch version to 2.10.0
original_version = torch.__version__
torch.__version__ = '2.10.0'

result = layer.forward_cuda(x.clone())

torch.__version__ = original_version

# Fixed code: is_torch_equal_or_newer('2.9.0') with '2.10.0' -> True -> mulmat
# Buggy code: is_torch_equal('2.9.0') with '2.10.0' -> False -> conv
assert torch.allclose(result, mulmat_ref, atol=1e-6), \
    'forward_cuda should use mulmat for torch 2.10.0 (>= 2.9.0)'
"

# --- F2P Test 2: torch 2.15.0.dev should use mulmat path ---
# [pr_diff] (0.25): Conv3d forward_cuda uses mulmat for future torch versions
run_py_test "torch 2.15.0.dev -> mulmat path" 0.25 -c "$MOCK_PREAMBLE
import torch

layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=2, stride=2)
torch.manual_seed(42)
nn.init.normal_(layer.weight)
nn.init.zeros_(layer.bias)

x = torch.randn(1, 2, 4, 4, 4)
mulmat_ref = layer._forward_mulmat(x.clone())

original_version = torch.__version__
torch.__version__ = '2.15.0.dev20260101'

result = layer.forward_cuda(x.clone())

torch.__version__ = original_version

assert torch.allclose(result, mulmat_ref, atol=1e-6), \
    'forward_cuda should use mulmat for torch 2.15.0.dev (>= 2.9.0)'
"

# --- P2P Test 1: torch 2.8.0 should NOT use mulmat ---
# [pr_diff] (0.10): Conv3d forward_cuda uses conv for torch < 2.9.0
run_py_test "torch 2.8.0 -> conv path" 0.10 -c "$MOCK_PREAMBLE
import torch

layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=2, stride=2)
torch.manual_seed(42)
nn.init.normal_(layer.weight)
nn.init.zeros_(layer.bias)

x = torch.randn(1, 2, 4, 4, 4)
conv_ref = layer._forward_conv(x.clone())

original_version = torch.__version__
torch.__version__ = '2.8.0'

result = layer.forward_cuda(x.clone())

torch.__version__ = original_version

assert torch.allclose(result, conv_ref, atol=1e-6), \
    'forward_cuda should use conv for torch 2.8.0 (< 2.9.0)'
"

# --- P2P Test 2: enable_linear=False -> always conv path ---
# [pr_diff] (0.10): Conv3d forward_cuda uses conv when enable_linear=False
run_py_test "enable_linear=False -> conv path" 0.10 -c "$MOCK_PREAMBLE
import torch

# Non-matching kernel_size and stride -> enable_linear=False
layer = Conv3dLayer(in_channels=2, out_channels=4, kernel_size=3, stride=1, padding=1)
torch.manual_seed(42)
nn.init.normal_(layer.weight)
nn.init.zeros_(layer.bias)

assert not layer.enable_linear, 'enable_linear should be False for kernel_size != stride'

x = torch.randn(1, 2, 4, 4, 4)
conv_ref = layer._forward_conv(x.clone())

original_version = torch.__version__
torch.__version__ = '2.10.0'

result = layer.forward_cuda(x.clone())

torch.__version__ = original_version

assert torch.allclose(result, conv_ref, atol=1e-6), \
    'forward_cuda should use conv when enable_linear=False regardless of torch version'
"

########################################################################
# Structural: anti-stub check
########################################################################
# [pr_diff] (0.10): forward_cuda body is non-trivial (not stubbed out)
# WHY AST: forward_cuda contains version-check logic that we verify structurally
# to ensure the method wasn't replaced with a trivial stub
echo ""
echo "=== Structural checks ==="
if python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Conv3dLayer':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward_cuda':
                # Must have at least an if-statement and two return statements
                has_if = any(isinstance(n, ast.If) for n in ast.walk(item))
                returns = [n for n in ast.walk(item) if isinstance(n, ast.Return)]
                assert has_if, 'forward_cuda must contain conditional logic'
                assert len(returns) >= 2, 'forward_cuda must have multiple return paths'
                print('Anti-stub check passed')
                exit(0)

print('Conv3dLayer.forward_cuda not found')
exit(1)
" 2>&1; then
    echo "  PASS (0.10): forward_cuda is non-trivial"
    TOTAL=$(python3 -c "print(round($TOTAL + 0.10, 4))")
else
    echo "  FAIL (0.10): forward_cuda appears stubbed or missing"
fi

########################################################################
# Config-derived: ruff formatting check
########################################################################
# [agent_config] (0.05): "Run all pre-commit hooks" — AGENTS.md:82-83 @ bea23536f6
echo ""
echo "=== Config-derived checks ==="
if command -v ruff &>/dev/null; then
    if ruff check "$TARGET" --select E,W --quiet 2>&1; then
        echo "  PASS (0.05): ruff check passes on conv.py"
        TOTAL=$(python3 -c "print(round($TOTAL + 0.05, 4))")
    else
        echo "  FAIL (0.05): ruff check found issues"
    fi
else
    echo "  SKIP (0.05): ruff not available"
    TOTAL=$(python3 -c "print(round($TOTAL + 0.05, 4))")
fi

########################################################################
# Final score
########################################################################
echo ""
echo "=== Final Score: $TOTAL ==="
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
total = $TOTAL
data = {'reward': total}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
