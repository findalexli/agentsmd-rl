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
if python3 -c "import py_compile; py_compile.compile('src/transformers/image_utils.py', doraise=True)" 2>/dev/null; then
    echo "GATE PASS: syntax OK"
else
    echo "GATE FAIL: syntax error in image_utils.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Fail-to-pass: Behavioral tests (weight = 0.70) ──

# [pr_diff] (0.25): SizeDict | dict returns SizeDict with merged fields
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20)
result = sd | {'longest_edge': 30}
assert isinstance(result, SizeDict), f'Expected SizeDict, got {type(result)}'
assert result.height == 10, f'Expected height=10, got {result.height}'
assert result.width == 20, f'Expected width=20, got {result.width}'
assert result.longest_edge == 30, f'Expected longest_edge=30, got {result.longest_edge}'
print('OK')
" 2>&1; then
    pass_check 0.25 "[pr_diff] SizeDict | dict returns merged SizeDict"
else
    fail_check 0.25 "[pr_diff] SizeDict | dict returns merged SizeDict"
fi

# [pr_diff] (0.25): dict | SizeDict returns plain dict with merged entries
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20)
result = {'longest_edge': 30} | sd
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert not isinstance(result, SizeDict), 'Should be plain dict, not SizeDict'
assert result == {'longest_edge': 30, 'height': 10, 'width': 20}, f'Wrong value: {result}'
print('OK')
" 2>&1; then
    pass_check 0.25 "[pr_diff] dict | SizeDict returns merged plain dict"
else
    fail_check 0.25 "[pr_diff] dict | SizeDict returns merged plain dict"
fi

# [pr_diff] (0.10): SizeDict | SizeDict returns merged SizeDict
if python3 -c "
from transformers.image_utils import SizeDict

sd1 = SizeDict(height=10, width=20)
sd2 = SizeDict(longest_edge=30)
result = sd1 | sd2
assert isinstance(result, SizeDict), f'Expected SizeDict, got {type(result)}'
assert result.height == 10, f'Expected height=10, got {result.height}'
assert result.width == 20, f'Expected width=20, got {result.width}'
assert result.longest_edge == 30, f'Expected longest_edge=30, got {result.longest_edge}'
print('OK')
" 2>&1; then
    pass_check 0.10 "[pr_diff] SizeDict | SizeDict returns merged SizeDict"
else
    fail_check 0.10 "[pr_diff] SizeDict | SizeDict returns merged SizeDict"
fi

# [pr_diff] (0.10): Right side values override left side on conflict
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20)
result = sd | {'height': 50, 'longest_edge': 100}
assert isinstance(result, SizeDict), f'Expected SizeDict, got {type(result)}'
assert result.height == 50, f'Expected overridden height=50, got {result.height}'
assert result.width == 20, f'Expected width=20, got {result.width}'
assert result.longest_edge == 100, f'Expected longest_edge=100, got {result.longest_edge}'
print('OK')
" 2>&1; then
    pass_check 0.10 "[pr_diff] Right side overrides left on key conflict"
else
    fail_check 0.10 "[pr_diff] Right side overrides left on key conflict"
fi

# [pr_diff] (0.05): Unsupported type returns NotImplemented (no crash)
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20)
try:
    result = sd | 42
    assert False, 'Should have raised TypeError'
except TypeError:
    pass
print('OK')
" 2>&1; then
    pass_check 0.05 "[pr_diff] SizeDict | unsupported type raises TypeError"
else
    fail_check 0.05 "[pr_diff] SizeDict | unsupported type raises TypeError"
fi

# ── Pass-to-pass: Existing behavior must not break (weight = 0.15) ──

# [repo_tests] (0.05): SizeDict equality with dict still works
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=224, width=224)
assert sd == {'height': 224, 'width': 224}, 'Dict equality broken'
assert sd != {'height': 224, 'width': 999}, 'Dict inequality broken'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] SizeDict dict equality still works"
else
    fail_check 0.05 "[repo_tests] SizeDict dict equality still works"
fi

# [repo_tests] (0.05): SizeDict __getitem__ and __contains__ still work
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=224, width=224)
assert sd['height'] == 224, '__getitem__ broken'
assert 'height' in sd, '__contains__ broken'
assert 'longest_edge' not in sd, '__contains__ broken for None field'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] SizeDict __getitem__/__contains__ still work"
else
    fail_check 0.05 "[repo_tests] SizeDict __getitem__/__contains__ still work"
fi

# [repo_tests] (0.05): SizeDict dict() conversion still works
if python3 -c "
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20, longest_edge=30)
d = dict(sd)
assert d == {'height': 10, 'width': 20, 'longest_edge': 30}, f'dict() conversion broken: {d}'
print('OK')
" 2>&1; then
    pass_check 0.05 "[repo_tests] SizeDict dict() conversion still works"
else
    fail_check 0.05 "[repo_tests] SizeDict dict() conversion still works"
fi

# ── Config-derived check (weight = 0.10) ──

# [agent_config] (0.05): Minimal diff — "PRs should be as brief as possible" — .github/copilot-instructions.md:18
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

added = [l for l in diff.splitlines() if l.startswith('+') and not l.startswith('+++')]
code_added = [l for l in added if l.strip('+').strip() and not l.strip('+').strip().startswith('#')]
assert len(code_added) < 40, f'Too many lines added ({len(code_added)}), fix should be minimal'
print('OK')
" 2>&1; then
    pass_check 0.05 "[agent_config] Minimal diff size — .github/copilot-instructions.md:18"
else
    fail_check 0.05 "[agent_config] Minimal diff size — .github/copilot-instructions.md:18"
fi

# [agent_config] (0.05): Only image_utils.py modified — "Aim to minimize the size of the diff" — .github/copilot-instructions.md:18
if python3 -c "
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True, text=True, cwd='/repo')
files = result.stdout.strip()
if not files:
    result = subprocess.run(['git', 'diff', '--name-only', '--cached'], capture_output=True, text=True, cwd='/repo')
    files = result.stdout.strip()
if not files:
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], capture_output=True, text=True, cwd='/repo')
    files = result.stdout.strip()

changed = [f for f in files.splitlines() if f.strip()]
# Should only touch image_utils.py (maybe a test file too, but no more than 2)
assert len(changed) <= 2, f'Too many files changed ({len(changed)}): {changed}'
print('OK')
" 2>&1; then
    pass_check 0.05 "[agent_config] Minimal files changed — .github/copilot-instructions.md:18"
else
    fail_check 0.05 "[agent_config] Minimal files changed — .github/copilot-instructions.md:18"
fi

# ── Compute final score ──
echo ""
echo "Score: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

# Build reward.json
python3 -c "
import json
score = $SCORE
behavioral = min(score, 0.75)
regression = max(0, min(score - 0.75, 0.15))
config = max(0, min(score - 0.9, 0.1))
style = 0.0
data = {'reward': round(score, 4), 'behavioral': round(behavioral, 4), 'regression': round(regression, 4), 'config': round(config, 4), 'style_rubric': round(style, 4)}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
