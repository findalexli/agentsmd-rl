#!/usr/bin/env bash
set -uo pipefail

REPO="/workspace/transformers"
SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "  PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "  FAIL ($1): $2"; }

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): All changed files must parse
for f in \
    src/transformers/configuration_utils.py \
    src/transformers/models/mt5/configuration_mt5.py \
    src/transformers/models/umt5/configuration_umt5.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        echo "  GATE FAILED: $f has syntax errors"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "  Gate passed."

echo ""
echo "=== Behavioral: PreTrainedConfig no tokenizer_class default ==="
# [pr_diff] (0.25): PreTrainedConfig should not have tokenizer_class as a declared field
RESULT=$(cd "$REPO" && python3 -c "
from transformers.configuration_utils import PreTrainedConfig
config = PreTrainedConfig()
d = config.to_dict()
# tokenizer_class should NOT be in the default serialized config
if 'tokenizer_class' in d:
    print('FOUND')
else:
    print('OK')
" 2>&1)
if [ "$RESULT" = "OK" ]; then
    pass 0.25 "PreTrainedConfig().to_dict() does not contain tokenizer_class"
else
    fail 0.25 "PreTrainedConfig().to_dict() still contains tokenizer_class"
fi

echo ""
echo "=== Behavioral: MT5Config no tokenizer_class default ==="
# [pr_diff] (0.20): MT5Config should not serialize a hardcoded tokenizer_class
RESULT=$(cd "$REPO" && python3 -c "
from transformers.models.mt5.configuration_mt5 import MT5Config
config = MT5Config()
d = config.to_dict()
if 'tokenizer_class' in d:
    print('FOUND')
else:
    print('OK')
" 2>&1)
if [ "$RESULT" = "OK" ]; then
    pass 0.20 "MT5Config().to_dict() does not contain tokenizer_class"
else
    fail 0.20 "MT5Config().to_dict() still contains tokenizer_class"
fi

echo ""
echo "=== Behavioral: UMT5Config no tokenizer_class default ==="
# [pr_diff] (0.15): UMT5Config should not serialize a hardcoded tokenizer_class
RESULT=$(cd "$REPO" && python3 -c "
from transformers.models.umt5.configuration_umt5 import UMT5Config
config = UMT5Config()
d = config.to_dict()
if 'tokenizer_class' in d:
    print('FOUND')
else:
    print('OK')
" 2>&1)
if [ "$RESULT" = "OK" ]; then
    pass 0.15 "UMT5Config().to_dict() does not contain tokenizer_class"
else
    fail 0.15 "UMT5Config().to_dict() still contains tokenizer_class"
fi

echo ""
echo "=== Pass-to-pass: Config basics still work ==="
# [pr_diff] (0.15): Basic config creation, serialization, and round-trip
RESULT=$(cd "$REPO" && python3 -c "
import json
from transformers.configuration_utils import PreTrainedConfig
from transformers.models.mt5.configuration_mt5 import MT5Config

# Basic creation
c = PreTrainedConfig()
d = c.to_dict()
assert 'model_type' in d, 'model_type missing from dict'

# MT5 round-trip
m = MT5Config(d_model=512, num_heads=8)
md = m.to_dict()
assert md['d_model'] == 512, 'd_model mismatch'
assert md['num_heads'] == 8, 'num_heads mismatch'
assert md['model_type'] == 'mt5', 'model_type mismatch'

# from_dict round-trip
m2 = MT5Config(**{k: v for k, v in md.items() if k != 'transformers_version'})
assert m2.d_model == 512, 'round-trip d_model mismatch'

print('OK')
" 2>&1)
if echo "$RESULT" | grep -q "OK"; then
    pass 0.15 "Config creation and serialization round-trip works"
else
    fail 0.15 "Config basics broken: $RESULT"
fi

echo ""
echo "=== Structural: No PreTrainedTokenizerBase import in configuration_utils ==="
# [pr_diff] (0.10): Unnecessary import of PreTrainedTokenizerBase should be removed
# WHY AST/grep: this checks an import dependency, not callable behavior
if grep -q "from.*tokenization_utils_base.*import.*PreTrainedTokenizerBase" "$REPO/src/transformers/configuration_utils.py" 2>/dev/null; then
    fail 0.10 "configuration_utils.py still imports PreTrainedTokenizerBase"
else
    pass 0.10 "PreTrainedTokenizerBase import removed from configuration_utils.py"
fi

echo ""
echo "=== Config-derived: ruff check on changed files ==="
# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2
RUFF_OK=true
for f in \
    src/transformers/configuration_utils.py \
    src/transformers/models/mt5/configuration_mt5.py \
    src/transformers/models/umt5/configuration_umt5.py; do
    if ! (cd "$REPO" && python3 -m ruff check "$f" --select=E,F,I --quiet 2>/dev/null); then
        RUFF_OK=false
    fi
done
if [ "$RUFF_OK" = true ]; then
    pass 0.10 "ruff check passes on all changed files"
else
    fail 0.10 "ruff check found issues"
fi

echo ""
echo "=== Anti-stub: test file updated ==="
# [pr_diff] (0.05): test_configuration_utils.py should not exclude tokenizer_class
if grep -q '"tokenizer_class"' "$REPO/tests/utils/test_configuration_utils.py" 2>/dev/null; then
    fail 0.05 "test_configuration_utils.py still references tokenizer_class in exclusion list"
else
    pass 0.05 "tokenizer_class removed from test exclusion list"
fi

echo ""
echo "=== Results ==="
echo "  Score: $SCORE / 1.00"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
data = {
    'reward': score,
    'behavioral': min(0.60, score),
    'regression': 0.15 if score >= 0.75 else 0.0,
    'config': 0.10 if score >= 0.90 else 0.0,
    'style_rubric': 0.05 if score >= 0.95 else 0.0
}
print(json.dumps(data))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
