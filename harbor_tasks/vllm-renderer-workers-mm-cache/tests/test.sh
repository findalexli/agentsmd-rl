#!/usr/bin/env bash
set +e

TARGET="/workspace/vllm/vllm/config/model.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.05
WEIGHTS[config]=0.10

for key in behavioral regression structural antistub config; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (40%): ValueError raised for renderer_num_workers > 1 + cache ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/config/model.py") as f: src = f.read()
if "renderer_num_workers" not in src:
    print("BEHAVIORAL FAIL: renderer_num_workers check not found"); sys.exit(1)
if "mm_processor_cache" not in src and "multimodal" not in src.lower():
    print("BEHAVIORAL FAIL: mm cache check not found"); sys.exit(1)
if "ValueError" not in src and "raise" not in src:
    print("BEHAVIORAL FAIL: no ValueError raised"); sys.exit(1)
# Check the actual validation logic
import re
check = re.search(r'renderer_num_workers\s*>\s*1.*mm_processor_cache', src, re.DOTALL)
check2 = re.search(r'mm_processor_cache.*renderer_num_workers\s*>\s*1', src, re.DOTALL)
if not check and not check2:
    print("BEHAVIORAL FAIL: combined check not found"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): regression - single worker + cache still works ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/config/model.py") as f: src = f.read()
# The validation should only fire when BOTH conditions are true
import re
# Check there's a condition with > 1 (not >= 1)
if re.search(r'renderer_num_workers\s*>=\s*1.*raise', src):
    print("REGRESSION FAIL: would block single-worker config too"); sys.exit(1)
print("REGRESSION PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/config/model.py") as f: src = f.read()
if "class ModelConfig" not in src:
    print("STRUCTURAL FAIL: ModelConfig not found"); sys.exit(1)
if "__post_init__" not in src:
    print("STRUCTURAL FAIL: __post_init__ not found"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/vllm/vllm/config/model.py") as f: src = f.read()
ok = all(["class ModelConfig" in src, len(src.splitlines()) > 200])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# Config-derived test (0.10): "Never use bare pip install"
# Source: AGENTS.md line 27 @ 2bf5b70ae86261431b4b92276828b40b9c0903b6
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
w={'behavioral':${WEIGHTS[behavioral]},'regression':${WEIGHTS[regression]},'structural':${WEIGHTS[structural]},'antistub':${WEIGHTS[antistub]},'config':${WEIGHTS[config]}}
r={'behavioral':${RESULTS[behavioral]},'regression':${RESULTS[regression]},'structural':${RESULTS[structural]},'antistub':${RESULTS[antistub]},'config':${RESULTS[config]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
