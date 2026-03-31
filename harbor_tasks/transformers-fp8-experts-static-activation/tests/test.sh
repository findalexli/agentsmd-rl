#!/usr/bin/env bash
set +e

TOTAL=0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd /repo

# Shared test setup (triton mock + FakeConfig)
cat > /tmp/fp8_test_setup.py << 'PYEOF'
import torch, sys, types
triton_mock = types.ModuleType('triton')
triton_mock.cdiv = lambda a, b: (a + b - 1) // b
triton_mock.jit = lambda **kw: (lambda fn: fn)
sys.modules.setdefault('triton', triton_mock)

class FakeConfig:
    hidden_size = 64
    num_local_experts = 4
    moe_intermediate_size = 128
    hidden_act = 'silu'
PYEOF

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0): Python syntax valid
python3 -c "
import py_compile, sys
try:
    py_compile.compile('src/transformers/integrations/finegrained_fp8.py', doraise=True)
except py_compile.PyCompileError as e:
    print(f'GATE FAIL: {e}', file=sys.stderr)
    sys.exit(1)
print('GATE: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

###############################################################################
# Fail-to-pass: FP8Experts accepts activation_scheme="static"
###############################################################################
# [pr_diff] (0.25): FP8Experts can be constructed with static activation scheme
if python3 -c "
exec(open('/tmp/fp8_test_setup.py').read())
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')
print('OK')
" 2>/dev/null; then
    echo "PASS (0.25): FP8Experts accepts activation_scheme=static"
    add 0.25
else
    echo "FAIL (0.25): FP8Experts crashes with activation_scheme=static"
fi

###############################################################################
# Fail-to-pass: Static activation scale parameters registered with correct shape
###############################################################################
# [pr_diff] (0.15): gate_up and down activation scale params exist, shape (num_experts,), float32
if python3 -c "
exec(open('/tmp/fp8_test_setup.py').read())
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')
    param_names = [n for n, _ in module.named_parameters()]
    assert 'gate_up_proj_activation_scale' in param_names, \
        f'Missing gate_up_proj_activation_scale, got: {param_names}'
    assert 'down_proj_activation_scale' in param_names, \
        f'Missing down_proj_activation_scale, got: {param_names}'
    gu = module.gate_up_proj_activation_scale
    dp = module.down_proj_activation_scale
    assert gu.shape == (4,), f'gate_up scale shape {gu.shape} != (4,)'
    assert dp.shape == (4,), f'down scale shape {dp.shape} != (4,)'
    assert gu.dtype == torch.float32, f'gate_up scale dtype {gu.dtype}'
    assert dp.dtype == torch.float32, f'down scale dtype {dp.dtype}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.15): static activation scale parameters correct"
    add 0.15
else
    echo "FAIL (0.15): static activation scale parameters missing or wrong"
fi

###############################################################################
# Fail-to-pass: linear() with static scheme quantizes input to FP8 dtype
###############################################################################
# [pr_diff] (0.25): linear() accepts activation_scale and quantizes input to FP8
# Mocks w8a8_fp8_matmul (Triton GPU kernel) to capture quantized input
if python3 -c "
exec(open('/tmp/fp8_test_setup.py').read())
from unittest.mock import patch

with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')

captured = {}
def mock_matmul(*args, **kwargs):
    captured['qinput'] = args[0]
    captured['input_scale'] = args[2]
    return torch.zeros(args[0].shape[0], args[1].shape[0], dtype=torch.float32)

with patch('transformers.integrations.finegrained_fp8.w8a8_fp8_matmul', mock_matmul):
    inp = torch.randn(4, 64)
    weight = torch.zeros(128, 64, dtype=torch.float8_e4m3fn)
    weight_scale = torch.ones(128)
    act_scale = torch.tensor(2.0)

    result = module.linear(inp, weight, weight_scale, activation_scale=act_scale)

    # The quantized input must be FP8 dtype (proves static quantization happened)
    fp8_types = (torch.float8_e4m3fn, torch.float8_e5m2)
    if hasattr(torch, 'float8_e4m3fnuz'):
        fp8_types = fp8_types + (torch.float8_e4m3fnuz,)
    assert captured['qinput'].dtype in fp8_types, \
        f'Expected FP8 dtype for quantized input, got {captured[\"qinput\"].dtype}'

    # The activation scale must be propagated to the matmul
    assert captured['input_scale'] is not None, 'Activation scale not passed to matmul'

print('OK')
" 2>/dev/null; then
    echo "PASS (0.25): linear() static quantization produces FP8 input"
    add 0.25
else
    echo "FAIL (0.25): linear() static quantization broken"
fi

###############################################################################
# Fail-to-pass: linear() actually uses the provided scale value
###############################################################################
# [pr_diff] (0.10): Changing activation_scale changes the quantized output
if python3 -c "
exec(open('/tmp/fp8_test_setup.py').read())
from unittest.mock import patch

with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='static')

results = []
for scale_val in [1.0, 4.0]:
    captured = {}
    def mock_matmul(*args, **kwargs):
        captured['qinput'] = args[0]
        return torch.zeros(args[0].shape[0], args[1].shape[0], dtype=torch.float32)

    with patch('transformers.integrations.finegrained_fp8.w8a8_fp8_matmul', mock_matmul):
        inp = torch.full((2, 64), 8.0)
        weight = torch.zeros(128, 64, dtype=torch.float8_e4m3fn)
        weight_scale = torch.ones(128)
        act_scale = torch.tensor(scale_val)
        module.linear(inp, weight, weight_scale, activation_scale=act_scale)
        results.append(captured['qinput'].float().clone())

# Different scales must produce different quantized values
# scale=1 -> qinput ~ 8.0, scale=4 -> qinput ~ 2.0
assert not torch.equal(results[0], results[1]), \
    'Changing activation_scale did not change quantized input — scale is ignored'

# Larger scale should produce smaller quantized values (input / scale)
assert results[1].abs().mean() < results[0].abs().mean(), \
    f'Larger scale should produce smaller quantized values: scale=1 mean={results[0].abs().mean():.2f}, scale=4 mean={results[1].abs().mean():.2f}'

print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): linear() correctly uses activation scale value"
    add 0.10
else
    echo "FAIL (0.10): linear() does not use activation scale correctly"
fi

###############################################################################
# Pass-to-pass: Dynamic mode still works (no static params registered)
###############################################################################
# [pr_diff] (0.10): FP8Experts with dynamic mode constructs without static params
if python3 -c "
exec(open('/tmp/fp8_test_setup.py').read())
with torch.device('meta'):
    from transformers.integrations.finegrained_fp8 import FP8Experts
    module = FP8Experts(FakeConfig(), activation_scheme='dynamic')
    param_names = [n for n, _ in module.named_parameters()]
    assert 'gate_up_proj' in param_names, 'Missing gate_up_proj'
    assert 'down_proj' in param_names, 'Missing down_proj'
    # Dynamic mode should NOT register activation_scale params
    assert 'gate_up_proj_activation_scale' not in param_names, \
        'Dynamic mode should not have gate_up_proj_activation_scale'
    assert 'down_proj_activation_scale' not in param_names, \
        'Dynamic mode should not have down_proj_activation_scale'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): dynamic mode still works correctly"
    add 0.10
else
    echo "FAIL (0.10): dynamic mode broken"
fi

###############################################################################
# Structural: forward() passes activation_scale keyword to linear() calls
###############################################################################
# [pr_diff] (0.05): forward method passes activation_scale as keyword arg
# WHY AST: forward() chains through linear() to Triton kernel — cannot run on CPU
if python3 -c "
import ast, sys

with open('src/transformers/integrations/finegrained_fp8.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'FP8Experts':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                # Check for activation_scale as a keyword argument in Call nodes
                kwarg_count = 0
                for call_node in ast.walk(item):
                    if isinstance(call_node, ast.Call):
                        for kw in call_node.keywords:
                            if kw.arg == 'activation_scale':
                                kwarg_count += 1
                assert kwarg_count >= 1, \
                    'forward() does not pass activation_scale as keyword arg to any call'
                print('OK')
                sys.exit(0)

print('FP8Experts.forward not found', file=sys.stderr)
sys.exit(1)
" 2>/dev/null; then
    echo "PASS (0.05): forward() passes activation_scale keyword"
    add 0.05
else
    echo "FAIL (0.05): forward() missing activation_scale keyword arg"
fi

###############################################################################
# Structural: set_device calls via AST (not gameable with comments)
###############################################################################
# [pr_diff] (0.05): set_device calls in multi-GPU code paths
# WHY AST: multi-GPU set_device cannot be tested on single-CPU container
if python3 -c "
import ast, sys

with open('src/transformers/integrations/finegrained_fp8.py') as f:
    tree = ast.parse(f.read())

# Count actual set_device method calls in the AST (not string matches)
set_device_count = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'set_device':
            set_device_count += 1

assert set_device_count >= 2, \
    f'Expected >=2 set_device() calls in AST, found {set_device_count}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): set_device calls present (AST-verified)"
    add 0.05
else
    echo "FAIL (0.05): missing set_device calls"
fi

###############################################################################
# Config: ruff check on changed file
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — .github/copilot-instructions.md:15 @ f619594
if command -v ruff &>/dev/null; then
    if ruff check src/transformers/integrations/finegrained_fp8.py --quiet 2>/dev/null; then
        echo "PASS (0.05): ruff check passes"
        add 0.05
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    echo "SKIP (0.05): ruff not installed, awarding points"
    add 0.05
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
