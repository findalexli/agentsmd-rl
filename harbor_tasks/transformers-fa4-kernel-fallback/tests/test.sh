#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight=$1 pass=$2 label=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight): $label\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $label\n"
    fi
}

REPO=/workspace/transformers

# ============================================================
# GATE: Syntax check on both modified files
# ============================================================
# [pr_diff] (gate): Both files must be valid Python
python3 -c "
import ast, sys
for f in ['$REPO/src/transformers/modeling_flash_attention_utils.py',
          '$REPO/src/transformers/modeling_utils.py']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}', file=sys.stderr)
        sys.exit(1)
" || { echo "0.0" > /logs/verifier/reward.txt; echo '{"reward":0.0,"reason":"syntax error"}' > /logs/verifier/reward.json; exit 0; }

# ============================================================
# BEHAVIORAL: Fail-to-pass tests (0.70 total)
# ============================================================

# [pr_diff] (0.25): FLASH_ATTN_KERNEL_FALLBACK contains flash_attention_4 entry
PASS=0
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_flash_attention_utils import FLASH_ATTN_KERNEL_FALLBACK
assert 'flash_attention_4' in FLASH_ATTN_KERNEL_FALLBACK, 'flash_attention_4 not in FLASH_ATTN_KERNEL_FALLBACK'
print('OK: flash_attention_4 found in FLASH_ATTN_KERNEL_FALLBACK')
" && PASS=1
add_result 0.25 "$PASS" "FLASH_ATTN_KERNEL_FALLBACK contains flash_attention_4"

# [pr_diff] (0.25): The FA4 skip logic is removed from _check_and_adjust_attn_implementation
PASS=0
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
# Read the source and check the loop body doesn't skip version 4
import inspect
from transformers.modeling_utils import PreTrainedModel
source = inspect.getsource(PreTrainedModel._check_and_adjust_attn_implementation)
# The buggy code has 'if fa_version == 4:' followed by 'continue'
if 'fa_version == 4' in source and 'continue' in source:
    # Verify they are close together (within 3 lines)
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if 'fa_version == 4' in line:
            nearby = ''.join(lines[i:i+3])
            if 'continue' in nearby:
                print('FAIL: FA4 skip logic still present', file=sys.stderr)
                sys.exit(1)
print('OK: FA4 skip logic removed')
" && PASS=1
add_result 0.25 "$PASS" "FA4 skip logic removed from _check_and_adjust_attn_implementation"

# [pr_diff] (0.20): FA4 fallback value is a valid kernels-community package name
PASS=0
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_flash_attention_utils import FLASH_ATTN_KERNEL_FALLBACK
val = FLASH_ATTN_KERNEL_FALLBACK.get('flash_attention_4', '')
# Must be a kernels-community path (like the other entries)
assert val.startswith('kernels-community/'), f'Expected kernels-community/ prefix, got: {val}'
assert len(val) > len('kernels-community/'), 'Package name is empty after prefix'
print(f'OK: flash_attention_4 maps to {val}')
" && PASS=1
add_result 0.20 "$PASS" "FA4 fallback value is a valid kernels-community package"

# ============================================================
# PASS-TO-PASS: Existing entries still work (0.15)
# ============================================================

# [pr_diff] (0.10): FA2 and FA3 entries unchanged in FLASH_ATTN_KERNEL_FALLBACK
PASS=0
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_flash_attention_utils import FLASH_ATTN_KERNEL_FALLBACK
assert FLASH_ATTN_KERNEL_FALLBACK['flash_attention_2'] == 'kernels-community/flash-attn2', \
    f'FA2 entry changed: {FLASH_ATTN_KERNEL_FALLBACK[\"flash_attention_2\"]}'
assert FLASH_ATTN_KERNEL_FALLBACK['flash_attention_3'] == 'kernels-community/vllm-flash-attn3', \
    f'FA3 entry changed: {FLASH_ATTN_KERNEL_FALLBACK[\"flash_attention_3\"]}'
print('OK: FA2 and FA3 entries preserved')
" && PASS=1
add_result 0.10 "$PASS" "FA2 and FA3 kernel fallback entries unchanged"

# [pr_diff] (0.05): FLASH_ATTENTION_COMPATIBILITY_MATRIX still has all 3 versions
PASS=0
python3 -c "
import sys
sys.path.insert(0, '$REPO/src')
from transformers.modeling_flash_attention_utils import FLASH_ATTENTION_COMPATIBILITY_MATRIX
for v in [2, 3, 4]:
    assert v in FLASH_ATTENTION_COMPATIBILITY_MATRIX, f'Version {v} missing from matrix'
print('OK: All FA versions present in compatibility matrix')
" && PASS=1
add_result 0.05 "$PASS" "FLASH_ATTENTION_COMPATIBILITY_MATRIX has all versions"

# ============================================================
# CONFIG-DERIVED: Agent config rules (0.15)
# ============================================================

# [agent_config] (0.05): "make style" passes — CLAUDE.md:1 @ a269c990
PASS=0
cd "$REPO"
python3 -c "
import subprocess, sys
# Run ruff check on the two changed files only
result = subprocess.run(
    ['python3', '-m', 'ruff', 'check',
     'src/transformers/modeling_flash_attention_utils.py',
     'src/transformers/modeling_utils.py'],
    capture_output=True, text=True, cwd='$REPO'
)
if result.returncode == 0:
    print('OK: ruff check passes')
else:
    print(f'FAIL: ruff check errors:\n{result.stdout}\n{result.stderr}', file=sys.stderr)
    sys.exit(1)
" && PASS=1
add_result 0.05 "$PASS" "ruff check passes on changed files"

# [agent_config] (0.10): Diff is minimal — .github/copilot-instructions.md:12 @ a269c990
PASS=0
python3 -c "
import subprocess, sys
result = subprocess.run(['git', 'diff', '--stat', 'HEAD'], capture_output=True, text=True, cwd='$REPO')
diff_output = result.stdout.strip()
if not diff_output:
    result = subprocess.run(['git', 'diff', '--stat', '--cached', 'HEAD'], capture_output=True, text=True, cwd='$REPO')
    diff_output = result.stdout.strip()
if not diff_output:
    result = subprocess.run(['git', 'diff', '--stat', 'HEAD~1'], capture_output=True, text=True, cwd='$REPO')
    diff_output = result.stdout.strip()
# Count files changed
lines = [l for l in diff_output.splitlines() if '|' in l]
n_files = len(lines)
if n_files <= 3:
    print(f'OK: {n_files} files changed (within minimal diff budget)')
else:
    print(f'FAIL: {n_files} files changed (expected <=3)', file=sys.stderr)
    sys.exit(1)
" && PASS=1
add_result 0.10 "$PASS" "Diff touches at most 3 files"

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "===== RESULTS ====="
printf "$DETAILS"
echo "Score: $SCORE / $TOTAL"

# Normalize to 1.0 (weights already sum to 1.0)
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = $SCORE
details = {
    'reward': round(score, 4),
    'behavioral': round(min(0.70, score), 4),
    'regression': round(max(0, min(0.15, score - 0.70)), 4),
    'config': round(max(0, min(0.15, score - 0.85)), 4),
}
json.dump(details, open('/logs/verifier/reward.json', 'w'), indent=2)
print(json.dumps(details, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
