#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
FILE1="scripts/ci/utils/diffusion/publish_comparison_results.py"
FILE2="scripts/ci/utils/diffusion/publish_diffusion_gt.py"

echo "=== GATE: Syntax check ==="
# [pr_diff] (0): Python syntax gate — abort on failure
for F in "$FILE1" "$FILE2"; do
    if ! python3 -c "import py_compile; py_compile.compile('$F', doraise=True)" 2>&1; then
        echo "GATE FAILED: syntax error in $F"
        echo "0" > /logs/verifier/reward.txt
        exit 0
    fi
done
echo "GATE PASSED"
echo ""

# ---------------------------------------------------------------------------
# Fail-to-pass behavioral tests (0.70 total)
# ---------------------------------------------------------------------------

echo "=== Behavioral: publish_comparison_results.py imports successfully ==="
# [pr_diff] (0.25): Script can be imported as standalone (no ImportError)
IMPORT1_RESULT=$(python3 -c "
import sys, importlib.util
# Import as standalone script (not as package) — simulates 'python3 script.py'
spec = importlib.util.spec_from_file_location('publish_comparison_results', '$FILE1')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    # Verify the key functions are accessible
    required = ['create_blobs', 'create_commit', 'create_tree', 'get_branch_sha',
                'get_tree_sha', 'verify_token_permissions']
    missing = [r for r in required if not hasattr(mod, r)]
    if missing:
        print(f'FAIL: missing attributes: {missing}')
    else:
        print('PASS')
except ImportError as e:
    print(f'FAIL: ImportError: {e}')
except Exception as e:
    # SystemExit from missing env vars is OK — import succeeded
    if 'SystemExit' in type(e).__name__:
        print('PASS')
    else:
        print(f'FAIL: {type(e).__name__}: {e}')
" 2>&1 | tail -1)
echo "  Result: $IMPORT1_RESULT"
if [[ "$IMPORT1_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")
echo ""

echo "=== Behavioral: publish_diffusion_gt.py imports successfully ==="
# [pr_diff] (0.25): Script can be imported as standalone (no ImportError)
IMPORT2_RESULT=$(python3 -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('publish_diffusion_gt', '$FILE2')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    required = ['create_blobs', 'create_commit', 'create_tree', 'get_branch_sha',
                'get_tree_sha', 'verify_token_permissions']
    missing = [r for r in required if not hasattr(mod, r)]
    if missing:
        print(f'FAIL: missing attributes: {missing}')
    else:
        print('PASS')
except ImportError as e:
    print(f'FAIL: ImportError: {e}')
except Exception as e:
    if 'SystemExit' in type(e).__name__:
        print('PASS')
    else:
        print(f'FAIL: {type(e).__name__}: {e}')
" 2>&1 | tail -1)
echo "  Result: $IMPORT2_RESULT"
if [[ "$IMPORT2_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")
echo ""

echo "=== Behavioral: publish_traces helpers are callable ==="
# [pr_diff] (0.20): Imported functions are the real implementations from publish_traces
CALLABLE_RESULT=$(python3 -c "
import sys, importlib.util, inspect

spec = importlib.util.spec_from_file_location('publish_comparison_results', '$FILE1')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass

# Verify imported functions are actual callables from publish_traces
funcs = ['create_blobs', 'create_commit', 'create_tree', 'get_branch_sha',
         'get_tree_sha', 'is_permission_error', 'is_rate_limit_error',
         'update_branch_ref', 'verify_token_permissions']
errors = []
for name in funcs:
    fn = getattr(mod, name, None)
    if fn is None:
        errors.append(f'{name} not found')
    elif not callable(fn):
        errors.append(f'{name} not callable')
    else:
        # Verify it comes from publish_traces module
        src_file = getattr(inspect.getmodule(fn), '__file__', '') or ''
        if 'publish_traces' not in src_file:
            errors.append(f'{name} not from publish_traces (from {src_file})')

if errors:
    print(f'FAIL: {errors}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $CALLABLE_RESULT"
if [[ "$CALLABLE_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.20)")
echo ""

# ---------------------------------------------------------------------------
# Pass-to-pass regression tests (0.15 total)
# ---------------------------------------------------------------------------

echo "=== Regression: publish_traces.py still importable ==="
# [pr_diff] (0.05): The upstream module itself still works
TRACES_RESULT=$(python3 -c "
import sys
sys.path.insert(0, 'scripts/ci/utils')
import publish_traces
required = ['create_blobs', 'create_commit', 'create_tree', 'get_branch_sha',
            'get_tree_sha', 'is_permission_error', 'is_rate_limit_error',
            'update_branch_ref', 'verify_token_permissions']
missing = [r for r in required if not hasattr(publish_traces, r)]
if missing:
    print(f'FAIL: missing: {missing}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $TRACES_RESULT"
if [[ "$TRACES_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

echo "=== Regression: publish_comparison_results has publish_comparison ==="
# [pr_diff] (0.05): Core function still exists
PUB_COMP_RESULT=$(python3 -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('publish_comparison_results', '$FILE1')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
if hasattr(mod, 'publish_comparison'):
    print('PASS')
else:
    print('FAIL: publish_comparison function missing')
" 2>&1 | tail -1)
echo "  Result: $PUB_COMP_RESULT"
if [[ "$PUB_COMP_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

echo "=== Regression: publish_diffusion_gt has publish and collect_images ==="
# [pr_diff] (0.05): Core functions still exist
PUB_GT_RESULT=$(python3 -c "
import sys, importlib.util
spec = importlib.util.spec_from_file_location('publish_diffusion_gt', '$FILE2')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except SystemExit:
    pass
missing = []
for fn in ['publish', 'collect_images']:
    if not hasattr(mod, fn):
        missing.append(fn)
if missing:
    print(f'FAIL: missing functions: {missing}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $PUB_GT_RESULT"
if [[ "$PUB_GT_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

# ---------------------------------------------------------------------------
# Config-derived checks (0.15 total)
# ---------------------------------------------------------------------------

echo "=== Config: No wildcard imports ==="
# [agent_config] (0.05): No wildcard imports in modified files
WILDCARD_RESULT=$(python3 -c "
import re
errors = []
for f in ['$FILE1', '$FILE2']:
    with open(f) as fh:
        content = fh.read()
    wildcards = re.findall(r'from\s+\S+\s+import\s+\*', content)
    if wildcards:
        errors.append(f'{f}: {wildcards}')
if errors:
    print(f'FAIL: wildcard imports found: {errors}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $WILDCARD_RESULT"
if [[ "$WILDCARD_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

echo "=== Config: Anti-stub check ==="
# [agent_config] (0.05): Import sections not stubbed or emptied
ANTISTUB_RESULT=$(python3 -c "
errors = []
for f in ['$FILE1', '$FILE2']:
    with open(f) as fh:
        content = fh.read()
    # Must still import these specific functions
    for fn in ['create_blobs', 'create_commit', 'get_branch_sha']:
        if fn not in content:
            errors.append(f'{f} missing import of {fn}')
    if len(content) < 500:
        errors.append(f'{f} suspiciously short ({len(content)} chars)')
if errors:
    print(f'FAIL: {errors}')
else:
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $ANTISTUB_RESULT"
if [[ "$ANTISTUB_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

echo "=== Config: Both files modified ==="
# [agent_config] (0.05): Both scripts must be fixed, not just one
BOTH_RESULT=$(python3 -c "
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True, text=True)
diff_output = result.stdout
if not diff_output:
    result = subprocess.run(['git', 'diff', '--name-only', '--cached'], capture_output=True, text=True)
    diff_output = result.stdout
if not diff_output:
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], capture_output=True, text=True)
    diff_output = result.stdout

files = diff_output.strip().split('\n') if diff_output.strip() else []
has_f1 = any('publish_comparison_results.py' in f for f in files)
has_f2 = any('publish_diffusion_gt.py' in f for f in files)

if has_f1 and has_f2:
    print('PASS')
elif has_f1:
    print('FAIL: only publish_comparison_results.py modified')
elif has_f2:
    print('FAIL: only publish_diffusion_gt.py modified')
else:
    # Maybe both were fixed but check import works
    print('PASS')
" 2>&1 | tail -1)
echo "  Result: $BOTH_RESULT"
if [[ "$BOTH_RESULT" == "PASS" ]]; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

# ---------------------------------------------------------------------------
# Final score
# ---------------------------------------------------------------------------

echo "=== FINAL ==="
echo "Score: $SCORE / $TOTAL"

# Write reward
mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Write detailed JSON
python3 -c "
import json
score = $SCORE
behavioral = min(score, 0.70)
regression = max(0, min(score - 0.70, 0.15))
config = max(0, min(score - 0.85, 0.15))
json.dump({
    'reward': score,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
}, open('/logs/verifier/reward.json', 'w'))
print(json.dumps({'reward': score}, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
