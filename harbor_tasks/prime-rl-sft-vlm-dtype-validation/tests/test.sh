#!/usr/bin/env bash
set +e

SCORE=0
REPO="/workspace/prime-rl"
TRAINER_PY="$REPO/src/prime_rl/configs/trainer.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): trainer.py must be valid Python
if python3 -c "import ast; ast.parse(open('$TRAINER_PY').read())" 2>/dev/null; then
    echo "PASS: trainer.py parses"
else
    echo "FAIL: trainer.py has syntax errors — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo ""
echo "=== Fail-to-Pass: Core bug — ModelConfig no longer blocks VLMs ==="

# [pr_diff] (0.30): ModelConfig with VLM name and default float32 dtypes does NOT raise
R1=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import ModelConfig
try:
    m = ModelConfig(name='Qwen/Qwen3-VL-4B-Instruct')
    print('PASS')
except ValueError as e:
    if 'bfloat16' in str(e):
        print('FAIL: ModelConfig still rejects VLM with default dtypes')
    else:
        print('FAIL: unexpected error: ' + str(e))
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R1" | grep -q "^PASS"; then
    echo "PASS (0.30): ModelConfig accepts VLM with default float32 dtypes"
    SCORE=$(python3 -c "print($SCORE + 0.30)")
else
    echo "FAIL (0.30): $R1"
fi

# [pr_diff] (0.15): SFTConfig with VLM model and default dtypes does NOT raise
# This is the actual user-facing bug — SFT training was blocked
R2=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import ModelConfig
from prime_rl.configs.sft import SFTConfig
try:
    sc = SFTConfig(model=ModelConfig(name='Qwen/Qwen3-VL-4B-Instruct'))
    print('PASS')
except ValueError as e:
    if 'bfloat16' in str(e):
        print('FAIL: SFTConfig still rejects VLM with default dtypes')
    else:
        print('FAIL: unexpected error: ' + str(e))
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R2" | grep -q "^PASS"; then
    echo "PASS (0.15): SFTConfig accepts VLM with default float32 dtypes"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "FAIL (0.15): $R2"
fi

echo ""
echo "=== Behavioral: RL trainer still enforces bfloat16 for VLMs ==="

# [pr_diff] (0.20): TrainerConfig with VLM name and default float32 dtypes DOES raise
# Construct ModelConfig first (which must now succeed), then wrap in TrainerConfig
R3=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import TrainerConfig, ModelConfig
mc = ModelConfig(name='Qwen/Qwen3-VL-4B-Instruct')
# If ModelConfig still raises, bug isn't fixed — bail out
if mc is None:
    print('FAIL: could not create ModelConfig')
    sys.exit(0)
try:
    tc = TrainerConfig(model=mc)
    print('FAIL: TrainerConfig should reject VLM with default float32 dtypes')
except ValueError as e:
    if 'bfloat16' in str(e):
        print('PASS')
    else:
        print('FAIL: wrong error: ' + str(e))
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R3" | grep -q "^PASS"; then
    echo "PASS (0.20): TrainerConfig rejects VLM with default float32 dtypes"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "FAIL (0.20): $R3"
fi

# [pr_diff] (0.10): TrainerConfig with VLM name and bfloat16 dtypes succeeds
R4=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import TrainerConfig, ModelConfig
try:
    tc = TrainerConfig(model=ModelConfig(
        name='Qwen/Qwen3-VL-4B-Instruct',
        optimization_dtype='bfloat16',
        reduce_dtype='bfloat16'
    ))
    print('PASS')
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R4" | grep -q "^PASS"; then
    echo "PASS (0.10): TrainerConfig accepts VLM with bfloat16 dtypes"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): $R4"
fi

# [pr_diff] (0.05): TrainerConfig rejects VLM with partial dtype mismatch
# (one bfloat16, one float32) — errors must not pass silently
R5=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import TrainerConfig, ModelConfig
raised = False
try:
    tc = TrainerConfig(model=ModelConfig(
        name='Qwen/Qwen3-VL-4B-Instruct',
        optimization_dtype='float32',
        reduce_dtype='bfloat16'
    ))
except ValueError:
    raised = True
except Exception:
    pass
if raised:
    print('PASS')
else:
    print('FAIL: partial dtype mismatch should raise ValueError in TrainerConfig')
" 2>&1)
if echo "$R5" | grep -q "^PASS"; then
    echo "PASS (0.05): TrainerConfig rejects VLM with partial dtype mismatch"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "FAIL (0.05): $R5"
fi

echo ""
echo "=== Pass-to-pass: Non-VLM models unaffected ==="

# [pr_diff] (0.10): Non-VLM ModelConfig with default dtypes still works
R6=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import ModelConfig
try:
    m = ModelConfig(name='Qwen/Qwen3-0.6B')
    assert m.optimization_dtype == 'float32', f'Expected float32, got {m.optimization_dtype}'
    assert m.reduce_dtype == 'float32', f'Expected float32, got {m.reduce_dtype}'
    print('PASS')
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R6" | grep -q "^PASS"; then
    echo "PASS (0.10): non-VLM ModelConfig with defaults works"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): $R6"
fi

# [pr_diff] (0.10): Non-VLM TrainerConfig still works
R7=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from prime_rl.configs.trainer import TrainerConfig, ModelConfig
try:
    tc = TrainerConfig(model=ModelConfig(name='Qwen/Qwen3-0.6B'))
    print('PASS')
except Exception as e:
    print('FAIL: ' + str(e))
" 2>&1)
if echo "$R7" | grep -q "^PASS"; then
    echo "PASS (0.10): non-VLM TrainerConfig works"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "FAIL (0.10): $R7"
fi

echo ""
echo "=== Summary ==="
SCORE=$(python3 -c "print(round($SCORE, 2))")
echo "Total score: $SCORE / 1.0"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
behavioral = min(0.80, score)
regression = min(0.20, max(score - 0.80, 0))
json.dump({
    'reward': score,
    'behavioral': behavioral,
    'regression': regression,
    'config': 0.0,
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
