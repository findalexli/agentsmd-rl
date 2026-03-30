#!/usr/bin/env bash
set +e

TARGET="/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"
ENVS="/workspace/vllm/vllm/envs.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config]=0.10

for key in behavioral behavioral2 structural antistub config; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$TARGET').read()); ast.parse(open('$ENVS').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (35%): _resolve_fi_ar_backend exists and checks node count ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py") as f:
    src = f.read()
if "_resolve_fi_ar_backend" not in src:
    print("BEHAVIORAL FAIL: _resolve_fi_ar_backend function not found"); sys.exit(1)
if "get_node_count" not in src:
    print("BEHAVIORAL FAIL: get_node_count not used"); sys.exit(1)
if "mnnvl" not in src:
    print("BEHAVIORAL FAIL: mnnvl backend not referenced"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): default changed to "auto" in envs.py ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/envs.py") as f: src = f.read()
import re
match = re.search(r'VLLM_FLASHINFER_ALLREDUCE_BACKEND.*?=\s*["\'](\w+)["\']', src)
if match:
    default = match.group(1)
    if default != "auto":
        print(f"BEHAVIORAL2 FAIL: default is '{default}', expected 'auto'"); sys.exit(1)
else:
    # Check for the env_with_choices pattern
    match2 = re.search(r'VLLM_FLASHINFER_ALLREDUCE_BACKEND.*?env_with_choices.*?["\'](\w+)["\']', src, re.DOTALL)
    if match2 and match2.group(1) != "auto":
        print(f"BEHAVIORAL2 FAIL: default is '{match2.group(1)}', expected 'auto'"); sys.exit(1)
print("BEHAVIORAL2 PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): multi-node quant workspace returns None ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py") as f:
    src = f.read()
# Should handle multi-node in get_fi_ar_quant_workspace
if "get_fi_ar_quant_workspace" not in src:
    print("STRUCTURAL FAIL"); sys.exit(1)
# Check that multi-node returns None for quant
if "get_node_count() > 1" not in src:
    print("STRUCTURAL FAIL: no multi-node check"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (20%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py") as f:
    src = f.read()
ok = all(["def get_fi_ar_workspace" in src, len(src.splitlines()) > 50])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# Config-derived test (0.10): "Never use bare pip install"
# Source: AGENTS.md line 27 @ f26fcdfb9e50fef30381ed27fa956f7a43b0b1aa
cd /workspace/vllm 2>/dev/null
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || true)
BARE_PIP=0
for cf in $CHANGED_FILES; do
    if [ -f "/workspace/vllm/$cf" ]; then
        if grep -Pn '(?<!uv )pip install' "/workspace/vllm/$cf" 2>/dev/null | grep -v '^.*#' | grep -v 'uv pip' > /dev/null 2>&1; then
            echo "CONFIG config: FAIL — $cf contains bare 'pip install'"
            BARE_PIP=1
        fi
    fi
done
if [ "$BARE_PIP" -eq 0 ]; then
    echo "CONFIG config: PASS"
    RESULTS[config]=1
fi

SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral]},'behavioral2':${WEIGHTS[behavioral2]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]},'config':${WEIGHTS[config]}}
r={'behavioral':${RESULTS[behavioral]},'behavioral2':${RESULTS[behavioral2]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
