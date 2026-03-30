#!/usr/bin/env bash
set +e

ACTOR="/workspace/AReaL/areal/trainer/ppo/actor.py"
CRITIC="/workspace/AReaL/areal/trainer/ppo/critic.py"
STATS="/workspace/AReaL/areal/trainer/ppo/stats.py"
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

# ---------- GATE ----------
for f in "$ACTOR" "$CRITIC"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "0.0" > "$REWARD_FILE"; exit 0
    fi
done
echo "GATE PASS"

# ---------- PRIMARY 1 (35%): stats.py exists with infer_token_denominator ----------
python3 << 'PYEOF'
import sys, os
STATS = "/workspace/AReaL/areal/trainer/ppo/stats.py"
if not os.path.isfile(STATS):
    print("BEHAVIORAL FAIL: stats.py not found"); sys.exit(1)
with open(STATS) as f: source = f.read()
if "def infer_token_denominator" not in source:
    print("BEHAVIORAL FAIL: infer_token_denominator not found"); sys.exit(1)
if "attention_mask" not in source:
    print("BEHAVIORAL FAIL: no attention_mask handling"); sys.exit(1)
if "cu_seqlens" not in source:
    print("BEHAVIORAL FAIL: no cu_seqlens handling"); sys.exit(1)
print("BEHAVIORAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- PRIMARY 2 (25%): actor+critic use infer_token_denominator ----------
python3 << 'PYEOF'
import sys
for fp, name in [("/workspace/AReaL/areal/trainer/ppo/actor.py","actor"),("/workspace/AReaL/areal/trainer/ppo/critic.py","critic")]:
    with open(fp) as f: src = f.read()
    if "infer_token_denominator" not in src:
        print(f"BEHAVIORAL2 FAIL: {name} missing infer_token_denominator"); sys.exit(1)
    if "torch.ones_like(loss_mask, dtype=torch.bool)" in src:
        print(f"BEHAVIORAL2 FAIL: {name} still uses old pattern"); sys.exit(1)
print("BEHAVIORAL2 PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- SUPPLEMENTARY (20%): structural ----------
python3 << 'PYEOF'
import ast, sys, os
STATS = "/workspace/AReaL/areal/trainer/ppo/stats.py"
if not os.path.isfile(STATS): print("STRUCTURAL FAIL"); sys.exit(1)
with open(STATS) as f: src = f.read()
tree = ast.parse(src)
found = any(isinstance(n, ast.FunctionDef) and n.name == "infer_token_denominator" for n in ast.walk(tree))
if not found: print("STRUCTURAL FAIL"); sys.exit(1)
print("STRUCTURAL PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[structural]=1 && echo "TEST structural: PASS" || echo "TEST structural: FAIL"

# ---------- Anti-stub (20%) ----------
python3 << 'PYEOF'
import sys
with open("/workspace/AReaL/areal/trainer/ppo/actor.py") as f: src = f.read()
ok = all(["def ppo_update" in src, "stats_tracker" in src, len(src.splitlines()) > 100])
if not ok: print("ANTI-STUB FAIL"); sys.exit(1)
print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: AGENTS.md line 13 @ commit d1cdac3442585565f902f1e69b9d7399c50b9b34
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$ACTOR" "$CRITIC" "$STATS" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: AGENTS.md line 80 @ commit d1cdac3442585565f902f1e69b9d7399c50b9b34
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$ACTOR" "$CRITIC" "$STATS" 2>/dev/null
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
