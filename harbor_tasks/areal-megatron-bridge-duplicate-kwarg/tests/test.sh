#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
BEHAVIORAL=0
REGRESSION=0
CONFIG=0

log() { echo "[$1] $2 (weight=$3)"; }

add_score() {
    local weight=$1
    local pass=$2
    local tag=$3
    local desc=$4
    local category=$5
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 2))")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 2))")
        eval "$category=\$(python3 -c \"print(round(\$$category + $weight, 2))\")"
        log "PASS" "$desc" "$weight"
    else
        log "FAIL" "$desc" "$weight"
    fi
}

FILE="/workspace/AReaL/areal/engine/megatron_engine.py"

########################################################################
# GATE: Syntax check — abort on failure
########################################################################
# [pr_diff] (GATE): File must be valid Python syntax
python3 -c "
import ast, sys
try:
    ast.parse(open('$FILE').read())
except SyntaxError as e:
    print(f'SyntaxError: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    log "GATE" "Syntax check FAILED — aborting" "0"
    echo "0.00" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
log "GATE" "Syntax check passed" "0"

########################################################################
# BEHAVIORAL: Fail-to-pass tests (0.65 total)
########################################################################

# [pr_diff] (0.30): No duplicate keyword arguments in any function call in the file.
# The core bug: duplicate trust_remote_code=True is a SyntaxError.
# On the buggy code, ast.parse itself fails (caught by gate), so this only
# runs on code that parses. We verify no call has duplicate kwargs AND that
# the from_hf_pretrained call still exists (not just deleted).
RESULT=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)

# Check ALL calls for duplicate kwargs
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        kwarg_names = [kw.arg for kw in node.keywords if kw.arg is not None]
        seen = set()
        for k in kwarg_names:
            if k in seen:
                print(f'DUPE:{k}')
                sys.exit(1)
            seen.add(k)

# Verify from_hf_pretrained call still exists (not deleted to dodge the check)
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if hasattr(node.func, 'attr') and node.func.attr == 'from_hf_pretrained':
            found = True
            break
if not found:
    print('CALL_MISSING')
    sys.exit(1)

print('OK')
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.30 1 "pr_diff" "No duplicate kwargs and from_hf_pretrained call exists" "BEHAVIORAL"
else
    add_score 0.30 0 "pr_diff" "Duplicate kwargs or missing call: $RESULT" "BEHAVIORAL"
fi

# [pr_diff] (0.20): from_hf_pretrained passes trust_remote_code exactly once
TRUST_RESULT=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if hasattr(node.func, 'attr') and node.func.attr == 'from_hf_pretrained':
            count = sum(1 for kw in node.keywords if kw.arg == 'trust_remote_code')
            if count == 1:
                print('OK')
                sys.exit(0)
            else:
                print(f'COUNT:{count}')
                sys.exit(1)
print('CALL_MISSING')
sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.20 1 "pr_diff" "trust_remote_code passed exactly once" "BEHAVIORAL"
else
    add_score 0.20 0 "pr_diff" "trust_remote_code issue: $TRUST_RESULT" "BEHAVIORAL"
fi

# [pr_diff] (0.15): from_hf_pretrained passes dtype argument
DTYPE_RESULT=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if hasattr(node.func, 'attr') and node.func.attr == 'from_hf_pretrained':
            has_dtype = any(kw.arg == 'dtype' for kw in node.keywords)
            if has_dtype:
                print('OK')
                sys.exit(0)
            else:
                print('MISSING_DTYPE')
                sys.exit(1)
print('CALL_MISSING')
sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.15 1 "pr_diff" "dtype argument preserved in from_hf_pretrained" "BEHAVIORAL"
else
    add_score 0.15 0 "pr_diff" "dtype issue: $DTYPE_RESULT" "BEHAVIORAL"
fi

########################################################################
# REGRESSION: Pass-to-pass (0.15)
########################################################################

# [pr_diff] (0.10): mbridge from_pretrained call unchanged — still has trust_remote_code
MBRIDGE_OK=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if hasattr(node.func, 'attr') and node.func.attr == 'from_pretrained':
            has_trust = any(kw.arg == 'trust_remote_code' for kw in node.keywords)
            if has_trust:
                print('OK')
                sys.exit(0)
print('MISSING')
sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.10 1 "pr_diff" "mbridge from_pretrained still has trust_remote_code" "REGRESSION"
else
    add_score 0.10 0 "pr_diff" "mbridge from_pretrained regression: $MBRIDGE_OK" "REGRESSION"
fi

# [pr_diff] (0.05): _build_hf_mcore_bridge method exists with non-trivial body (>= 2 stmts)
METHOD_OK=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == '_build_hf_mcore_bridge':
            body_len = len(node.body)
            if body_len < 2:
                print(f'STUBBED:{body_len}')
                sys.exit(1)
            print('OK')
            sys.exit(0)
print('MISSING')
sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.05 1 "pr_diff" "_build_hf_mcore_bridge exists with meaningful body" "REGRESSION"
else
    add_score 0.05 0 "pr_diff" "_build_hf_mcore_bridge issue: $METHOD_OK" "REGRESSION"
fi

########################################################################
# CONFIG-DERIVED: Agent config checks (0.10)
########################################################################

# [agent_config] (0.05): "No wildcard imports" — CLAUDE.md:51 @ 722e235
WILDCARD_OK=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names:
        if any(alias.name == '*' for alias in node.names):
            print('WILDCARD_FOUND')
            sys.exit(1)
print('OK')
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.05 1 "agent_config" "No wildcard imports — CLAUDE.md:51" "CONFIG"
else
    add_score 0.05 0 "agent_config" "Wildcard imports found — CLAUDE.md:51" "CONFIG"
fi

# [agent_config] (0.05): "No hardcoded secrets, paths, or endpoints" — AGENTS.md:24 @ 722e235
SECRETS_OK=$(python3 -c "
import ast, sys, re
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and re.search(r'(password|secret|api_key)', target.id, re.I):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    print(f'HARDCODED:{target.id}')
                    sys.exit(1)
print('OK')
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.05 1 "agent_config" "No hardcoded secrets — AGENTS.md:24" "CONFIG"
else
    add_score 0.05 0 "agent_config" "Hardcoded secrets found — AGENTS.md:24" "CONFIG"
fi

########################################################################
# ANTI-STUB (0.10)
########################################################################

# [pr_diff] (0.05): megatron-bridge code path not deleted
BRANCH_OK=$(python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.Compare):
        for comp in node.comparators:
            if isinstance(comp, ast.Constant) and comp.value == 'megatron-bridge':
                print('OK')
                sys.exit(0)
print('MISSING')
sys.exit(1)
" 2>&1)
if [ $? -eq 0 ]; then
    add_score 0.05 1 "pr_diff" "megatron-bridge code path still exists" "REGRESSION"
else
    add_score 0.05 0 "pr_diff" "megatron-bridge code path removed: $BRANCH_OK" "REGRESSION"
fi

# [pr_diff] (0.05): File not gutted (>300 lines)
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 300 ]; then
    add_score 0.05 1 "pr_diff" "File not gutted ($LINE_COUNT lines)" "REGRESSION"
else
    add_score 0.05 0 "pr_diff" "File suspiciously small ($LINE_COUNT lines)" "REGRESSION"
fi

########################################################################
# RESULTS
########################################################################

echo ""
echo "=== SCORE: $SCORE / $TOTAL ==="

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
data = {
    'reward': $SCORE,
    'behavioral': $BEHAVIORAL,
    'regression': $REGRESSION,
    'config': $CONFIG,
    'style_rubric': 0.0
}
print(json.dumps(data))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
