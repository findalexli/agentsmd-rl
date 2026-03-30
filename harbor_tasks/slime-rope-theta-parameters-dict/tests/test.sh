#!/usr/bin/env bash
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/arguments.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.15
WEIGHTS[antistub]=0.15
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural antistub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS"

# ---------- PRIMARY 1 (40%): rope_parameters dict is checked ----------
python3 << 'PYEOF'
import sys
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f: src = f.read()
if "rope_parameters" not in src:
    print("BEHAVIORAL FAIL: rope_parameters not checked"); sys.exit(1)
# Should look into dict for rope_theta
if "rope_theta" not in src:
    print("BEHAVIORAL FAIL: rope_theta not referenced"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): rope_theta removed from generic validation loop ----------
python3 << 'PYEOF'
import sys, re
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f: src = f.read()
# The old pattern had ("rope_theta", "rotary_base", equal) in the tuple list
loop_match = re.search(r'for\s+hf_config_name.*?in\s*\[([^]]+)\]', src, re.DOTALL)
if loop_match:
    loop_content = loop_match.group(1)
    if '"rope_theta"' in loop_content or "'rope_theta'" in loop_content:
        print("BEHAVIORAL2 FAIL: rope_theta still in generic validation loop")
        sys.exit(1)
print("BEHAVIORAL2 PASS: rope_theta handled separately")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f: src = f.read()
tree = ast.parse(src)
found = any(isinstance(n, ast.FunctionDef) and n.name == "hf_validate_args" for n in ast.walk(tree))
if not found: print("STRUCTURAL FAIL: hf_validate_args not found"); sys.exit(1)
if "rotary_base" not in src:
    print("STRUCTURAL FAIL: rotary_base validation missing"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (15%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/slime/slime/backends/megatron_utils/arguments.py") as f: src = f.read()
ok = all(["def hf_validate_args" in src, len(src.splitlines()) > 30])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 600624625219566f742540189dd18399d310d923
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 600624625219566f742540189dd18399d310d923
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
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
