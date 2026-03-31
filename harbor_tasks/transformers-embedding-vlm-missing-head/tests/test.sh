#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "FAIL ($1): $2"; }

# ── GATE (0.00): Syntax check on changed files ──
# [pr_diff] (0.00): All modified Python files must parse
echo "=== GATE: Syntax check ==="
GATE_PASS=true
for f in \
    src/transformers/models/colpali/modeling_colpali.py \
    src/transformers/models/colqwen2/modeling_colqwen2.py \
    src/transformers/models/colqwen2/modular_colqwen2.py \
    src/transformers/models/colmodernvbert/modeling_colmodernvbert.py \
    src/transformers/conversion_mapping.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE passed"

# ── Behavioral: base_model_prefix set to "vlm" ──
# These FAIL on buggy code (defaults to "") and PASS after the fix

# [pr_diff] (0.20): ColPaliForRetrieval.base_model_prefix == "vlm"
echo "=== Check: ColPali base_model_prefix ==="
if python3 -c "
from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval
assert ColPaliForRetrieval.base_model_prefix == 'vlm', f'Got: {ColPaliForRetrieval.base_model_prefix!r}'
" 2>/dev/null; then
    pass 0.20 "ColPaliForRetrieval.base_model_prefix == 'vlm'"
else
    fail 0.20 "ColPaliForRetrieval.base_model_prefix != 'vlm'"
fi

# [pr_diff] (0.15): ColQwen2ForRetrieval.base_model_prefix == "vlm"
echo "=== Check: ColQwen2 base_model_prefix ==="
if python3 -c "
from transformers.models.colqwen2.modeling_colqwen2 import ColQwen2ForRetrieval
assert ColQwen2ForRetrieval.base_model_prefix == 'vlm', f'Got: {ColQwen2ForRetrieval.base_model_prefix!r}'
" 2>/dev/null; then
    pass 0.15 "ColQwen2ForRetrieval.base_model_prefix == 'vlm'"
else
    fail 0.15 "ColQwen2ForRetrieval.base_model_prefix != 'vlm'"
fi

# [pr_diff] (0.15): ColModernVBertForRetrieval.base_model_prefix == "vlm"
echo "=== Check: ColModernVBert base_model_prefix ==="
if python3 -c "
from transformers.models.colmodernvbert.modeling_colmodernvbert import ColModernVBertForRetrieval
assert ColModernVBertForRetrieval.base_model_prefix == 'vlm', f'Got: {ColModernVBertForRetrieval.base_model_prefix!r}'
" 2>/dev/null; then
    pass 0.15 "ColModernVBertForRetrieval.base_model_prefix == 'vlm'"
else
    fail 0.15 "ColModernVBertForRetrieval.base_model_prefix != 'vlm'"
fi

# ── Behavioral: conversion_mapping has colqwen2 entry ──
# [pr_diff] (0.15): colqwen2 weight renaming exists in conversion mapping
echo "=== Check: colqwen2 in conversion_mapping ==="
if python3 -c "
from transformers.conversion_mapping import _build_checkpoint_conversion_mapping
mapping = _build_checkpoint_conversion_mapping()
assert 'colqwen2' in mapping, f'colqwen2 not in mapping; keys: {list(mapping.keys())}'
" 2>/dev/null; then
    pass 0.15 "colqwen2 entry exists in conversion_mapping"
else
    fail 0.15 "colqwen2 entry missing from conversion_mapping"
fi

# ── Behavioral: ColPali uses base model (AutoModel), not causal-LM model ──
# On buggy code, vlm is created with AutoModelForImageTextToText (has lm_head).
# After fix, vlm is created with AutoModel (no lm_head).
# [pr_diff] (0.15): ColPali vlm is a base model without lm_head
echo "=== Check: ColPali vlm is base model ==="
if python3 -c "
from transformers.models.colpali.configuration_colpali import ColPaliConfig
from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval
config = ColPaliConfig()
model = ColPaliForRetrieval(config)
# A base model (AutoModel) should NOT have an lm_head attribute
assert not hasattr(model.vlm, 'lm_head'), 'vlm still has lm_head — should use base model, not causal LM'
" 2>/dev/null; then
    pass 0.15 "ColPali vlm is base model (no lm_head)"
else
    fail 0.15 "ColPali vlm has lm_head — still using causal LM model"
fi

# ── Regression: modules import without error ──
# [pr_diff] (0.10): All affected modules import cleanly
echo "=== Check: modules import cleanly ==="
if python3 -c "
from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval
from transformers.models.colqwen2.modeling_colqwen2 import ColQwen2ForRetrieval
from transformers.models.colmodernvbert.modeling_colmodernvbert import ColModernVBertForRetrieval
from transformers.conversion_mapping import _build_checkpoint_conversion_mapping
print('All imports OK')
" 2>/dev/null; then
    pass 0.10 "All affected modules import cleanly"
else
    fail 0.10 "Module import failed"
fi

# ── Structural: anti-stub check — forward method still exists ──
# [pr_diff] (0.05): forward() method not stubbed out
echo "=== Check: forward methods exist ==="
if python3 -c "
import inspect
from transformers.models.colpali.modeling_colpali import ColPaliForRetrieval
from transformers.models.colqwen2.modeling_colqwen2 import ColQwen2ForRetrieval
from transformers.models.colmodernvbert.modeling_colmodernvbert import ColModernVBertForRetrieval
for cls in [ColPaliForRetrieval, ColQwen2ForRetrieval, ColModernVBertForRetrieval]:
    fwd = getattr(cls, 'forward', None)
    assert fwd is not None, f'{cls.__name__} missing forward()'
    src = inspect.getsource(fwd)
    assert len(src) > 100, f'{cls.__name__}.forward() looks stubbed (too short)'
" 2>/dev/null; then
    pass 0.05 "forward() methods exist and are not stubbed"
else
    fail 0.05 "forward() method missing or stubbed"
fi

# ── Config-derived: ruff format check on changed files ──
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2
echo "=== Check: ruff format ==="
if command -v ruff &>/dev/null || pip install --quiet ruff 2>/dev/null; then
    RUFF_OK=true
    for f in \
        src/transformers/models/colpali/modeling_colpali.py \
        src/transformers/models/colqwen2/modeling_colqwen2.py \
        src/transformers/models/colqwen2/modular_colqwen2.py \
        src/transformers/models/colmodernvbert/modeling_colmodernvbert.py \
        src/transformers/conversion_mapping.py; do
        if ! ruff format --check "$f" 2>/dev/null; then
            RUFF_OK=false
        fi
    done
    if [ "$RUFF_OK" = true ]; then
        pass 0.05 "ruff format passes on changed files"
    else
        fail 0.05 "ruff format fails on changed files"
    fi
else
    pass 0.05 "ruff not available, skipping (neutral)"
fi

# ── Compute final score ──
echo ""
echo "Final score: $SCORE / 1.00"
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json breakdown
python3 -c "
import json
score = float('$SCORE')
# behavioral = base_model_prefix (0.20+0.15+0.15) + conversion_mapping (0.15) + base model (0.15) = 0.80
# regression = imports (0.10) = 0.10
# structural = forward exists (0.05) = 0.05
# config = ruff (0.05) = 0.05
behavioral = 0.0
regression = 0.0
structural = 0.0
config = 0.0
json.dump({'reward': score, 'behavioral': behavioral, 'regression': regression, 'config': config, 'style_rubric': 0.0}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
