#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
REPO=/workspace/transformers

echo "=== Transformers Mistral Query Scaling Positions ==="

########################################
# GATE: Syntax check on all affected files
########################################
echo "--- GATE: Syntax check ---"
GATE_PASS=true
for f in \
    src/transformers/models/ministral3/modeling_ministral3.py \
    src/transformers/models/ministral3/modular_ministral3.py \
    src/transformers/models/mistral4/modeling_mistral4.py \
    src/transformers/models/mistral4/modular_mistral4.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "reward: 0.0"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    cp /logs/verifier/reward.txt "/logs/verifier/reward.txt" 2>/dev/null || true
    cp /logs/verifier/reward.json "/logs/verifier/reward.json" 2>/dev/null || true
    exit 0
fi
echo "GATE PASS: All files parse cleanly"

########################################
# BEHAVIORAL TEST 1 (0.30): get_llama_4_attn_scale produces 4D output from 2D input
# [pr_diff] (0.30): Scaling function must accept batched 2D position_ids and return 4D tensor
########################################
echo "--- Behavioral 1: 4D output shape from 2D position_ids (ministral3) ---"
T1=$(cd "$REPO" && python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale

# 2D position_ids: (batch=2, seq=4)
pos = torch.tensor([[0, 1, 2, 3], [0, 1, 2, 3]])
result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=8192)

# Should be 4D: (batch, 1, seq, 1) for broadcasting with (batch, heads, seq, head_dim)
assert result.ndim == 4, f'Expected 4D, got {result.ndim}D with shape {result.shape}'
assert result.shape[0] == 2, f'Expected batch=2, got {result.shape[0]}'
assert result.shape[1] == 1, f'Expected dim1=1, got {result.shape[1]}'
assert result.shape[2] == 4, f'Expected seq=4, got {result.shape[2]}'
assert result.shape[3] == 1, f'Expected dim3=1, got {result.shape[3]}'
print('PASS')
" 2>&1) || T1="FAIL"
if [[ "$T1" == *"PASS"* ]]; then
    echo "PASS: 4D output shape correct (ministral3)"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "FAIL: $T1"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.30)")

########################################
# BEHAVIORAL TEST 2 (0.25): Per-batch scaling differs with different positions (mistral4)
# [pr_diff] (0.25): Different position_ids per batch item yield different scaling factors
########################################
echo "--- Behavioral 2: Per-batch scaling with padded positions (mistral4) ---"
T2=$(cd "$REPO" && python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale

# Batch 0: normal positions. Batch 1: padded (starts at position 100, well beyond max_pos=64)
pos = torch.tensor([[0, 1, 2, 3], [100, 101, 102, 103]])
result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=64)

# Must be 4D
assert result.ndim == 4, f'Expected 4D, got {result.ndim}D'

# The two batch items should have DIFFERENT scaling factors since positions differ
batch0 = result[0, 0, :, 0]  # (seq,)
batch1 = result[1, 0, :, 0]  # (seq,)
assert not torch.allclose(batch0, batch1), f'Batches should differ: {batch0} vs {batch1}'

# Batch 1 positions > max_pos_emb should have scaling > 1.0
assert (batch1 > 1.0).all(), f'Positions > max_pos should scale > 1.0, got {batch1}'
print('PASS')
" 2>&1) || T2="FAIL"
if [[ "$T2" == *"PASS"* ]]; then
    echo "PASS: Per-batch scaling differs correctly (mistral4)"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "FAIL: $T2"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")

########################################
# BEHAVIORAL TEST 3 (0.15): Scaling formula correctness for large positions
# [pr_diff] (0.15): Verify numerical output of scaling function matches expected values
########################################
echo "--- Behavioral 3: Scaling formula numerical correctness ---"
T3=$(cd "$REPO" && python3 -c "
import torch, sys, math
sys.path.insert(0, 'src')
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale

beta = 0.1
max_pos = 64

# Positions that span multiple max_pos windows
pos = torch.tensor([[0, 64, 128, 256]])
result = get_llama_4_attn_scale(pos, beta=beta, max_position_embeddings=max_pos)

# Expected: 1 + beta * log(1 + floor(pos / max_pos))
# pos=0:   1 + 0.1*log(1+0) = 1.0
# pos=64:  1 + 0.1*log(1+1) = 1 + 0.1*ln(2) ≈ 1.0693
# pos=128: 1 + 0.1*log(1+2) = 1 + 0.1*ln(3) ≈ 1.1099
# pos=256: 1 + 0.1*log(1+4) = 1 + 0.1*ln(5) ≈ 1.1609
expected = [
    1.0,
    1.0 + 0.1 * math.log(2),
    1.0 + 0.1 * math.log(3),
    1.0 + 0.1 * math.log(5),
]

for i, exp in enumerate(expected):
    got = result[0, 0, i, 0].item()
    assert abs(got - exp) < 1e-4, f'Position {pos[0,i].item()}: expected {exp:.4f}, got {got:.4f}'

print('PASS')
" 2>&1) || T3="FAIL"
if [[ "$T3" == *"PASS"* ]]; then
    echo "PASS: Scaling formula numerically correct"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: $T3"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

########################################
# PASS-TO-PASS (0.15): Scaling values for small positions unchanged
# [pr_diff] (0.15): Positions < max_pos_embeddings still produce scaling = 1.0
########################################
echo "--- Pass-to-pass: Scaling = 1.0 for small positions ---"
T4=$(cd "$REPO" && python3 -c "
import torch, sys
sys.path.insert(0, 'src')
from transformers.models.ministral3.modeling_ministral3 import get_llama_4_attn_scale

# All positions < max_pos_embeddings: floor(pos/8192) = 0, so scaling = 1.0
pos = torch.tensor([[0, 1, 100, 8191]])
result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=8192)

# Must be 4D
assert result.ndim == 4, f'Expected 4D, got {result.ndim}D'

for i in range(4):
    val = result[0, 0, i, 0].item()
    assert abs(val - 1.0) < 1e-5, f'Position {pos[0,i].item()} scaling should be 1.0, got {val}'

print('PASS')
" 2>&1) || T4="FAIL"
if [[ "$T4" == *"PASS"* ]]; then
    echo "PASS: Small position scaling correct"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL: $T4"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")

########################################
# BEHAVIORAL TEST 5 (0.10): mistral4 function also produces correct 4D output
# [pr_diff] (0.10): Both model variants must be fixed, not just one
########################################
echo "--- Behavioral 5: mistral4 also returns 4D with correct values ---"
T5=$(cd "$REPO" && python3 -c "
import torch, sys, math
sys.path.insert(0, 'src')
from transformers.models.mistral4.modeling_mistral4 import get_llama_4_attn_scale

# Test shape AND values for mistral4 variant
pos = torch.tensor([[0, 1, 2, 3], [64, 65, 66, 67]])
result = get_llama_4_attn_scale(pos, beta=0.1, max_position_embeddings=64)

# Shape check
assert result.ndim == 4, f'Expected 4D, got {result.ndim}D'
assert result.shape == (2, 1, 4, 1), f'Expected (2,1,4,1), got {result.shape}'

# Batch 0 positions < max_pos: scaling = 1.0
for i in range(4):
    val = result[0, 0, i, 0].item()
    assert abs(val - 1.0) < 1e-5, f'Batch 0 pos {i}: expected 1.0, got {val}'

# Batch 1 positions >= max_pos: scaling > 1.0
expected_b1 = 1.0 + 0.1 * math.log(2)  # floor(64/64)=1, log(1+1)=ln(2)
for i in range(4):
    val = result[1, 0, i, 0].item()
    assert abs(val - expected_b1) < 1e-4, f'Batch 1 pos {64+i}: expected {expected_b1:.4f}, got {val}'

print('PASS')
" 2>&1) || T5="FAIL"
if [[ "$T5" == *"PASS"* ]]; then
    echo "PASS: mistral4 variant also correct"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL: $T5"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")

########################################
# ANTI-STUB (0.05): Functions are not trivial stubs
# [static] (0.05): get_llama_4_attn_scale has real computation (>=3 meaningful statements)
########################################
echo "--- Anti-stub check ---"
T6=$(cd "$REPO" && python3 -c "
import ast, sys

files = [
    'src/transformers/models/ministral3/modeling_ministral3.py',
    'src/transformers/models/mistral4/modeling_mistral4.py',
]
for f in files:
    tree = ast.parse(open(f).read())
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'get_llama_4_attn_scale':
            found = True
            # Filter out docstrings and bare constants
            real_stmts = [s for s in node.body
                          if not (isinstance(s, ast.Expr) and isinstance(getattr(s, 'value', None), (ast.Constant, ast.Str)))]
            assert len(real_stmts) >= 2, f'{f}: get_llama_4_attn_scale appears stubbed ({len(real_stmts)} real statements)'
            break
    assert found, f'{f}: get_llama_4_attn_scale not found'
print('PASS')
" 2>&1) || T6="FAIL"
if [[ "$T6" == *"PASS"* ]]; then
    echo "PASS: Functions not stubbed"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL: $T6"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")

########################################
# FINAL SCORING
########################################
echo ""
echo "=== Final Score: $SCORE / $TOTAL ==="

# Compute component scores for reward.json
BEHAVIORAL=$(python3 -c "
b1 = 0.30 if 'PASS' in '''$T1''' else 0.0
b2 = 0.25 if 'PASS' in '''$T2''' else 0.0
b3 = 0.15 if 'PASS' in '''$T3''' else 0.0
b5 = 0.10 if 'PASS' in '''$T5''' else 0.0
print(f'{b1+b2+b3+b5:.2f}')
")
REGRESSION=$(python3 -c "print('0.15' if 'PASS' in '''$T4''' else '0.00')")

echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
json.dump({
    'reward': float('$SCORE'),
    'behavioral': float('$BEHAVIORAL'),
    'regression': float('$REGRESSION'),
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

cp /logs/verifier/reward.txt "/logs/verifier/reward.txt" 2>/dev/null || true
cp /logs/verifier/reward.json "/logs/verifier/reward.json" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
