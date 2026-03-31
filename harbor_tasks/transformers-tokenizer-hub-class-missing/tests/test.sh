#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight=$1 name=$2 pass=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $name\n"
    fi
}

cd /workspace/transformers

# ── GATE: Syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): Source file must parse without syntax errors
if python3 -c "import ast; ast.parse(open('src/transformers/models/auto/tokenization_auto.py').read())" 2>/dev/null; then
    echo "GATE: syntax OK"
else
    echo "GATE FAILED: tokenization_auto.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    python3 -c "
import json
json.dump({'reward': 0.0, 'behavioral': 0.0, 'regression': 0.0, 'config': 0.0, 'style_rubric': 0.0}, open('/logs/verifier/reward.json','w'))
"
    exit 0
fi

# ── BEHAVIORAL: Fail-to-pass tests (0.70 total) ─────────────────────

# [pr_diff] (0.20): deepseek_v2 must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if python3 -c "
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
assert 'deepseek_v2' in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS, 'deepseek_v2 missing'
" 2>/dev/null; then
    add_result 0.20 "deepseek_v2 in incorrect-class set" 1
else
    add_result 0.20 "deepseek_v2 in incorrect-class set" 0
fi

# [pr_diff] (0.20): deepseek_v3 must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if python3 -c "
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
assert 'deepseek_v3' in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS, 'deepseek_v3 missing'
" 2>/dev/null; then
    add_result 0.20 "deepseek_v3 in incorrect-class set" 1
else
    add_result 0.20 "deepseek_v3 in incorrect-class set" 0
fi

# [pr_diff] (0.20): modernbert must be in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
if python3 -c "
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
assert 'modernbert' in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS, 'modernbert missing'
" 2>/dev/null; then
    add_result 0.20 "modernbert in incorrect-class set" 1
else
    add_result 0.20 "modernbert in incorrect-class set" 0
fi

# [pr_diff] (0.10): All three model types must resolve to TokenizersBackend in TOKENIZER_MAPPING_NAMES
if python3 -c "
from transformers.models.auto.tokenization_auto import TOKENIZER_MAPPING_NAMES
for mt in ['deepseek_v2', 'deepseek_v3', 'modernbert']:
    val = TOKENIZER_MAPPING_NAMES.get(mt)
    assert val is not None, f'{mt} not in TOKENIZER_MAPPING_NAMES'
    assert 'TokenizersBackend' in str(val) or 'Backend' in str(val), f'{mt} mapped to {val}, expected TokenizersBackend'
" 2>/dev/null; then
    add_result 0.10 "model types resolve in TOKENIZER_MAPPING_NAMES" 1
else
    add_result 0.10 "model types resolve in TOKENIZER_MAPPING_NAMES" 0
fi

# ── PASS-TO-PASS: Regression tests (0.15 total) ─────────────────────

# [repo_tests] (0.10): Existing entries in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS still present
if python3 -c "
from transformers.models.auto.tokenization_auto import MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS
existing = ['arctic', 'chameleon', 'deepseek_vl', 'deepseek_vl_v2', 'fuyu', 'jamba', 'llava', 'phi3']
for m in existing:
    assert m in MODELS_WITH_INCORRECT_HUB_TOKENIZER_CLASS, f'Regression: {m} removed from set'
" 2>/dev/null; then
    add_result 0.10 "existing incorrect-class entries preserved" 1
else
    add_result 0.10 "existing incorrect-class entries preserved" 0
fi

# [repo_tests] (0.05): TOKENIZER_MAPPING_NAMES still contains core model types
if python3 -c "
from transformers.models.auto.tokenization_auto import TOKENIZER_MAPPING_NAMES
for mt in ['bert', 'gpt2', 'roberta', 't5']:
    assert mt in TOKENIZER_MAPPING_NAMES, f'Regression: {mt} missing from mapping'
" 2>/dev/null; then
    add_result 0.05 "core TOKENIZER_MAPPING_NAMES entries intact" 1
else
    add_result 0.05 "core TOKENIZER_MAPPING_NAMES entries intact" 0
fi

# ── CONFIG-DERIVED: Agent config checks (0.15 total) ────────────────

# [agent_config] (0.05): "make style" — code passes ruff format check — CLAUDE.md:2 @ c55f6505
if python3 -c "
import subprocess, sys
r = subprocess.run(['python3', '-m', 'ruff', 'format', '--check', '--quiet',
    'src/transformers/models/auto/tokenization_auto.py'],
    capture_output=True, cwd='/workspace/transformers')
sys.exit(r.returncode)
" 2>/dev/null; then
    add_result 0.05 "ruff format check passes" 1
else
    add_result 0.05 "ruff format check passes" 0
fi

# [agent_config] (0.05): "When writing tests, they should be added to an existing file" — .github/copilot-instructions.md:16 @ c55f6505
# Verify the agent didn't create new test files for this change (tests belong in existing files)
if python3 -c "
import subprocess
r = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD'],
    capture_output=True, text=True, cwd='/workspace/transformers')
new_files = [f for f in r.stdout.strip().split('\n') if f.startswith('tests/') and f.endswith('.py') and f]
# New test files are a violation (for bugfix PRs, add to existing test files)
import sys
sys.exit(1 if new_files else 0)
" 2>/dev/null; then
    add_result 0.05 "no new test files created (use existing)" 1
else
    add_result 0.05 "no new test files created (use existing)" 0
fi

# [agent_config] (0.05): "Do not edit a # Copied from block" — CLAUDE.md:65 @ c55f6505
# Verify no Copied-from blocks were modified
if python3 -c "
import subprocess
r = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, cwd='/workspace/transformers')
diff = r.stdout
# Check if any hunk touches a '# Copied from' line
import re
in_hunk = False
violation = False
for line in diff.split('\n'):
    if line.startswith('@@'):
        in_hunk = True
    elif in_hunk and (line.startswith('+') or line.startswith('-')) and not line.startswith('+++') and not line.startswith('---'):
        if '# Copied from' in line:
            violation = True
            break
import sys
sys.exit(1 if violation else 0)
" 2>/dev/null; then
    add_result 0.05 "no Copied-from blocks modified" 1
else
    add_result 0.05 "no Copied-from blocks modified" 0
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "SCORE: $SCORE / $TOTAL"

echo "$SCORE" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "
parts = '$DETAILS'.split('\\\\n')
s = 0
for p in parts:
    if 'incorrect-class set' in p or 'TOKENIZER_MAPPING_NAMES' in p:
        if 'PASS' in p:
            w = p.split('(')[1].split(')')[0]
            s += float(w)
print(f'{s:.2f}')
")

python3 -c "
import json
json.dump({
    'reward': $SCORE,
    'behavioral': $BEHAVIORAL,
    'regression': round($SCORE - $BEHAVIORAL - 0.15 if $SCORE > $BEHAVIORAL + 0.15 else max(0, $SCORE - $BEHAVIORAL), 2),
    'config': 0.15 if $SCORE >= $TOTAL else round(max(0, $SCORE - $BEHAVIORAL - 0.15), 2),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
