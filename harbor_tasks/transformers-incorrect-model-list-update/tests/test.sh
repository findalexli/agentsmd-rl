#!/usr/bin/env bash
set +e
set -uo pipefail

SCORE=0
REPO="/workspace/transformers"

log() { echo "[$1] $2 (weight=$3)"; }

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (GATE): Modified files must parse without syntax errors
GATE_PASS=1
for f in \
    src/transformers/models/auto/tokenization_auto.py \
    src/transformers/models/llama4/configuration_llama4.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        log GATE "Syntax error in $f" 0
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "GATE FAILED: syntax errors found"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log GATE "All modified files parse OK" 0

########################################################################
# BEHAVIORAL: Fail-to-pass tests (weight = 0.65)
########################################################################

# --- Test 1: Key missing models present in the imported set ---
# [pr_diff] (0.25): Missing model types must be present in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
T1=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS

key_models = {'h2ovl_chat', 'internvl_chat', 'molmo', 'phi3_v', 'openvla', 'kimi_k25'}
missing = key_models - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if missing:
    print(f'FAIL: missing {missing}')
else:
    print('PASS')
" 2>&1)

if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    log PASS "Key missing models present in set" 0.25
else
    log FAIL "Missing key models: $T1" 0.25
fi

# --- Test 2: Remaining missing models present ---
# [pr_diff] (0.20): All missing model types must be present
T2=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS

remaining = {'chatlm', 'minimax_m2', 'molmo2', 'nemotron', 'nvfp4', 'phimoe', 'minicpmv'}
missing = remaining - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if missing:
    print(f'FAIL: missing {missing}')
else:
    print('PASS')
" 2>&1)

if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    log PASS "Remaining missing models present in set" 0.20
else
    log FAIL "Missing remaining models: $T2" 0.20
fi

# --- Test 3: Llama4TextConfig layer_types accepts string values ---
# [pr_diff] (0.20): layer_types must work with string values (was incorrectly int-annotated)
T3=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.llama4.configuration_llama4 import Llama4TextConfig

# Instantiate with string layer_types — the whole point of the fix
config = Llama4TextConfig(layer_types=['dense', 'moe', 'dense'])
# Verify the stored value is actually strings
if config.layer_types is None:
    print('FAIL: layer_types is None after setting')
    sys.exit(0)
if not all(isinstance(t, str) for t in config.layer_types):
    print('FAIL: layer_types contains non-string values')
    sys.exit(0)
if config.layer_types != ['dense', 'moe', 'dense']:
    print(f'FAIL: unexpected value {config.layer_types}')
    sys.exit(0)

# Check the type annotation says str, not int
import typing
hints = typing.get_type_hints(Llama4TextConfig)
layer_hint = hints.get('layer_types')
if layer_hint is not None:
    hint_str = str(layer_hint)
    if 'int' in hint_str and 'str' not in hint_str:
        print('FAIL: type hint still declares int instead of str')
        sys.exit(0)
print('PASS')
" 2>&1)

if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    log PASS "Llama4TextConfig layer_types accepts strings correctly" 0.20
else
    log FAIL "Llama4 layer_types: $T3" 0.20
fi

########################################################################
# PASS-TO-PASS: Regression checks (weight = 0.15)
########################################################################

# --- Test 4: Pre-existing models still in the set ---
# [pr_diff] (0.10): Existing entries must not be removed
T4=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS

existing = {'arctic', 'chameleon', 'deepseek_v2', 'deepseek_v3', 'deepseek_vl',
            'deepseek_vl_v2', 'deepseek_vl_hybrid', 'fuyu', 'hyperclovax_vlm',
            'internlm2', 'jamba', 'janus', 'llava', 'llava_next', 'modernbert',
            'opencua', 'phi3', 'step3p5', 'vipllava'}
missing = existing - MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if missing:
    print(f'FAIL: removed {missing}')
else:
    print('PASS')
" 2>&1)

if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    log PASS "Pre-existing models still in set" 0.10
else
    log FAIL "Regression — removed models: $T4" 0.10
fi

# --- Test 5: Llama4TextConfig other key attributes unchanged ---
# [pr_diff] (0.05): Other Llama4TextConfig attributes must remain intact
T5=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.llama4.configuration_llama4 import Llama4TextConfig

config = Llama4TextConfig()
# Check key attributes still exist with sensible defaults
assert hasattr(config, 'attention_chunk_size'), 'missing attention_chunk_size'
assert hasattr(config, 'attn_temperature_tuning'), 'missing attn_temperature_tuning'
assert hasattr(config, 'floor_scale'), 'missing floor_scale'
assert hasattr(config, 'attn_scale'), 'missing attn_scale'
assert isinstance(config.attention_chunk_size, int), 'attention_chunk_size wrong type'
print('PASS')
" 2>&1)

if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "Llama4TextConfig other attrs intact" 0.05
else
    log FAIL "Llama4 regression: $T5" 0.05
fi

########################################################################
# CONFIG-DERIVED: Agent config checks (weight = 0.10)
########################################################################

# --- Test 6: Set entries are sorted alphabetically ---
# [agent_config] (0.05): "make check-repo" consistency — CLAUDE.md:5 @ a48a63c2
T6=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS

entries = sorted(MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS)
# The set itself is unordered; check if the source file has them sorted
import ast
with open('$REPO/src/transformers/models/auto/tokenization_auto.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.AnnAssign) and hasattr(node.target, 'id'):
        if node.target.id == 'MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS':
            if hasattr(node.value, 'elts'):
                source_order = [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
                if source_order == sorted(source_order):
                    print('PASS')
                else:
                    print('FAIL: entries not sorted alphabetically in source')
            else:
                # Non-literal set, can't check ordering — pass if content is correct
                print('PASS')
            sys.exit(0)

print('FAIL: variable not found')
" 2>&1)

if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "Set entries sorted alphabetically" 0.05
else
    log FAIL "Sorting: $T6" 0.05
fi

# --- Test 7: ruff lint check on changed files ---
# [agent_config] (0.05): "make style" runs ruff — CLAUDE.md:2 @ a48a63c2
T7=$(cd "$REPO" && python3 -m ruff check \
    src/transformers/models/auto/tokenization_auto.py \
    src/transformers/models/llama4/configuration_llama4.py \
    --select E,W --quiet 2>&1)

if [ $? -eq 0 ] || [ -z "$T7" ]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    log PASS "ruff lint clean on changed files" 0.05
else
    log FAIL "ruff issues: $T7" 0.05
fi

########################################################################
# ANTI-STUB: Set must have sufficient entries (weight = 0.10)
########################################################################

# [pr_diff] (0.10): Set must contain all expected models (not gutted)
T8=$(python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS

count = len(MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS)
if count >= 25:
    print('PASS')
else:
    print(f'FAIL: only {count} entries, expected >= 25')
" 2>&1)

if echo "$T8" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    log PASS "Set has sufficient entries (anti-stub)" 0.10
else
    log FAIL "Anti-stub: $T8" 0.10
fi

########################################################################
# SUMMARY
########################################################################

echo ""
echo "=== Score: $SCORE / 1.00 ==="

FINAL=$(python3 -c "print(round(float('$SCORE'), 4))")

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
echo "{\"reward\": $FINAL, \"behavioral\": $(python3 -c "print(min($FINAL, 0.65))"), \"regression\": $(python3 -c "print(min(max($FINAL - 0.65, 0), 0.15))"), \"config\": $(python3 -c "print(min(max($FINAL - 0.80, 0), 0.10))"), \"anti_stub\": $(python3 -c "print(min(max($FINAL - 0.90, 0), 0.10))")}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
