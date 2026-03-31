#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0

pass_check() {
    local weight=$1 desc=$2
    SCORE=$(python3 -c "print($SCORE + $weight)")
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    echo "PASS ($weight): $desc"
}

fail_check() {
    local weight=$1 desc=$2
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    echo "FAIL ($weight): $desc"
}

cd /repo

# ── GATE (0.00): Syntax check — abort on failure ──
# [pr_diff] (0.00): File must parse without syntax errors
if python3 -c "import py_compile; py_compile.compile('src/transformers/image_processing_utils.py', doraise=True)" 2>/dev/null; then
    echo "GATE PASS: syntax OK"
else
    echo "GATE FAIL: syntax error in image_processing_utils.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Fail-to-pass: Behavioral tests (weight >= 0.60) ──

# [pr_diff] (0.35): get_size_dict accepts SizeDict with height/width and returns a plain dict
if python3 -c "
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(height=224, width=224)
result = get_size_dict(sd)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert not isinstance(result, SizeDict), 'Should be plain dict, not SizeDict'
assert result == {'height': 224, 'width': 224}, f'Wrong value: {result}'
print('OK')
" 2>&1; then
    pass_check 0.35 "[pr_diff] get_size_dict accepts SizeDict(height=224, width=224)"
else
    fail_check 0.35 "[pr_diff] get_size_dict accepts SizeDict(height=224, width=224)"
fi

# [pr_diff] (0.20): get_size_dict accepts SizeDict with shortest_edge
if python3 -c "
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(shortest_edge=256)
result = get_size_dict(sd, default_to_square=False)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert result == {'shortest_edge': 256}, f'Wrong value: {result}'
print('OK')
" 2>&1; then
    pass_check 0.20 "[pr_diff] get_size_dict accepts SizeDict(shortest_edge=256)"
else
    fail_check 0.20 "[pr_diff] get_size_dict accepts SizeDict(shortest_edge=256)"
fi

# [pr_diff] (0.15): get_size_dict accepts SizeDict with shortest_edge + longest_edge
if python3 -c "
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(shortest_edge=800, longest_edge=1333)
result = get_size_dict(sd, default_to_square=False)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert result == {'shortest_edge': 800, 'longest_edge': 1333}, f'Wrong value: {result}'
print('OK')
" 2>&1; then
    pass_check 0.15 "[pr_diff] get_size_dict accepts SizeDict(shortest_edge=800, longest_edge=1333)"
else
    fail_check 0.15 "[pr_diff] get_size_dict accepts SizeDict(shortest_edge=800, longest_edge=1333)"
fi

# ── Pass-to-pass: Existing behavior must not break (weight ~0.15) ──

# [repo_tests] (0.05): get_size_dict still works with plain dict input
if python3 -c "
from transformers.image_processing_utils import get_size_dict
result = get_size_dict({'height': 224, 'width': 224})
assert result == {'height': 224, 'width': 224}, f'Wrong: {result}'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] get_size_dict works with plain dict"
else
    fail_check 0.05 "[repo_tests] get_size_dict works with plain dict"
fi

# [repo_tests] (0.05): get_size_dict still works with int input
if python3 -c "
from transformers.image_processing_utils import get_size_dict
result = get_size_dict(224)
assert result == {'height': 224, 'width': 224}, f'Wrong: {result}'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] get_size_dict works with int input"
else
    fail_check 0.05 "[repo_tests] get_size_dict works with int input"
fi

# [repo_tests] (0.05): get_size_dict still works with tuple input
if python3 -c "
from transformers.image_processing_utils import get_size_dict
result = get_size_dict((384, 512))
assert result == {'height': 384, 'width': 512}, f'Wrong: {result}'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] get_size_dict works with tuple input"
else
    fail_check 0.05 "[repo_tests] get_size_dict works with tuple input"
fi

# ── Structural: Anti-stub + basic checks (weight <= 0.15) ──

# [pr_diff] (0.10): The isinstance check in get_size_dict handles SizeDict as dict-like (not falling through to convert_to_size_dict)
if python3 -c "
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict
import logging

# Capture log output — if SizeDict falls through to convert_to_size_dict,
# the info log 'should be a dictionary...' fires. It should NOT fire for SizeDict.
logger = logging.getLogger('transformers.image_processing_utils')
handler = logging.handlers if hasattr(logging, 'handlers') else None

import io
stream = io.StringIO()
sh = logging.StreamHandler(stream)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)

sd = SizeDict(height=224, width=224)
result = get_size_dict(sd)

log_output = stream.getvalue()
# The conversion log should NOT appear for SizeDict input
assert 'should be a dictionary' not in log_output, f'SizeDict fell through to convert path: {log_output}'
print('OK')
" 2>&1; then
    pass_check 0.10 "[pr_diff] SizeDict does not fall through to convert_to_size_dict path"
else
    fail_check 0.10 "[pr_diff] SizeDict does not fall through to convert_to_size_dict path"
fi

# [agent_config] (0.05): No unnecessary new functions or large additions — \"PRs should be as brief as possible\" — .github/copilot-instructions.md:18
if python3 -c "
import subprocess
result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, cwd='/repo')
diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True, cwd='/repo')
    diff = result.stdout
if not diff:
    result = subprocess.run(['git', 'diff', 'HEAD~1'], capture_output=True, text=True, cwd='/repo')
    diff = result.stdout

# Count added lines (excluding blank lines and comments)
added = [l for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++')]
code_added = [l for l in added if l.strip('+').strip() and not l.strip('+').strip().startswith('#')]
# A minimal fix should add fewer than 30 lines of code
assert len(code_added) < 30, f'Too many lines added ({len(code_added)}), fix should be minimal'
print('OK')
" 2>&1; then
    pass_check 0.05 "[agent_config] Minimal diff size — .github/copilot-instructions.md:18"
else
    fail_check 0.05 "[agent_config] Minimal diff size — .github/copilot-instructions.md:18"
fi

# ── Compute final score ──
echo ""
echo "Score: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
score = $SCORE
# Approximate breakdown
behavioral = min(score, 0.65)
regression = max(0, min(score - 0.65, 0.15))
config = max(0, min(score - 0.80, 0.05))
style = 0.0
data = {'reward': round(score, 4), 'behavioral': round(behavioral, 4), 'regression': round(regression, 4), 'config': round(config, 4), 'style_rubric': round(style, 4)}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
