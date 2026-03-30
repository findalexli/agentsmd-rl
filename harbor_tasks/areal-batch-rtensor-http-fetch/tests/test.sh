#!/usr/bin/env bash
set +e

SERVER="/workspace/AReaL/areal/infra/rpc/rpc_server.py"
RTENSOR="/workspace/AReaL/areal/infra/rpc/rtensor.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.30
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.20
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural antistub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$SERVER').read()); ast.parse(open('$RTENSOR').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (35%): /data/batch endpoint exists ----------
python3 << 'PYEOF'
import sys
with open("/workspace/AReaL/areal/infra/rpc/rpc_server.py") as f: src = f.read()
if "/data/batch" not in src:
    print("BEHAVIORAL FAIL: /data/batch endpoint not found"); sys.exit(1)
if "shard_ids" not in src:
    print("BEHAVIORAL FAIL: shard_ids handling not found"); sys.exit(1)
if "missing" not in src.lower():
    print("BEHAVIORAL FAIL: missing shard reporting not found"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): HttpRTensorBackend batches by node ----------
python3 << 'PYEOF'
import sys
with open("/workspace/AReaL/areal/infra/rpc/rtensor.py") as f: src = f.read()
if "max_shards_per_request" not in src:
    print("BEHAVIORAL2 FAIL: max_shards_per_request not found"); sys.exit(1)
if "node_addr" not in src or "shards_by_node" not in src and "grouped" not in src:
    print("BEHAVIORAL2 FAIL: node grouping not found"); sys.exit(1)
if "/data/batch" not in src:
    print("BEHAVIORAL2 FAIL: batch endpoint not used in client"); sys.exit(1)
print("BEHAVIORAL2 PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/AReaL/areal/infra/rpc/rtensor.py") as f: src = f.read()
tree = ast.parse(src)
found_init = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                found_init = True
if not found_init:
    print("STRUCTURAL FAIL: HttpRTensorBackend.__init__ not found"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (20%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/AReaL/areal/infra/rpc/rtensor.py") as f: src = f.read()
ok = all(["class HttpRTensorBackend" in src, "def fetch" in src, len(src.splitlines()) > 50])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: AGENTS.md line 13 @ commit 3142b88a5e93e991df727c81892d6cb8bd65d06e
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$SERVER" "$RTENSOR" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: AGENTS.md line 80 @ commit 3142b88a5e93e991df727c81892d6cb8bd65d06e
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$SERVER" "$RTENSOR" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral]},'behavioral2':${WEIGHTS[behavioral2]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]},'config_no_wildcard':${WEIGHTS[config_no_wildcard]},'config_no_bare_print':${WEIGHTS[config_no_bare_print]}}
r={'behavioral':${RESULTS[behavioral]},'behavioral2':${RESULTS[behavioral2]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]},'config_no_wildcard':${RESULTS[config_no_wildcard]},'config_no_bare_print':${RESULTS[config_no_bare_print]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
