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

# Weights
W_SERVER_CONFIGURE=0.20
W_LOCAL_ERROR_KEY=0.25
W_SLURM_ERROR_KEY=0.20
W_BEHAVIORAL_ROUNDTRIP=0.15
W_ANTISTUB=0.10
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- rpc_server /configure uses "error" not "detail" --
echo ""
echo "TEST 1: behavioral -- rpc_server /configure uses 'error' key (weight=$W_SERVER_CONFIGURE)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/infra/rpc/rpc_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the configure function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "configure":
        func_node = node
        break

if func_node is None:
    print("FAIL: configure function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# Check that "detail" is NOT used as a dict key in error responses
detail_count = func_src.count('"detail"')
error_count = func_src.count('"error"')

if detail_count > 0:
    print(f"FAIL: /configure still uses 'detail' key ({detail_count} times)")
    sys.exit(1)
elif error_count >= 3:
    print(f"PASS: /configure uses 'error' key ({error_count} times, no 'detail')")
    sys.exit(0)
else:
    print(f"FAIL: /configure has only {error_count} 'error' keys (expected >=3)")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_SERVER_CONFIGURE)")
fi

# -- TEST 2 (PRIMARY): behavioral -- local.py reads "error" not "detail" --
echo ""
echo "TEST 2: behavioral -- local.py reads 'error' key (weight=$W_LOCAL_ERROR_KEY)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/infra/scheduler/local.py") as f:
    source = f.read()

# Count .get("detail" and .get("error" in error handling contexts
detail_gets = source.count('.get("detail"')
error_gets = source.count('.get("error"')

if detail_gets > 0:
    print(f"FAIL: local.py still uses .get('detail') ({detail_gets} times)")
    sys.exit(1)
elif error_gets >= 8:
    print(f"PASS: local.py uses .get('error') ({error_gets} times, no .get('detail'))")
    sys.exit(0)
elif error_gets > 0:
    # Partial fix
    print(f"PASS: local.py uses .get('error') ({error_gets} times)")
    sys.exit(0)
else:
    print("FAIL: no .get('error') found in local.py")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_LOCAL_ERROR_KEY)")
fi

# -- TEST 3 (PRIMARY): behavioral -- slurm.py reads "error" not "detail" --
echo ""
echo "TEST 3: behavioral -- slurm.py reads 'error' key (weight=$W_SLURM_ERROR_KEY)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/infra/scheduler/slurm.py") as f:
    source = f.read()

detail_gets = source.count('.get("detail"')
error_gets = source.count('.get("error"')

if detail_gets > 0:
    print(f"FAIL: slurm.py still uses .get('detail') ({detail_gets} times)")
    sys.exit(1)
elif error_gets >= 8:
    print(f"PASS: slurm.py uses .get('error') ({error_gets} times, no .get('detail'))")
    sys.exit(0)
elif error_gets > 0:
    print(f"PASS: slurm.py uses .get('error') ({error_gets} times)")
    sys.exit(0)
else:
    print("FAIL: no .get('error') found in slurm.py")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_SLURM_ERROR_KEY)")
fi

# -- TEST 4 (PRIMARY): behavioral -- simulated round-trip: server error -> client extract --
echo ""
echo "TEST 4: behavioral -- round-trip: server error dict matches client extraction (weight=$W_BEHAVIORAL_ROUNDTRIP)"
T4=$(python3 << 'PYEOF'
import ast, sys, re

# Extract what key the server uses for errors in /configure
with open("/workspace/AReaL/areal/infra/rpc/rpc_server.py") as f:
    server_src = f.read()

# Extract what key local.py uses to read errors
with open("/workspace/AReaL/areal/infra/scheduler/local.py") as f:
    local_src = f.read()

# Find the key used in jsonify calls in configure()
tree = ast.parse(server_src)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "configure":
        func_node = node
        break

if func_node is None:
    print("FAIL: configure function not found")
    sys.exit(1)

func_lines = server_src.splitlines(keepends=True)
func_src = "".join(func_lines[func_node.lineno - 1:func_node.end_lineno])

# Extract all dict keys from jsonify calls
server_keys = set(re.findall(r'jsonify\(\{["\'](\w+)["\']:', func_src))

# Extract all .get("key") calls from local.py error handling
client_keys = set(re.findall(r'\.get\(["\'](\w+)["\'],\s*["\']Unknown error["\']\)', local_src))

if not server_keys:
    print("FAIL: could not extract server error keys from configure()")
    sys.exit(1)

if not client_keys:
    print("FAIL: could not extract client error keys from local.py")
    sys.exit(1)

# They should match
if server_keys == client_keys:
    print(f"PASS: server and client use matching key(s): {server_keys}")
    sys.exit(0)
elif server_keys & client_keys:
    # At least some overlap
    overlap = server_keys & client_keys
    print(f"PASS: server and client share key(s): {overlap}")
    sys.exit(0)
else:
    print(f"FAIL: mismatch -- server uses {server_keys}, client uses {client_keys}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_ROUNDTRIP)")
fi

# -- TEST 5: anti-stub check --
echo ""
echo "TEST 5: anti-stub -- files retain original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys

files = {
    "/workspace/AReaL/areal/infra/rpc/rpc_server.py": ["configure", "jsonify", "request", "get_json", 400, 500],
    "/workspace/AReaL/areal/infra/scheduler/local.py": ["_configure_worker", "create_engine", "WorkerConfigurationError", "EngineCallError"],
    "/workspace/AReaL/areal/infra/scheduler/slurm.py": ["_configure_worker", "create_engine", "WorkerConfigurationError", "EngineCallError"],
}

for path, required in files.items():
    with open(path) as f:
        source = f.read()
    missing = [str(r) for r in required if str(r) not in source]
    if missing:
        print(f"FAIL: {path} is missing: {missing}")
        sys.exit(1)
    if len(source.splitlines()) < 200:
        print(f"FAIL: {path} too short -- likely stubbed")
        sys.exit(1)

print("PASS: all files retain original logic")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit a3e36d4af66ac6fa88e723675060cde591ca133e
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" /workspace/AReaL/areal/infra/rpc/rpc_server.py /workspace/AReaL/areal/infra/scheduler/local.py /workspace/AReaL/areal/infra/scheduler/slurm.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit a3e36d4af66ac6fa88e723675060cde591ca133e
echo ""
echo "TEST 7: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" /workspace/AReaL/areal/infra/rpc/rpc_server.py /workspace/AReaL/areal/infra/scheduler/local.py /workspace/AReaL/areal/infra/scheduler/slurm.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    echo "PASS"
else
    echo "FAIL: bare print() found"
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
