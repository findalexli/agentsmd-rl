#!/usr/bin/env bash
set -uo pipefail

SCORE=0
REPO="/workspace/slime"
BRIDGE="$REPO/slime_plugins/mbridge/glm4moe_lite.py"
PROVIDER="$REPO/slime/backends/megatron_utils/model_provider.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): Modified files must be valid Python
if ! python3 -c "import ast; ast.parse(open('$BRIDGE').read())" 2>/dev/null; then
    echo "FAIL: Syntax error in glm4moe_lite.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
if ! python3 -c "import ast; ast.parse(open('$PROVIDER').read())" 2>/dev/null; then
    echo "FAIL: Syntax error in model_provider.py"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: Syntax OK"

# Write shared mock setup that mocks heavy deps (mbridge, torch, megatron)
# and loads + instantiates the actual bridge class with a GLM-4.7-Flash config.
cat > /tmp/bridge_mock_setup.py << 'MOCKEOF'
import sys, types

# Mock torch (needed by the bridge file's `import torch`)
_torch = types.ModuleType('torch')
class _FakeTensor:
    pass
_torch.Tensor = _FakeTensor
sys.modules['torch'] = _torch

# Mock mbridge package hierarchy
for _mod_name in ['mbridge', 'mbridge.core', 'mbridge.models', 'mbridge.core.safetensor_io']:
    sys.modules[_mod_name] = types.ModuleType(_mod_name)

def _register_model(name):
    def decorator(cls):
        return cls
    return decorator
sys.modules['mbridge.core'].register_model = _register_model

class MockSafeTensorIO:
    """Mock standard bf16 loader."""
    def __init__(self, path):
        self.path = path
sys.modules['mbridge.core.safetensor_io'].SafeTensorIO = MockSafeTensorIO

class MockDeepseekV3Bridge:
    """Mock parent with hardcoded layer 61 — the exact bug being fixed.
    If the child just inherits (stub), these hardcoded values will propagate."""
    _SHARED_STATE_DICT_MAPPING = {
        'embedding.word_embeddings.weight': [
            'model.embed_tokens.weight',
            'model.layers.61.embed_tokens.weight',
        ],
        'output_layer.weight': [
            'lm_head.weight',
            'model.layers.61.shared_head.head.weight',
        ],
    }

    def __init__(self, hf_config, **kwargs):
        self.hf_config = hf_config
        self.config = types.SimpleNamespace(
            num_layers=hf_config.num_hidden_layers,
            mtp_num_layers=getattr(hf_config, 'num_nextn_predict_layers', 0),
            hidden_size=4096,
        )

    def _convert_mtp_param(self, name):
        """Parent hardcodes layer 61 for DeepSeek V3."""
        _direct = {
            'mtp.layers.0.enorm.weight': 'model.layers.61.enorm.weight',
            'mtp.layers.0.hnorm.weight': 'model.layers.61.hnorm.weight',
            'mtp.layers.0.eh_proj.weight': 'model.layers.61.eh_proj.weight',
            'mtp.layers.0.final_layernorm.weight': 'model.layers.61.shared_head.norm.weight',
        }
        if name in _direct:
            return [_direct[name]]
        return [name.replace('mtp.layers.0.transformer_layer', 'decoder.layers.61')]

    def _get_safetensor_io(self, path):
        """Parent uses FP8 dequant — wrong for GLM-4.7-Flash bf16 weights."""
        return 'FP8_DEQUANT_LOADER'

    def _get_actual_hf_path(self, path):
        return path

    def _weight_name_mapping_attention(self, name):
        return [name]

    def _weight_name_mapping_mlp(self, name):
        return [name]

    def _weight_to_hf_format(self, name, weights):
        if name in self._SHARED_STATE_DICT_MAPPING:
            hf_names = self._SHARED_STATE_DICT_MAPPING[name]
            return hf_names, [weights] * len(hf_names)
        return [name], [weights]

sys.modules['mbridge.models'].DeepseekV3Bridge = MockDeepseekV3Bridge

# Load the ACTUAL bridge file with mocked deps
_bridge_ns = {}
with open(BRIDGE_PATH) as _bf:
    exec(compile(_bf.read(), BRIDGE_PATH, 'exec'), _bridge_ns)
BridgeClass = _bridge_ns.get('GLM4MoELiteBridge')
assert BridgeClass is not None, 'GLM4MoELiteBridge class not found in source'

# Instantiate with a GLM-4.7-Flash config (47 hidden layers, rope_theta in dict)
class _TestConfig:
    num_hidden_layers = 47
    num_nextn_predict_layers = 1
    rope_parameters = {'rope_theta': 500000}
    # No direct rope_theta — bridge must extract it from rope_parameters

bridge = BridgeClass(_TestConfig())
MOCKEOF

echo ""
echo "=== F2P Behavioral: rope_theta extracted from rope_parameters ==="
# [pr_diff] (0.15): Bridge __init__ must patch rope_theta from rope_parameters dict.
# The buggy stub inherits parent __init__ which reads hf_config.rope_theta directly
# and would fail on GLM-4.7-Flash (which stores it in rope_parameters dict).
# Test: instantiate with config lacking rope_theta, verify it gets patched to 500000.
python3 -c "
BRIDGE_PATH = '$BRIDGE'
exec(open('/tmp/bridge_mock_setup.py').read())
cfg = bridge.hf_config
assert hasattr(cfg, 'rope_theta'), 'rope_theta was not patched onto config'
assert cfg.rope_theta == 500000, f'Expected rope_theta=500000, got {cfg.rope_theta}'
print('PASS')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

echo ""
echo "=== F2P Behavioral: _SHARED_STATE_DICT_MAPPING uses dynamic layer ==="
# [pr_diff] (0.20): Shared state dict mapping must reference layer 47 (from config),
# not hardcoded 61 (DeepSeek V3's layer count).
# Test: after instantiation with num_hidden_layers=47, verify mapping values.
python3 -c "
BRIDGE_PATH = '$BRIDGE'
exec(open('/tmp/bridge_mock_setup.py').read())
mapping = bridge._SHARED_STATE_DICT_MAPPING

# Must have the standard embedding/output keys
assert 'embedding.word_embeddings.weight' in mapping, f'Missing embedding key: {list(mapping.keys())}'
assert 'output_layer.weight' in mapping, f'Missing output key: {list(mapping.keys())}'

# Values must reference layer 47, never 61
for key, values in mapping.items():
    for v in values:
        assert '.61.' not in v, f'Hardcoded layer 61 still in mapping: {v}'
    layer_refs = [v for v in values if '.47.' in v]
    assert len(layer_refs) >= 1, f'No layer-47 reference for {key}: {values}'

print('PASS')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

echo ""
echo "=== F2P Behavioral: _convert_mtp_param uses dynamic layer count ==="
# [pr_diff] (0.20): MTP parameter name conversion must produce layer-47 names,
# not layer-61. The buggy stub inherits parent's hardcoded mapping.
# Test: call _convert_mtp_param with MTP names, verify output uses 47.
python3 -c "
BRIDGE_PATH = '$BRIDGE'
exec(open('/tmp/bridge_mock_setup.py').read())

# Direct name mappings (enorm, hnorm, eh_proj, final_layernorm)
test_inputs = [
    'mtp.layers.0.enorm.weight',
    'mtp.layers.0.hnorm.weight',
    'mtp.layers.0.eh_proj.weight',
    'mtp.layers.0.final_layernorm.weight',
]
for name in test_inputs:
    result = bridge._convert_mtp_param(name)
    assert isinstance(result, list), f'Expected list for {name}, got {type(result)}'
    assert len(result) >= 1, f'Empty result for {name}'
    joined = ' '.join(result)
    assert '.47.' in joined, f'Expected layer 47 for {name}, got: {result}'
    assert '.61.' not in joined, f'Hardcoded 61 for {name}: {result}'

# Transformer-layer proxy mapping (self_attention, mlp paths)
proxy_result = bridge._convert_mtp_param(
    'mtp.layers.0.transformer_layer.self_attention.proj.weight'
)
assert isinstance(proxy_result, list), f'Expected list, got {type(proxy_result)}'
proxy_joined = ' '.join(proxy_result)
assert '.61.' not in proxy_joined, f'Hardcoded 61 in proxy: {proxy_result}'

print('PASS')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

echo ""
echo "=== F2P Behavioral: _get_safetensor_io uses standard loader ==="
# [pr_diff] (0.10): Bridge must override _get_safetensor_io to use standard
# SafeTensorIO (bf16) instead of parent's FP8 dequant loader.
# Test: call _get_safetensor_io and verify it returns SafeTensorIO, not FP8.
python3 -c "
BRIDGE_PATH = '$BRIDGE'
exec(open('/tmp/bridge_mock_setup.py').read())

result = bridge._get_safetensor_io('/fake/weights/path')
# Parent returns string 'FP8_DEQUANT_LOADER'; child should return SafeTensorIO instance
assert result != 'FP8_DEQUANT_LOADER', 'Still using parent FP8 dequant loader'
assert hasattr(result, 'path'), f'Expected SafeTensorIO-like object with .path, got {type(result)}'
print('PASS')
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Structural: model_provider bridge path handles critic role ==="
# [pr_diff] (0.10): Bridge path must wrap provider.provide for critic role.
# WHY AST: model_provider.py requires megatron.core imports; can't instantiate.
# Check: in get_model_provider_func, there's an if-block comparing to 'critic'
# that contains both a nested function def AND a return (the wrapper pattern).
python3 -c "
import ast

source = open('$PROVIDER').read()
tree = ast.parse(source)

# Walk all if-blocks, find one that tests for 'critic' and contains
# a wrapper pattern (nested function def + return)
for node in ast.walk(tree):
    if isinstance(node, ast.If):
        has_critic = False
        has_func_def = False
        has_return = False
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and child.value == 'critic':
                has_critic = True
            if isinstance(child, ast.FunctionDef):
                has_func_def = True
            if isinstance(child, ast.Return):
                has_return = True
        if has_critic and has_func_def and has_return:
            print('PASS: critic wrapper pattern found in model_provider')
            exit(0)

print('FAIL: No critic wrapper pattern in model_provider')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Regression: GLM4MoELiteBridge inherits DeepseekV3Bridge ==="
# [pr_diff] (0.10): Class must inherit from DeepseekV3Bridge and be registered
python3 -c "
import ast

source = open('$BRIDGE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GLM4MoELite' in node.name:
        bases = []
        for b in node.bases:
            if isinstance(b, ast.Name):
                bases.append(b.id)
            elif isinstance(b, ast.Attribute):
                bases.append(b.attr)
        assert 'DeepseekV3Bridge' in bases, f'Expected DeepseekV3Bridge base, got {bases}'

        deco_names = []
        for d in node.decorator_list:
            if isinstance(d, ast.Call) and isinstance(d.func, ast.Name):
                deco_names.append(d.func.id)
        assert 'register_model' in deco_names, f'Missing @register_model: {deco_names}'
        print('PASS')
        exit(0)

print('FAIL: GLM4MoELiteBridge class not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

echo ""
echo "=== Anti-stub: Class body is non-trivial ==="
# [pr_diff] (0.15): GLM4MoELiteBridge must have >=4 meaningful members (not just pass)
python3 -c "
import ast

source = open('$BRIDGE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GLM4MoELite' in node.name:
        meaningful = 0
        for item in node.body:
            if isinstance(item, ast.Pass):
                continue
            if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant) and isinstance(item.value.value, str):
                continue  # docstring
            meaningful += 1
        assert meaningful >= 4, f'Class too small ({meaningful} members) — likely a stub'
        print(f'PASS: {meaningful} meaningful members')
        exit(0)

print('FAIL: class not found')
exit(1)
" 2>&1
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

echo ""
echo "=== FINAL SCORE ==="
echo "Score: $SCORE / 1.0"
mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
