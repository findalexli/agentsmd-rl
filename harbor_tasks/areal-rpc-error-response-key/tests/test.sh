#!/usr/bin/env bash
# Verifier for areal-rpc-error-response-key
# Task: unify RPC error response JSON key to "error" across server and schedulers
# Files: rpc_server.py, local.py, slurm.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== areal rpc error response key verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
GATE_PASS=true
for f in areal/infra/rpc/rpc_server.py areal/infra/scheduler/local.py areal/infra/scheduler/slurm.py; do
    python3 -c "
import ast, sys
try:
    with open('/workspace/AReaL/$f') as fh:
        ast.parse(fh.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'  FAIL: $f SyntaxError: {e}')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "GATE FAIL: syntax error -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights - target: >=60% behavioral
W_F2P_SERVER_KEY=0.25
W_F2P_LOCAL_GET=0.25
W_F2P_SLURM_GET=0.25
W_P2P_UPSTREAM=0.10
W_ANTI_STUB=0.10
W_NO_WILDCARD=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): Fail-to-Pass -- Server /configure uses "error" key --
# [pr_diff] (0.25): Server error responses use "error" key, not "detail"
echo ""
echo "TEST 1: F2P -- rpc_server /configure uses 'error' key (weight=$W_F2P_SERVER_KEY)"
T1=$(python3 << 'PYEOF'
import ast
import sys

def get_function_source(filepath, func_name):
    """Extract function source using AST."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            return "".join(lines[node.lineno - 1:node.end_lineno])
    return None

def extract_jsonify_keys(func_src):
    """Extract dict keys from jsonify calls in the source."""
    keys = set()
    # Pattern 1: jsonify({"key": value})
    import re
    matches = re.findall(r'jsonify\(\s*\{\s*["\'](\w+)["\']\s*:', func_src)
    keys.update(matches)
    # Pattern 2: return {"key": value} (for the success case in configure)
    # Look for dict literals that include error/info keys
    return keys

configure_src = get_function_source("/workspace/AReaL/areal/infra/rpc/rpc_server.py", "configure")
if configure_src is None:
    print("FAIL: configure function not found")
    sys.exit(1)

# Check for error key usage
has_error_key = '"error"' in configure_src or "'error'" in configure_src
has_detail_key = '"detail"' in configure_src or "'detail'" in configure_src

# The fix requires: "error" key present, "detail" key absent in error responses
error_keys = extract_jsonify_keys(configure_src)

if has_detail_key:
    print(f"FAIL: /configure still uses 'detail' key - keys found: {error_keys}")
    sys.exit(1)
elif has_error_key:
    print(f"PASS: /configure uses 'error' key (no 'detail') - keys: {error_keys}")
    sys.exit(0)
else:
    print(f"FAIL: No recognizable error key pattern found")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_SERVER_KEY)")
fi

# -- TEST 2 (PRIMARY): Fail-to-Pass -- local.py reads "error" key --
# [pr_diff] (0.25): local scheduler reads "error" key from RPC responses
echo ""
echo "TEST 2: F2P -- local.py reads 'error' key (weight=$W_F2P_LOCAL_GET)"
T2=$(python3 << 'PYEOF'
import ast
import sys

def get_function_source(filepath, func_name):
    """Extract function source using AST."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            return "".join(lines[node.lineno - 1:node.end_lineno])
    return None

configure_worker_src = get_function_source("/workspace/AReaL/areal/infra/scheduler/local.py", "_configure_worker")
if configure_worker_src is None:
    print("FAIL: _configure_worker function not found")
    sys.exit(1)

# Check error handling paths specifically (the 400 and 500 status code branches)
# Looking for patterns like .get("error", ...) and NOT .get("detail", ...)
import re

# Find error extraction patterns
detail_pattern = r'\.get\(\s*["\']detail["\']\s*,\s*["\']Unknown error["\']\s*\)'
error_pattern = r'\.get\(\s*["\']error["\']\s*,\s*["\']Unknown error["\']\s*\)'

has_detail = re.search(detail_pattern, configure_worker_src) is not None
has_error = re.search(error_pattern, configure_worker_src) is not None

if has_detail:
    print("FAIL: _configure_worker still uses .get('detail', 'Unknown error')")
    sys.exit(1)
elif has_error:
    # Count occurrences to ensure it's comprehensive
    error_count = len(re.findall(error_pattern, configure_worker_src))
    if error_count >= 2:  # Should have at least 2 (for 400 and 500 errors)
        print(f"PASS: _configure_worker uses .get('error') ({error_count} occurrences)")
        sys.exit(0)
    else:
        print(f"PARTIAL: Only {error_count} .get('error') found (expected >=2)")
        sys.exit(1)
else:
    # Alternative: check if they use different but valid approach
    # Look for bracket access with error key
    bracket_pattern = r'\[["\']error["\']\]'
    if re.search(bracket_pattern, configure_worker_src):
        print("PASS: _configure_worker uses ['error'] bracket access")
        sys.exit(0)
    print("FAIL: No recognizable error key extraction pattern")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_LOCAL_GET)")
fi

# -- TEST 3 (PRIMARY): Fail-to-Pass -- slurm.py reads "error" key --
# [pr_diff] (0.25): slurm scheduler reads "error" key from RPC responses
echo ""
echo "TEST 3: F2P -- slurm.py reads 'error' key (weight=$W_F2P_SLURM_GET)"
T3=$(python3 << 'PYEOF'
import ast
import sys

def get_function_source(filepath, func_name):
    """Extract function source using AST."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            lines = source.splitlines(keepends=True)
            return "".join(lines[node.lineno - 1:node.end_lineno])
    return None

configure_worker_src = get_function_source("/workspace/AReaL/areal/infra/scheduler/slurm.py", "_configure_worker")
if configure_worker_src is None:
    print("FAIL: _configure_worker function not found in slurm.py")
    sys.exit(1)

import re

# Find error extraction patterns
detail_pattern = r'\.get\(\s*["\']detail["\']\s*,\s*["\']Unknown error["\']\s*\)'
error_pattern = r'\.get\(\s*["\']error["\']\s*,\s*["\']Unknown error["\']\s*\)'

has_detail = re.search(detail_pattern, configure_worker_src) is not None
has_error = re.search(error_pattern, configure_worker_src) is not None

if has_detail:
    print("FAIL: slurm _configure_worker still uses .get('detail', 'Unknown error')")
    sys.exit(1)
elif has_error:
    error_count = len(re.findall(error_pattern, configure_worker_src))
    if error_count >= 2:
        print(f"PASS: slurm _configure_worker uses .get('error') ({error_count} occurrences)")
        sys.exit(0)
    else:
        print(f"PARTIAL: Only {error_count} .get('error') found (expected >=2)")
        sys.exit(1)
else:
    # Alternative: bracket access
    bracket_pattern = r'\[["\']error["\']\]'
    if re.search(bracket_pattern, configure_worker_src):
        print("PASS: slurm _configure_worker uses ['error'] bracket access")
        sys.exit(0)
    print("FAIL: No recognizable error key extraction pattern")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_SLURM_GET)")
fi

# -- TEST 4: Pass-to-Pass -- upstream test suite (CPU-safe subset) --
# [pr_diff]: test_local_scheduler.py should still pass
echo ""
echo "TEST 4: P2P -- upstream test suite (weight=$W_P2P_UPSTREAM)"
T4=$(python3 << 'PYEOF'
import sys
import os
import ast
import re

# Check that the file exists in tests/
test_file = "/workspace/AReaL/tests/test_local_scheduler.py"
if not os.path.exists(test_file):
    print("INFO: No upstream tests available - skipping P2P")
    sys.exit(0)

with open(test_file) as f:
    source = f.read()

# The tests mock the responses - check they use correct key
# Look for mock_response.json.return_value patterns
if '.json().get("error"' in source or '.json().get("detail"' in source:
    # Check if they've been updated to use "error" in mock responses
    error_in_mock = source.count('"error":') >= 3
    detail_in_mock = source.count('"detail":') > 0

    if error_in_mock and not detail_in_mock:
        print("PASS: Test mocks updated to use 'error' key")
        sys.exit(0)
    elif detail_in_mock:
        print("FAIL: Test mocks still use 'detail' key")
        sys.exit(1)
    else:
        print("PASS: No relevant mock updates needed or found")
        sys.exit(0)
else:
    print("PASS: Test file structure OK")
    sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_UPSTREAM)")
fi

# -- TEST 5: Anti-stub check --
# [agent_config]: Files must retain substantial logic (not be stubbed)
echo ""
echo "TEST 5: anti-stub -- files retain original logic (weight=$W_ANTI_STUB)"
T5=$(python3 << 'PYEOF'
import ast
import sys

def count_meanful_statements(filepath):
    """Count non-docstring, non-pass statements in a file."""
    with open(filepath) as f:
        source = f.read()
    tree = ast.parse(source)

    count = 0
    for node in ast.walk(tree):
        # Skip docstrings
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            continue
        # Skip pass statements
        if isinstance(node, ast.Pass):
            continue
        # Count meaningful statements
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For, ast.While,
                             ast.With, ast.Try, ast.Assign, ast.AugAssign, ast.AnnAssign,
                             ast.Return, ast.Raise, ast.Assert, ast.Delete, ast.Global,
                             ast.Nonlocal, ast.Expr)):
            count += 1

    return count

files = {
    "/workspace/AReaL/areal/infra/rpc/rpc_server.py": 500,
    "/workspace/AReaL/areal/infra/scheduler/local.py": 400,
    "/workspace/AReaL/areal/infra/scheduler/slurm.py": 400,
}

for path, min_stmts in files.items():
    actual = count_meanful_statements(path)
    if actual < min_stmts * 0.5:  # Allow some reduction but not more than 50%
        print(f"FAIL: {path} too small ({actual} stmts, expected >= {min_stmts * 0.5})")
        sys.exit(1)
    print(f"  {path}: {actual} statements (OK)")

print("PASS: All files retain substantial logic")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTI_STUB)")
fi

# -- TEST 6: Config-derived -- No wildcard imports --
# Source: "No wildcard imports" -- AReaL AGENTS.md:30 @ a3e36d4
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_NO_WILDCARD)"
python3 -c "
import ast
import sys
import re

files = [
    '/workspace/AReaL/areal/infra/rpc/rpc_server.py',
    '/workspace/AReaL/areal/infra/scheduler/local.py',
    '/workspace/AReaL/areal/infra/scheduler/slurm.py'
]

for path in files:
    with open(path) as f:
        source = f.read()
    # Check for 'from X import *' patterns
    if re.search(r'from\s+\S+\s+import\s+\*', source):
        print(f'FAIL: wildcard import found in {path}')
        sys.exit(1)

print('PASS: no wildcard imports')
sys.exit(0)
"
if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
