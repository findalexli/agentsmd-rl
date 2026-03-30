#!/usr/bin/env bash
set +e

WANDB="/workspace/slime/slime/utils/wandb_utils.py"
LOGGING="/workspace/slime/slime/utils/logging_utils.py"
ROLLOUT="/workspace/slime/slime/ray/rollout.py"
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

for f in "$WANDB" "$LOGGING" "$ROLLOUT"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
done
echo "GATE PASS"

# ---------- PRIMARY 1 (35%): reinit function exists in wandb_utils ----------
python3 << 'PYEOF'
import sys
with open("/workspace/slime/slime/utils/wandb_utils.py") as f: src = f.read()
if "reinit_wandb_primary_with_open_metrics" not in src:
    print("BEHAVIORAL FAIL: reinit function not found"); sys.exit(1)
if "engine_metrics" not in src:
    print("BEHAVIORAL FAIL: metrics endpoint not configured"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): router_addr removed from init_wandb_secondary ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/slime/slime/utils/wandb_utils.py") as f: src = f.read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "init_wandb_secondary":
        args = [a.arg for a in node.args.args]
        if "router_addr" in args:
            print("BEHAVIORAL2 FAIL: router_addr still in init_wandb_secondary"); sys.exit(1)
        break
print("BEHAVIORAL2 PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): public get_metrics_router_addr ----------
python3 << 'PYEOF'
import sys
with open("/workspace/slime/slime/ray/rollout.py") as f: src = f.read()
if "def get_metrics_router_addr" not in src:
    print("STRUCTURAL FAIL: public get_metrics_router_addr not found"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (20%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/slime/slime/utils/wandb_utils.py") as f: src = f.read()
ok = all(["def init_wandb_primary" in src, "wandb" in src, len(src.splitlines()) > 50])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit d4c4d3fb24d45c3cd12f47b64b30fc3301286778
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$WANDB" "$LOGGING" "$ROLLOUT" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit d4c4d3fb24d45c3cd12f47b64b30fc3301286778
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$WANDB" "$LOGGING" "$ROLLOUT" 2>/dev/null
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
