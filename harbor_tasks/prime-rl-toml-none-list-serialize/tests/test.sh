#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
LOGS=""

log() { LOGS="${LOGS}\n$1"; echo "$1"; }

add_score() {
    local weight=$1 name=$2 pass=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        log "PASS ($weight): $name"
    else
        log "FAIL ($weight): $name"
    fi
}

cd /workspace/prime-rl

# ============================================================
# GATE: Syntax check — abort if config.py is not valid Python
# ============================================================
# [pr_diff] (gate): config.py must be syntactically valid
if python3 -c "import ast; ast.parse(open('src/prime_rl/utils/config.py').read())" 2>/dev/null; then
    log "GATE PASS: config.py syntax valid"
else
    log "GATE FAIL: config.py has syntax errors"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    printf "$LOGS"
    exit 0
fi

# ============================================================
# Fail-to-pass: Behavioral tests (0.65 total)
# ============================================================

# [pr_diff] (0.20): None inside a flat list is converted to "None" string
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'key': [None, 'a', None]})
assert result == {'key': ['None', 'a', 'None']}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.20 "[pr_diff] None inside flat list converted" "$P"

# [pr_diff] (0.20): None inside a dict nested in a list is converted
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'key': [{'nested': None, 'ok': 1}]})
assert result == {'key': [{'nested': 'None', 'ok': 1}]}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.20 "[pr_diff] None inside dict-in-list converted" "$P"

# [pr_diff] (0.15): Deeply nested None (list of list) is converted
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'key': [[None, 1], [2, None]]})
assert result == {'key': [['None', 1], [2, 'None']]}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.15 "[pr_diff] Deeply nested list-of-list None converted" "$P"

# [pr_diff] (0.10): End-to-end TOML round-trip with None in list
RESULT=$(python3 -c "
import tomli_w
from prime_rl.utils.config import none_to_none_str
data = {'section': {'items': [None, 'hello', None], 'nested': {'vals': [1, None]}}}
converted = none_to_none_str(data)
# Should not raise — TOML serialization succeeds
toml_bytes = tomli_w.dumps(converted)
assert 'None' in toml_bytes, f'Missing None string in TOML output'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.10 "[pr_diff] TOML round-trip with None in list succeeds" "$P"

# ============================================================
# Pass-to-pass: Regression tests (0.15 total)
# ============================================================

# [repo_tests] (0.05): Top-level None still converted
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'a': None, 'b': 'hello'})
assert result == {'a': 'None', 'b': 'hello'}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[repo_tests] Top-level None still works" "$P"

# [repo_tests] (0.05): Nested dict None still converted
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'outer': {'inner': None, 'val': 42}})
assert result == {'outer': {'inner': 'None', 'val': 42}}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[repo_tests] Nested dict None still works" "$P"

# [repo_tests] (0.05): Non-None values pass through unchanged
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'a': 1, 'b': 'str', 'c': [1, 2], 'd': {'e': True}})
assert result == {'a': 1, 'b': 'str', 'c': [1, 2], 'd': {'e': True}}, f'Got: {result}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[repo_tests] Non-None values pass through" "$P"

# ============================================================
# Structural: Anti-stub check (0.10)
# ============================================================

# [static] (0.05): none_to_none_str still exists as a callable function
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
assert callable(none_to_none_str), 'none_to_none_str must be callable'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[static] none_to_none_str is callable" "$P"

# [static] (0.05): Function is not a trivial stub (returns meaningful output)
RESULT=$(python3 -c "
from prime_rl.utils.config import none_to_none_str
result = none_to_none_str({'a': None, 'b': [None]})
assert isinstance(result, dict), 'Must return dict'
assert len(result) == 2, 'Must preserve all keys'
assert result['a'] == 'None', 'Must convert None to string'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[static] Function not stubbed" "$P"

# ============================================================
# Config-derived checks (0.10)
# ============================================================

# [agent_config] (0.05): No unnecessary try/except — AGENTS.md:5
RESULT=$(python3 -c "
import ast
tree = ast.parse(open('src/prime_rl/utils/config.py').read())
try_blocks = [n for n in ast.walk(tree) if isinstance(n, ast.Try)]
# The file should have zero try/except blocks (original has none)
assert len(try_blocks) == 0, f'Found {len(try_blocks)} try/except blocks — AGENTS.md says avoid them'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[agent_config] No unnecessary try/except — AGENTS.md:5" "$P"

# [agent_config] (0.05): No unnecessary comments explaining work process — AGENTS.md:7
RESULT=$(python3 -c "
import re
content = open('src/prime_rl/utils/config.py').read()
# Check for comments referencing old code or work process
bad_patterns = [
    r'#.*used to.*but now',
    r'#.*old code',
    r'#.*previous(ly)?',
    r'#.*was originally',
    r'#.*changed from',
    r'#.*refactored',
]
for pat in bad_patterns:
    m = re.search(pat, content, re.IGNORECASE)
    assert m is None, f'Found work-process comment: {m.group()}'
print('OK')
" 2>&1)
[ "$RESULT" = "OK" ] && P=1 || P=0
add_score 0.05 "[agent_config] No work-process comments — AGENTS.md:7" "$P"

# ============================================================
# Write results
# ============================================================

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

# Compute component scores for reward.json
BEHAVIORAL=$(python3 -c "print(min($SCORE, 0.65))")
REGRESSION=$(python3 -c "
b = $SCORE - $BEHAVIORAL if $SCORE > 0.65 else 0
print(min(b, 0.15))
")

echo ""
echo "=== Score: $SCORE / $TOTAL ==="
printf "$LOGS"

python3 -c "
import json
score = $SCORE
json.dump({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.65), 4),
    'regression': round(min(max(score - 0.65, 0), 0.15), 4),
    'config': round(min(max(score - 0.80, 0), 0.10), 4),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
