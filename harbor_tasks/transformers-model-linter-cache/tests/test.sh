#!/usr/bin/env bash
set +e

SCORE=0

log_check() {
    local name="$1" weight="$2" result="$3" tag="$4"
    if [ "$result" = "pass" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        echo "  PASS ($weight) $tag: $name"
    else
        echo "  FAIL ($weight) $tag: $name"
    fi
}

cd /workspace/transformers

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Modified files must parse without syntax errors
if python3 -c "
import ast, sys
for f in ['utils/check_modeling_structure.py']:
    try:
        with open(f) as fh:
            ast.parse(fh.read(), filename=f)
    except SyntaxError as e:
        print(f'Syntax error in {f}: {e}', file=sys.stderr)
        sys.exit(1)
print('Syntax OK')
"; then
    echo "  GATE PASSED"
else
    echo "  GATE FAILED — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== Fail-to-pass behavioral tests ==="

# --- T1: Content hash function works correctly (discovered dynamically) ---
# [pr_diff] (0.25): Content hash produces deterministic, content-sensitive digests
T1=$(python3 -c "
import sys, inspect
sys.path.insert(0, 'utils')
import check_modeling_structure as mod

# Discover the hash function: any module-level callable that accepts (str, set)
# and returns a hex digest string. Does NOT require a specific name.
hash_func = None
for name, obj in vars(mod).items():
    if name.startswith('__') or not callable(obj):
        continue
    try:
        sig = inspect.signature(obj)
        if len(sig.parameters) < 2:
            continue
        result = obj('probe_text_12345', {'probe_rule_A'})
        if isinstance(result, str) and len(result) >= 32 and all(c in '0123456789abcdef' for c in result):
            hash_func = obj
            break
    except Exception:
        continue

assert hash_func is not None, 'No content hash function found in module (need callable taking text + rules, returning hex string)'

# Same input => same hash (deterministic)
h1 = hash_func('hello', {'ruleA', 'ruleB'})
h2 = hash_func('hello', {'ruleA', 'ruleB'})
assert h1 == h2, f'Same input should give same hash: {h1} vs {h2}'

# Different text => different hash
h3 = hash_func('world', {'ruleA', 'ruleB'})
assert h1 != h3, 'Different text should give different hash'

# Different rules => different hash
h4 = hash_func('hello', {'ruleA', 'ruleC'})
assert h1 != h4, 'Different rules should give different hash'

# Rule order doesn't matter (sorted internally)
h5 = hash_func('hello', {'ruleB', 'ruleA'})
assert h1 == h5, f'Rule order should not matter: {h1} vs {h5}'

# Returns a hex string of reasonable length
assert isinstance(h1, str) and len(h1) >= 32, f'Expected hex string >=32 chars, got len={len(h1)}'

print('OK')
" 2>&1 && echo "pass" || echo "fail")
T1_RESULT="${T1##*$'\n'}"
log_check "Content hash function: deterministic, sensitive, order-insensitive" 0.25 "$T1_RESULT" "[pr_diff]"

# --- T2: Cache save/load round-trip (discovered dynamically) ---
# [pr_diff] (0.20): Cache persistence: save then load returns same data
T2=$(python3 -c "
import sys, inspect, tempfile, json
from pathlib import Path
sys.path.insert(0, 'utils')
import check_modeling_structure as mod

# Find module-level Path constant ending in .json (cache path)
cache_attr = None
cache_path_val = None
for name, val in vars(mod).items():
    if isinstance(val, Path) and val.suffix == '.json' and name.startswith('_') or (isinstance(val, Path) and val.suffix == '.json'):
        # Prefer ones with 'cache' in name, but accept any .json Path
        if cache_attr is None or 'cache' in name.lower():
            cache_attr = name
            cache_path_val = val

assert cache_attr is not None, 'No .json Path constant found in module'
assert cache_path_val.parent == Path(mod.__file__).resolve().parent, \
    f'Cache should be next to script, got {cache_path_val.parent}'

# Find save function: callable with 'cache' in name OR takes 1 dict param
# Find load function: callable with 'cache' in name OR takes 0 params returning dict
save_fn = load_fn = None
for name, obj in vars(mod).items():
    if not callable(obj) or name.startswith('__'):
        continue
    if 'cache' not in name.lower():
        continue
    try:
        sig = inspect.signature(obj)
        nparams = len(sig.parameters)
        if nparams == 1 and save_fn is None:
            save_fn = obj
        elif nparams == 0 and load_fn is None:
            # Verify it returns a dict
            load_fn = obj
    except Exception:
        continue

assert save_fn is not None, 'No cache save function found (callable with cache in name, 1 param)'
assert load_fn is not None, 'No cache load function found (callable with cache in name, 0 params)'

# Test round-trip with temp file
orig = getattr(mod, cache_attr)
tmp = Path(tempfile.mktemp(suffix='.json'))
setattr(mod, cache_attr, tmp)
try:
    data = {'file_a.py': 'abc123', 'file_b.py': 'def456'}
    save_fn(data)
    loaded = load_fn()
    assert loaded == data, f'Round-trip failed: {loaded} != {data}'

    # Verify JSON on disk
    raw = json.loads(tmp.read_text())
    assert raw == data, f'JSON on disk mismatch: {raw}'

    # Missing file returns empty dict
    tmp.unlink()
    empty = load_fn()
    assert empty == {}, f'Missing file should return empty dict, got {empty}'

    print('OK')
finally:
    setattr(mod, cache_attr, orig)
    if tmp.exists():
        tmp.unlink()
" 2>&1 && echo "pass" || echo "fail")
T2_RESULT="${T2##*$'\n'}"
log_check "Cache save/load round-trip works" 0.20 "$T2_RESULT" "[pr_diff]"

# --- T3: CLI has a cache-disable flag ---
# [pr_diff] (0.10): Script advertises a flag to disable/bypass caching
T3=$(python3 -c "
import subprocess, sys
result = subprocess.run(
    ['python3', 'utils/check_modeling_structure.py', '--help'],
    capture_output=True, text=True, timeout=30
)
help_text = (result.stdout + result.stderr).lower()
# Must mention cache in --help (accepts any reasonable flag name)
if 'cache' not in help_text:
    print('No cache-related option in --help output')
    print('Searched in:', help_text[:500])
    sys.exit(1)
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T3_RESULT="${T3##*$'\n'}"
log_check "CLI has cache-disable flag (any name)" 0.10 "$T3_RESULT" "[pr_diff]"

# --- T4: Makefile has typing target that runs model linter ---
# [pr_diff] (0.10): New make typing target exists and includes model linter
T4=$(python3 -c "
import re

with open('Makefile') as f:
    content = f.read()

# Check 'typing' target exists
assert re.search(r'^typing:', content, re.MULTILINE), 'Makefile must have a typing: target'

# Check model linter is invoked under typing
typing_match = re.search(r'^typing:.*?(?=^\S|\Z)', content, re.MULTILINE | re.DOTALL)
assert typing_match, 'Could not find typing target block'
typing_block = typing_match.group()
assert 'check_modeling_structure' in typing_block, 'typing target must run check_modeling_structure'

print('OK')
" 2>&1 && echo "pass" || echo "fail")
T4_RESULT="${T4##*$'\n'}"
log_check "Makefile has typing target with model linter" 0.10 "$T4_RESULT" "[pr_diff]"

# --- T5: Redundant Makefile targets removed ---
# [pr_diff] (0.05): Legacy check-model-rules targets are removed
T5=$(python3 -c "
import re

with open('Makefile') as f:
    content = f.read()

for target in ['check-model-rules:', 'check-model-rules-pr:', 'check-model-rules-all:']:
    if re.search(r'^' + re.escape(target), content, re.MULTILINE):
        print(f'Redundant target {target} still present in Makefile')
        import sys; sys.exit(1)

print('OK')
" 2>&1 && echo "pass" || echo "fail")
T5_RESULT="${T5##*$'\n'}"
log_check "Redundant Makefile targets removed" 0.05 "$T5_RESULT" "[pr_diff]"

echo ""
echo "=== Pass-to-pass regression tests ==="

# --- T6: parse_args backward compatibility ---
# [pr_diff] (0.10): Existing CLI flags still work after changes
T6=$(python3 -c "
import sys
sys.path.insert(0, 'utils')
from check_modeling_structure import parse_args

sys.argv = ['check_modeling_structure.py', '--list-rules']
args = parse_args()
assert args.list_rules == True, 'list_rules should be True'

sys.argv = ['check_modeling_structure.py', '--no-progress']
args = parse_args()
assert args.no_progress == True, 'no_progress should be True'

sys.argv = ['check_modeling_structure.py', '--changed-only', '--base-ref', 'main']
args = parse_args()
assert args.changed_only == True
assert args.base_ref == 'main'

print('OK')
" 2>&1 && echo "pass" || echo "fail")
T6_RESULT="${T6##*$'\n'}"
log_check "parse_args backward compat with standard flags" 0.10 "$T6_RESULT" "[pr_diff]"

echo ""
echo "=== Config-derived checks ==="

# --- T7: ruff lint on modified file ---
# [agent_config] (0.10): "make style runs formatters and linters (ruff)" — .ai/AGENTS.md:2 @ aa1c36f1
T7=$(python3 -c "
import subprocess, sys
result = subprocess.run(
    ['ruff', 'check', '--select=E,W,F', '--no-fix', 'utils/check_modeling_structure.py'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('OK')
else:
    print(result.stdout[:500])
    print(result.stderr[:500])
    sys.exit(1)
" 2>&1 && echo "pass" || echo "fail")
T7_RESULT="${T7##*$'\n'}"
log_check "ruff lint check on utils/check_modeling_structure.py" 0.10 "$T7_RESULT" "[agent_config]"

echo ""
echo "=== Structural checks ==="

# --- T8: .gitignore excludes cache file ---
# [pr_diff] (0.05): Cache file excluded from version control
T8=$(python3 -c "
with open('.gitignore') as f:
    content = f.read()

# Must have a line that excludes a cache file related to the model linter.
# Accept any reasonable pattern: check_modeling_structure_cache, .lint_cache, etc.
lines = content.lower().split('\n')
found = any(
    'cache' in line and ('model' in line or 'structure' in line or 'lint' in line or 'check_modeling' in line)
    for line in lines if not line.strip().startswith('#')  # skip comments for the pattern match
) or any(
    'check_modeling_structure' in line and 'cache' in line
    for line in lines
)
# Also accept if any non-comment line mentions cache + json in the utils context
if not found:
    found = any(
        'cache' in line and '.json' in line
        for line in lines if not line.strip().startswith('#')
    )
assert found, 'No model linter cache exclusion found in .gitignore'
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T8_RESULT="${T8##*$'\n'}"
log_check ".gitignore excludes model linter cache" 0.05 "$T8_RESULT" "[pr_diff]"

# --- T9: Agent config references make typing ---
# [pr_diff] (0.05): .ai/AGENTS.md updated to reference make typing
T9=$(python3 -c "
import sys

try:
    with open('.ai/AGENTS.md') as f:
        content = f.read()
except FileNotFoundError:
    print('.ai/AGENTS.md not found')
    sys.exit(1)

# Should reference 'make typing' or 'typing' target
if 'typing' not in content.lower():
    print('.ai/AGENTS.md should reference make typing')
    sys.exit(1)

print('OK')
" 2>&1 && echo "pass" || echo "fail")
T9_RESULT="${T9##*$'\n'}"
log_check ".ai/AGENTS.md references make typing" 0.05 "$T9_RESULT" "[pr_diff]"

echo ""
echo "=== Results ==="
echo "Score: $SCORE / 1.00"

# Write reward
mkdir -p /logs/verifier
REWARD=$(python3 -c "print(f'{min(1.0, $SCORE):.4f}')")
echo "$REWARD" > /logs/verifier/reward.txt
echo "reward=$REWARD"

# Write detailed JSON
python3 -c "
import json
data = {
    'reward': min(1.0, $SCORE),
    'behavioral': min(0.75, sum([
        $( [ \"$T1_RESULT\" = \"pass\" ] && echo 0.25 || echo 0 ),
        $( [ \"$T2_RESULT\" = \"pass\" ] && echo 0.20 || echo 0 ),
        $( [ \"$T3_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
        $( [ \"$T6_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
    ])),
    'regression': $( [ \"$T6_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
    'config': $( [ \"$T7_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
    'structural': min(0.15, sum([
        $( [ \"$T4_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
        $( [ \"$T5_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
        $( [ \"$T8_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
        $( [ \"$T9_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
    ])),
}
print(json.dumps(data, indent=2))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
