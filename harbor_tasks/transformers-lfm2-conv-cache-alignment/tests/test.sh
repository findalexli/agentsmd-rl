#!/usr/bin/env bash
set -euo pipefail

TOTAL=0.0
SCORE=0.0
RESULTS=()

add_result() {
    local name="$1" weight="$2" passed="$3"
    RESULTS+=("$name:$weight:$passed")
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$passed" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
    fi
}

# ─── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): All three files must parse without syntax errors
GATE_PASS=1
for f in \
    src/transformers/models/lfm2/modeling_lfm2.py \
    src/transformers/models/lfm2/modular_lfm2.py \
    src/transformers/models/lfm2_moe/modeling_lfm2_moe.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "0" ]; then
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ─── Fail-to-pass: Cache update_conv_state with cache_init=True ──────
# [pr_diff] (0.15): update_conv_state(cache_init=True) stores state correctly
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=2, dtype=torch.float32)

# Simulate prefill: create a state and init the conv cache for layer 0
new_state = torch.randn(2, 8, 3)
result = cache.update_conv_state(0, new_state, cache_init=True)

# Verify the cache was updated
assert torch.allclose(result, new_state), 'cache_init=True should store exact state'
assert torch.allclose(cache.conv_cache[0], new_state), 'conv_cache should hold stored state'
print('PASS: update_conv_state cache_init=True')
" 2>/dev/null && PASS=1
add_result "update_conv_state_init" 0.15 "$PASS"

# ─── Fail-to-pass: Cache update_conv_state with cache_init=False ─────
# [pr_diff] (0.10): update_conv_state(cache_init=False) does roll+update
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

# Init the cache first
init_state = torch.tensor([[[1.0, 2.0, 3.0]]] * 8).unsqueeze(0)  # (1, 8, 3)
cache.update_conv_state(0, init_state, cache_init=True)

# Now decode update: should roll left and update last position
decode_input = torch.tensor([[[0.0, 0.0, 9.0]]] * 8).unsqueeze(0)  # (1, 8, 3)
result = cache.update_conv_state(0, decode_input, cache_init=False)

# After roll(-1) on [1,2,3] -> [2,3,1], then last pos set to 9 -> [2,3,9]
expected_last = 9.0
assert result[0, 0, -1].item() == expected_last, f'Expected last pos=9.0, got {result[0,0,-1].item()}'
assert result[0, 0, 0].item() == 2.0, f'Expected first pos=2.0 after roll, got {result[0,0,0].item()}'
print('PASS: update_conv_state cache_init=False roll+update')
" 2>/dev/null && PASS=1
add_result "update_conv_state_decode" 0.10 "$PASS"

# ─── Fail-to-pass: has_previous_state flag lifecycle ─────────────────
# [pr_diff] (0.10): has_previous_state starts False, becomes True after last conv layer, resets
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

# Initially False
assert cache.has_previous_state == False, 'Should start False'

# Update a non-last conv layer -> still False
state = torch.randn(1, 8, 3)
cache.update_conv_state(0, state, cache_init=True)
assert cache.has_previous_state == False, 'Should stay False after non-last conv layer'

# Update the last conv layer (index 3) -> becomes True
cache.update_conv_state(3, state, cache_init=True)
assert cache.has_previous_state == True, 'Should be True after last conv layer update'

# Reset -> back to False
cache.reset()
assert cache.has_previous_state == False, 'Should be False after reset'
print('PASS: has_previous_state lifecycle')
" 2>/dev/null && PASS=1
add_result "has_previous_state_lifecycle" 0.10 "$PASS"

# ─── Fail-to-pass: slow_forward prefill then decode produces valid output ──
# [pr_diff] (0.10): slow_forward works for both prefill and decode paths
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache, Lfm2ConvModule
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=16, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=32, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

# Create a conv module for layer 0 (a conv layer)
conv_mod = Lfm2ConvModule(config, layer_idx=0)
conv_mod.eval()

# Prefill: sequence of length 5
x_prefill = torch.randn(1, 5, 16)
out_prefill = conv_mod.slow_forward(x_prefill, cache, attention_mask=None)
assert out_prefill.shape == (1, 5, 16), f'Prefill shape wrong: {out_prefill.shape}'

# Simulate that all conv layers did prefill (set has_previous_state)
for li in [0, 1, 3]:
    cache.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)

# Decode: single token
x_decode = torch.randn(1, 1, 16)
out_decode = conv_mod.slow_forward(x_decode, cache, attention_mask=None)
assert out_decode.shape == (1, 1, 16), f'Decode shape wrong: {out_decode.shape}'
assert not torch.isnan(out_decode).any(), 'Decode output contains NaN'
print('PASS: slow_forward prefill+decode')
" 2>/dev/null && PASS=1
add_result "slow_forward_prefill_decode" 0.10 "$PASS"

# ─── Fail-to-pass: slow_forward decode output depends on cached conv state ──
# [pr_diff] (0.20): Decode path must actually read from conv cache (not just do fresh conv)
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache, Lfm2ConvModule
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

torch.manual_seed(42)

config = Lfm2Config(
    hidden_size=16, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=32, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)

conv_mod = Lfm2ConvModule(config, layer_idx=0)
conv_mod.eval()

# Use the same decode input for both runs
x_decode = torch.randn(1, 1, 16)

# --- Run 1: Prefill, set cache to known state A, then decode ---
cache1 = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)
x_prefill = torch.randn(1, 5, 16)
conv_mod.slow_forward(x_prefill, cache1, attention_mask=None)
# Initialize all conv layers to trigger has_previous_state
for li in [0, 1, 3]:
    cache1.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)
# Overwrite layer 0 cache with known state A
cache1.conv_cache[0] = torch.ones(1, 16, 3) * 2.0
out1 = conv_mod.slow_forward(x_decode, cache1, attention_mask=None)

# --- Run 2: Prefill, set cache to very different state B, then decode ---
cache2 = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)
conv_mod.slow_forward(x_prefill, cache2, attention_mask=None)
for li in [0, 1, 3]:
    cache2.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)
# Overwrite layer 0 cache with very different state B
cache2.conv_cache[0] = torch.ones(1, 16, 3) * -50.0
out2 = conv_mod.slow_forward(x_decode, cache2, attention_mask=None)

# If slow_forward decode path reads from cache, outputs MUST differ
# If it still uses old past_seen_tokens logic (==0 -> prefill branch), outputs will be identical
assert not torch.allclose(out1, out2, atol=1e-3), \
    'Decode output must depend on cached conv state — slow_forward is not using cache in decode mode'
print('PASS: slow_forward decode depends on conv cache')
" 2>/dev/null && PASS=1
add_result "slow_forward_decode_cache_dep" 0.20 "$PASS"

# ─── Fail-to-pass: MoE variant has same cache behavior ──────────────
# [pr_diff] (0.10): lfm2_moe cache also has update_conv_state and has_previous_state
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2_moe.modeling_lfm2_moe import Lfm2MoeHybridConvCache
from transformers.models.lfm2_moe.configuration_lfm2_moe import Lfm2MoeConfig

config = Lfm2MoeConfig(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv'],
    num_local_experts=2, num_experts_per_tok=1
)
cache = Lfm2MoeHybridConvCache(config, max_batch_size=1, dtype=torch.float32)

assert cache.has_previous_state == False
state = torch.randn(1, 8, 3)
result = cache.update_conv_state(3, state, cache_init=True)
assert cache.has_previous_state == True
assert torch.allclose(result, state)
cache.reset()
assert cache.has_previous_state == False
print('PASS: MoE cache has same behavior')
" 2>/dev/null && PASS=1
add_result "moe_cache_alignment" 0.10 "$PASS"

# ─── Pass-to-pass: Cache basic init and get_seq_length still work ────
# [pr_diff] (0.10): Existing cache API is preserved
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=2, dtype=torch.float32)

# Basic API checks
assert len(cache) == 4, f'Expected 4 layers, got {len(cache)}'
assert cache.get_seq_length() == 0, f'Expected 0 seq length initially'
assert len(cache.conv_cache) == 4, f'Expected 4 conv caches'
assert cache.conv_cache[0].shape == (2, 8, 3), f'Wrong conv cache shape: {cache.conv_cache[0].shape}'

# update KV cache
k = torch.randn(2, 2, 5, 4)
v = torch.randn(2, 2, 5, 4)
cache.update(k, v, layer_idx=2)
assert cache.get_seq_length(2) == 5, f'Expected seq_length 5 after update'
print('PASS: basic cache API preserved')
" 2>/dev/null && PASS=1
add_result "cache_api_preserved" 0.10 "$PASS"

# ─── Config-derived: ruff format check on changed files ──────────────
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ f5e573080ae
PASS=0
if command -v ruff &>/dev/null; then
    if ruff check --select E,W src/transformers/models/lfm2/modeling_lfm2.py \
                               src/transformers/models/lfm2/modular_lfm2.py \
                               src/transformers/models/lfm2_moe/modeling_lfm2_moe.py 2>/dev/null; then
        PASS=1
    fi
else
    # ruff not installed, skip gracefully (don't penalize)
    PASS=1
fi
add_result "ruff_lint" 0.05 "$PASS"

# ─── Anti-stub: update_conv_state actually modifies cache ────────────
# [pr_diff] (0.05): Ensure update_conv_state is not a no-op stub
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=4, num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=8, conv_L_cache=3,
    layer_types=['conv', 'full_attention']
)
cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

before = cache.conv_cache[0].clone()
state = torch.randn(1, 4, 3)
cache.update_conv_state(0, state, cache_init=True)
after = cache.conv_cache[0]

assert not torch.equal(before, after), 'update_conv_state should actually modify the cache'
print('PASS: anti-stub verified')
" 2>/dev/null && PASS=1
add_result "anti_stub" 0.05 "$PASS"

# ─── Modular file consistency ────────────────────────────────────────
# [pr_diff] (0.05): modular_lfm2.py also has update_conv_state and has_previous_state
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.lfm2.modular_lfm2 import Lfm2HybridConvCache
from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

config = Lfm2Config(
    hidden_size=8, num_hidden_layers=4, num_attention_heads=2, num_key_value_heads=2,
    intermediate_size=16, conv_L_cache=3,
    layer_types=['conv', 'conv', 'full_attention', 'conv']
)
cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

assert cache.has_previous_state == False
state = torch.randn(1, 8, 3)
cache.update_conv_state(3, state, cache_init=True)
assert cache.has_previous_state == True
print('PASS: modular file consistent')
" 2>/dev/null && PASS=1
add_result "modular_consistency" 0.05 "$PASS"

# ─── Compute final reward ────────────────────────────────────────────
echo ""
echo "=== Results ==="
BEHAVIORAL=0.0
REGRESSION=0.0
CONFIG=0.0

for r in "${RESULTS[@]}"; do
    IFS=: read -r name weight passed <<< "$r"
    status="FAIL"
    [ "$passed" = "1" ] && status="PASS"
    echo "  [$status] $name (weight=$weight)"

    if [ "$passed" = "1" ]; then
        case "$name" in
            cache_api_preserved) REGRESSION=$(python3 -c "print($REGRESSION + $weight)") ;;
            ruff_lint) CONFIG=$(python3 -c "print($CONFIG + $weight)") ;;
            *) BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + $weight)") ;;
        esac
    fi
done

echo ""
echo "Behavioral: $BEHAVIORAL"
echo "Regression: $REGRESSION"
echo "Config: $CONFIG"
echo "Total: $SCORE / $TOTAL"

# Write reward files
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
print(json.dumps({
    'reward': $SCORE,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG,
    'style_rubric': 0.0
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
