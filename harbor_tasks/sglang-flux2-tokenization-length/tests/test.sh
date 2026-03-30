#!/usr/bin/env bash
set +e

TARGET="/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.40
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.05
WEIGHTS[config]=0.10

for key in behavioral behavioral2 structural antistub config; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (40%): Flux2PipelineConfig overrides text_encoder_extra_args with 512 ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py") as f:
    src = f.read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Flux2PipelineConfig":
        cls_src = "\n".join(src.splitlines()[node.lineno - 1 : node.end_lineno])
        if "512" in cls_src and "text_encoder_extra_args" in cls_src:
            print("BEHAVIORAL PASS: Flux2PipelineConfig overrides with 512")
            sys.exit(0)
        break
print("BEHAVIORAL FAIL: Flux2PipelineConfig does not override text_encoder_extra_args with 512")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): Klein tokenize_prompt enforces 512 ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py") as f:
    src = f.read()
# Find Flux2KleinPipelineConfig.tokenize_prompt
if "max_length = 512" in src or "max_length=512" in src:
    print("BEHAVIORAL2 PASS: Klein enforces max_length=512")
else:
    print("BEHAVIORAL2 FAIL: max_length=512 not enforced in Klein"); import sys; sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import sys
with open("/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py") as f:
    src = f.read()
if "Flux2PipelineConfig" not in src: print("STRUCTURAL FAIL"); import sys; sys.exit(1)
if "Flux2KleinPipelineConfig" not in src: print("STRUCTURAL FAIL"); import sys; sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/sglang/python/sglang/multimodal_gen/configs/pipeline_configs/flux.py") as f:
    src = f.read()
ok = all(["class Flux2PipelineConfig" in src, "tokenize_prompt" in src, len(src.splitlines()) > 100])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# Config-derived test (0.10): "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ edd4d540237be4267c3a260d6a2f23a035e203af
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
if [ -z "$NEW_TEST_FILES" ]; then
    echo "CONFIG config: PASS (no new test files added)"
    RESULTS[config]=1
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "CONFIG config: FAIL — $tf missing main guard"
            ALL_OK=0
        fi
    done
    [ "$ALL_OK" -eq 1 ] && RESULTS[config]=1
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
