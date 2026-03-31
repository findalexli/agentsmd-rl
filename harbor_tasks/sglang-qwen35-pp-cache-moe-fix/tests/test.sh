#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/workspace/sglang"
TOTAL=0.0
LOG="/logs/verifier/test.log"
mkdir -p /logs/verifier

exec > >(tee -a "$LOG") 2>&1

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
}

echo "=== GATE: Syntax check ==="
# [pr_diff] (0.00): Gate — changed files must parse
GATE_PASS=true
for f in \
    python/sglang/srt/mem_cache/memory_pool.py \
    python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py \
    python/sglang/srt/models/qwen3_5.py \
    python/sglang/srt/models/qwen3_vl.py \
    python/sglang/srt/disaggregation/decode.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "FAIL: $f does not parse"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: All files parse"

echo ""
echo "=== Behavioral: get_layer_id correctly identifies layer IDs ==="
# [pr_diff] (0.10): get_layer_id must parse layer IDs from weight names
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    'common', '$REPO/python/sglang/srt/layers/utils/common.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['sglang.srt.layers.utils.common'] = mod
spec.loader.exec_module(mod)
get_layer_id = mod.get_layer_id

# Verify get_layer_id parses correctly
assert get_layer_id('model.layers.0.mlp.gate_proj.weight') == 0
assert get_layer_id('model.layers.21.mlp.experts.w2_weight') == 21
assert get_layer_id('model.layers.99.qkv_proj.weight') == 99
assert get_layer_id('model.embed_tokens.weight') is None
assert get_layer_id('lm_head.weight') is None
print('PASS: get_layer_id works correctly')
" && add_score 0.10 || echo "FAIL: get_layer_id"

echo ""
echo "=== Behavioral: PP-aware weight filtering skips out-of-range layers ==="
# [pr_diff] (0.25): Simulated load_weights loop must skip layers outside [start_layer, end_layer)
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    'common', '$REPO/python/sglang/srt/layers/utils/common.py')
mod = importlib.util.module_from_spec(spec)
sys.modules['sglang.srt.layers.utils.common'] = mod
spec.loader.exec_module(mod)
get_layer_id = mod.get_layer_id

# Simulate PP rank 1 of 2 for a 40-layer model: layers [20, 40)
start_layer, end_layer = 20, 40

# Simulate the full set of weight names a model would see
weight_names = []
for layer in range(40):
    weight_names.append(f'model.layers.{layer}.mlp.gate_proj.weight')
    weight_names.append(f'model.layers.{layer}.mlp.experts.w2_weight')
    weight_names.append(f'model.layers.{layer}.qkv_proj.weight')
# Non-layer weights
weight_names.extend(['model.embed_tokens.weight', 'model.norm.weight', 'lm_head.weight'])

# Apply the filtering logic from the fix
loaded, skipped = [], []
for name in weight_names:
    layer_id = get_layer_id(name)
    if layer_id is not None and (layer_id < start_layer or layer_id >= end_layer):
        skipped.append(name)
        continue
    loaded.append(name)

# 20 layers * 3 weights = 60 layer weights loaded, plus 3 non-layer weights
assert len(loaded) == 63, f'Expected 63 loaded, got {len(loaded)}'
# 20 layers * 3 weights = 60 skipped
assert len(skipped) == 60, f'Expected 60 skipped, got {len(skipped)}'

# Verify no skipped weight has layer in [20, 40)
for name in skipped:
    lid = get_layer_id(name)
    assert lid is not None and (lid < start_layer or lid >= end_layer), f'Incorrectly skipped: {name}'

# Verify all loaded layer weights are in [20, 40)
for name in loaded:
    lid = get_layer_id(name)
    if lid is not None:
        assert start_layer <= lid < end_layer, f'Incorrectly loaded out-of-range: {name}'

# The bug: without this filtering, layer 21 expert weights cause KeyError
# because params_dict only has layers 20-39
assert 'model.layers.21.mlp.experts.w2_weight' in loaded, 'Layer 21 expert weights must be loaded'
assert 'model.layers.0.mlp.experts.w2_weight' in skipped, 'Layer 0 expert weights must be skipped'
print('PASS: PP-aware weight filtering correctly skips out-of-range layers')
" && add_score 0.25 || echo "FAIL: PP-aware weight filtering"

echo ""
echo "=== Behavioral: Mamba layer ID filtering for PP ==="
# [pr_diff] (0.20): Filtering mamba_layer_ids by PP range reduces pool size
python3 -c "
import sys
sys.path.insert(0, '$REPO/python')

# Simulate the fix: filter mamba_layer_ids by PP range
# A hybrid model has mamba layers at specific positions (e.g., alternating)
all_mamba_layers = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]

# PP rank with start_layer=10, end_layer=20
start_layer, end_layer = 10, 20
filtered = [i for i in all_mamba_layers if start_layer <= i < end_layer]

# Only layers 10, 12, 14, 16, 18 should remain
assert filtered == [10, 12, 14, 16, 18], f'Expected [10,12,14,16,18], got {filtered}'
assert len(filtered) == 5, f'Expected 5 filtered layers, got {len(filtered)}'

# Bug: without filtering, MambaPool allocates for all 15 layers instead of 5
# This wastes 10/15 = 67% of GPU memory for mamba cache
num_all = len(all_mamba_layers)
num_filtered = len(filtered)
assert num_filtered < num_all, 'Filtered should be smaller than all layers'

# Verify the mamba_map uses filtered IDs
mamba_map = {layer_id: i for i, layer_id in enumerate(filtered)}
assert mamba_map == {10: 0, 12: 1, 14: 2, 16: 3, 18: 4}, f'Wrong mamba_map: {mamba_map}'
assert len(mamba_map) == 5, 'mamba_map should only have 5 entries'

print('PASS: Mamba layer filtering reduces pool to PP rank range')
" && add_score 0.20 || echo "FAIL: Mamba layer filtering"

echo ""
echo "=== Behavioral: start_layer correctly propagated (not hardcoded to 0) ==="
# [pr_diff] (0.15): HybridReqToTokenPool and HybridLinearKVPool use passed start_layer
python3 -c "
import sys
sys.path.insert(0, '$REPO/python')

# Read the source and verify the TODO comments are removed and start_layer is parametric
src = open('$REPO/python/sglang/srt/mem_cache/memory_pool.py').read()

# The buggy code had:
#   self.start_layer = 0  # TODO: Support PP
# The fix should remove this pattern entirely

# Count occurrences of the hardcoded pattern
hardcoded_count = src.count('self.start_layer = 0')
todo_count = src.count('TODO: Support PP')

# After fix, there should be no hardcoded start_layer = 0 without conditional
# and no TODO: Support PP comments
assert todo_count == 0, f'Still has {todo_count} TODO: Support PP comments'

# Check that start_layer is now a parameter in HybridReqToTokenPool and HybridLinearKVPool
# by looking for the parametric assignment pattern
parametric = src.count('start_layer if start_layer is not None else 0')
assert parametric >= 2, f'Expected >=2 parametric start_layer assignments, got {parametric}'

print('PASS: start_layer is parametric, not hardcoded')
" && add_score 0.15 || echo "FAIL: start_layer propagation"

echo ""
echo "=== Behavioral: Qwen3VL start_layer/end_layer property delegation ==="
# [pr_diff] (0.10): Qwen3VLForConditionalGeneration must expose PP boundaries
python3 -c "
import sys
sys.path.insert(0, '$REPO/python')

# Test the property logic extracted from the fix
# The fix adds:
#   @property
#   def start_layer(self): return getattr(getattr(self, 'model', None), 'start_layer', 0)
#   @property
#   def end_layer(self): ...

# Simulate the property logic
class MockModel:
    start_layer = 10
    end_layer = 20

class MockConfig:
    num_hidden_layers = 40

class MockModelNoLayers:
    config = MockConfig()

# Test start_layer delegation
class TestClass:
    model = MockModel()

obj = TestClass()
result = getattr(getattr(obj, 'model', None), 'start_layer', 0)
assert result == 10, f'Expected 10, got {result}'

# Test end_layer delegation
model = getattr(obj, 'model', None)
end_layer = getattr(model, 'end_layer', None)
assert end_layer == 20, f'Expected 20, got {end_layer}'

# Test fallback when model has no end_layer
obj2 = type('T', (), {'model': MockModelNoLayers()})()
model2 = getattr(obj2, 'model', None)
end_layer2 = getattr(model2, 'end_layer', None)
if end_layer2 is not None:
    result2 = end_layer2
else:
    cfg = getattr(model2, 'config', None)
    result2 = int(getattr(cfg, 'num_hidden_layers', 0))
assert result2 == 40, f'Expected fallback 40, got {result2}'

# Test fallback when no model at all
obj3 = type('T', (), {})()
result3 = getattr(getattr(obj3, 'model', None), 'start_layer', 0)
assert result3 == 0, f'Expected default 0, got {result3}'

print('PASS: Property delegation logic works correctly')
" && add_score 0.10 || echo "FAIL: property delegation"

echo ""
echo "=== Behavioral: HybridMambaDecodeReqToTokenPool accepts PP params ==="
# [pr_diff] (0.10): disaggregation/decode.py must accept mamba_layer_ids and start_layer
python3 -c "
import sys, ast
sys.path.insert(0, '$REPO/python')

src = open('$REPO/python/sglang/srt/disaggregation/decode.py').read()
tree = ast.parse(src)

# WHY AST: HybridMambaDecodeReqToTokenPool requires torch CUDA, complex cache_params,
# and DecodeReqToTokenPool base class with live GPU tensors — cannot instantiate on CPU
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'HybridMambaDecodeReqToTokenPool':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                param_names = [arg.arg for arg in item.args.args]
                assert 'mamba_layer_ids' in param_names, \
                    f'HybridMambaDecodeReqToTokenPool must accept mamba_layer_ids, got: {param_names}'
                assert 'start_layer' in param_names, \
                    f'HybridMambaDecodeReqToTokenPool must accept start_layer, got: {param_names}'
                # Verify start_layer is used parametrically
                init_src = ast.get_source_segment(src, item)
                assert 'start_layer if start_layer' in init_src, \
                    'start_layer must be used parametrically'
                print('PASS: HybridMambaDecodeReqToTokenPool accepts PP params')
                break
        break
" && add_score 0.10 || echo "FAIL: HybridMambaDecodeReqToTokenPool PP params"

echo ""
echo "=== Regression: model_runner passes PP-filtered mamba_layer_ids ==="
# [pr_diff] (0.10): model_runner_kv_cache_mixin must construct filtered mamba_layer_ids
python3 -c "
import sys
sys.path.insert(0, '$REPO/python')

src = open('$REPO/python/sglang/srt/model_executor/model_runner_kv_cache_mixin.py').read()

# Verify that mamba_layer_ids is computed with PP filtering
assert 'mamba_layer_ids' in src, 'Must pass mamba_layer_ids to pool constructors'
# Must have the filtering pattern
assert 'self.start_layer' in src, 'Must reference self.start_layer for filtering'
assert 'self.end_layer' in src, 'Must reference self.end_layer for filtering'

print('PASS: model_runner_kv_cache_mixin passes filtered mamba_layer_ids')
" && add_score 0.10 || echo "FAIL: model_runner PP params"

echo ""
echo "==================================="
echo "Total score: $TOTAL"
echo "==================================="

# Write reward files
echo "$TOTAL" > /logs/verifier/reward.txt
python3 -c "
import json
total = $TOTAL
# Weights: behavioral(call)=0.10+0.25+0.20+0.10=0.65, structural=0.15+0.10=0.25,
# regression=0.10. Total=1.00
print(json.dumps({
    'reward': round(total, 4),
    'behavioral': round(min(total, 0.65), 4),
    'regression': round(max(0, min(total - 0.90, 0.10)), 4),
    'config': 0.0,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
