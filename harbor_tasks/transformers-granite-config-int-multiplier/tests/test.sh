#!/usr/bin/env bash
set +e

PASS=0
TOTAL=0

add()   { TOTAL=$(python3 -c "print($TOTAL + $1)"); }
award() { PASS=$(python3 -c "print($PASS + $1)"); }

# ── GATE: Syntax check on all three config files ──
# [pr_diff] (gate): Changed files must parse
for f in \
    src/transformers/models/granite/configuration_granite.py \
    src/transformers/models/granitemoe/configuration_granitemoe.py \
    src/transformers/models/granitemoeshared/configuration_granitemoeshared.py; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null || {
        echo "GATE FAIL: $f has syntax errors"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
        exit 0
    }
done
echo "GATE PASS: all config files parse"

# ── Behavioral F2P: GraniteConfig accepts int multiplier values (0.20) ──
# [pr_diff] (0.20): GraniteConfig must accept integer multiplier fields without error
add 0.20
if python3 -c "
from transformers import GraniteConfig
c = GraniteConfig(embedding_multiplier=12, logits_scaling=8, residual_multiplier=4, attention_multiplier=2)
assert c.embedding_multiplier == 12
assert c.logits_scaling == 8
assert c.residual_multiplier == 4
assert c.attention_multiplier == 2
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteConfig accepts int multipliers"
    award 0.20
else
    echo "FAIL: GraniteConfig rejects int multipliers"
fi

# ── Behavioral F2P: GraniteConfig int roundtrip through save/load (0.10) ──
# [pr_diff] (0.10): Config with int values survives save_pretrained / from_pretrained roundtrip
add 0.10
if python3 -c "
import tempfile
from transformers import GraniteConfig
c = GraniteConfig(embedding_multiplier=12, logits_scaling=8, residual_multiplier=4, attention_multiplier=2)
with tempfile.TemporaryDirectory() as d:
    c.save_pretrained(d)
    loaded = GraniteConfig.from_pretrained(d)
assert loaded.embedding_multiplier == 12
assert loaded.logits_scaling == 8
assert loaded.residual_multiplier == 4
assert loaded.attention_multiplier == 2
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteConfig int roundtrip"
    award 0.10
else
    echo "FAIL: GraniteConfig int roundtrip"
fi

# ── Behavioral F2P: GraniteMoeConfig accepts int multiplier values (0.15) ──
# [pr_diff] (0.15): GraniteMoeConfig must accept integer multiplier fields
add 0.15
if python3 -c "
from transformers import GraniteMoeConfig
c = GraniteMoeConfig(embedding_multiplier=12, logits_scaling=8, residual_multiplier=4, attention_multiplier=2)
assert c.embedding_multiplier == 12
assert c.logits_scaling == 8
assert c.residual_multiplier == 4
assert c.attention_multiplier == 2
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteMoeConfig accepts int multipliers"
    award 0.15
else
    echo "FAIL: GraniteMoeConfig rejects int multipliers"
fi

# ── Behavioral F2P: GraniteMoeConfig int roundtrip (0.05) ──
# [pr_diff] (0.05): GraniteMoeConfig int values survive save/load roundtrip
add 0.05
if python3 -c "
import tempfile
from transformers import GraniteMoeConfig
c = GraniteMoeConfig(embedding_multiplier=10, logits_scaling=6)
with tempfile.TemporaryDirectory() as d:
    c.save_pretrained(d)
    loaded = GraniteMoeConfig.from_pretrained(d)
assert loaded.embedding_multiplier == 10
assert loaded.logits_scaling == 6
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteMoeConfig int roundtrip"
    award 0.05
else
    echo "FAIL: GraniteMoeConfig int roundtrip"
fi

# ── Behavioral F2P: GraniteMoeSharedConfig accepts int multiplier values (0.15) ──
# [pr_diff] (0.15): GraniteMoeSharedConfig must accept integer multiplier fields
add 0.15
if python3 -c "
from transformers import GraniteMoeSharedConfig
c = GraniteMoeSharedConfig(embedding_multiplier=12, logits_scaling=8, residual_multiplier=4, attention_multiplier=2)
assert c.embedding_multiplier == 12
assert c.logits_scaling == 8
assert c.residual_multiplier == 4
assert c.attention_multiplier == 2
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteMoeSharedConfig accepts int multipliers"
    award 0.15
else
    echo "FAIL: GraniteMoeSharedConfig rejects int multipliers"
fi

# ── Behavioral F2P: GraniteMoeSharedConfig int roundtrip (0.05) ──
# [pr_diff] (0.05): GraniteMoeSharedConfig int values survive save/load roundtrip
add 0.05
if python3 -c "
import tempfile
from transformers import GraniteMoeSharedConfig
c = GraniteMoeSharedConfig(embedding_multiplier=7, logits_scaling=3)
with tempfile.TemporaryDirectory() as d:
    c.save_pretrained(d)
    loaded = GraniteMoeSharedConfig.from_pretrained(d)
assert loaded.embedding_multiplier == 7
assert loaded.logits_scaling == 3
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteMoeSharedConfig int roundtrip"
    award 0.05
else
    echo "FAIL: GraniteMoeSharedConfig int roundtrip"
fi

# ── Pass-to-pass: GraniteConfig still works with float defaults (0.05) ──
# [pr_diff] (0.05): Existing float-based configs must still load correctly
add 0.05
if python3 -c "
from transformers import GraniteConfig
c = GraniteConfig()
assert c.embedding_multiplier == 1.0
assert c.logits_scaling == 1.0
assert c.residual_multiplier == 1.0
assert c.attention_multiplier == 1.0
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteConfig float defaults still work"
    award 0.05
else
    echo "FAIL: GraniteConfig float defaults broken"
fi

# ── Pass-to-pass: GraniteConfig with explicit float roundtrip (0.05) ──
# [pr_diff] (0.05): Explicit float values still accepted and survive roundtrip
add 0.05
if python3 -c "
import tempfile
from transformers import GraniteConfig
c = GraniteConfig(embedding_multiplier=1.5, logits_scaling=2.0)
with tempfile.TemporaryDirectory() as d:
    c.save_pretrained(d)
    loaded = GraniteConfig.from_pretrained(d)
assert loaded.embedding_multiplier == 1.5
assert loaded.logits_scaling == 2.0
print('OK')
" 2>/dev/null; then
    echo "PASS: GraniteConfig explicit float roundtrip"
    award 0.05
else
    echo "FAIL: GraniteConfig explicit float roundtrip"
fi

# ── Config-derived: ruff check on changed files (0.10) ──
# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2
add 0.10
if ruff check \
    src/transformers/models/granite/configuration_granite.py \
    src/transformers/models/granitemoe/configuration_granitemoe.py \
    src/transformers/models/granitemoeshared/configuration_granitemoeshared.py \
    --quiet 2>/dev/null; then
    echo "PASS: ruff check clean"
    award 0.10
else
    echo "FAIL: ruff check found issues"
fi

# ── Compute final reward ──
REWARD=$(python3 -c "print(round($PASS / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo "$REWARD" > /logs/verifier/reward.txt

# Compute category scores for reward.json
python3 -c "
pass_val = $PASS
total = $TOTAL
reward = round(pass_val / total, 4) if total > 0 else 0.0
# F2P behavioral: first 0.85 of points
behavioral = round(min(pass_val, 0.85), 4)
# P2P regression: next 0.10
regression = round(max(0, min(pass_val, 0.95) - 0.85), 4)
# Config: last 0.10
config = round(max(0, min(pass_val, 1.05) - 0.95), 4)
import json
print(json.dumps({'reward': reward, 'behavioral': behavioral, 'regression': regression, 'config': config, 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

echo "Total: $PASS / $TOTAL = $REWARD"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
