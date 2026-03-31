#!/usr/bin/env bash
set +e

WANDB="/workspace/slime/slime/utils/wandb_utils.py"
LOGGING="/workspace/slime/slime/utils/logging_utils.py"
ROLLOUT="/workspace/slime/slime/ray/rollout.py"
TRAIN="/workspace/slime/train.py"
TRAIN_ASYNC="/workspace/slime/train_async.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_router_removed]=0.25
WEIGHTS[behavioral_reinit_exists]=0.10
WEIGHTS[behavioral_reinit_logic]=0.20
WEIGHTS[behavioral_get_router]=0.15
WEIGHTS[behavioral_train_integration]=0.15
WEIGHTS[antistub]=0.10
WEIGHTS[config_no_wildcard]=0.025
WEIGHTS[config_no_bare_print]=0.025

for key in behavioral_router_removed behavioral_reinit_exists behavioral_reinit_logic behavioral_get_router behavioral_train_integration antistub config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

for f in "$WANDB" "$LOGGING" "$ROLLOUT"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
done
echo "GATE PASS"

# ---------- BEHAVIORAL 1 (25%): router_addr removed from init_wandb_secondary ----------
# [pr_diff] (0.25): router_addr parameter removed from init_wandb_secondary
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/slime/slime/utils/wandb_utils.py") as f:
    src = f.read()

tree = ast.parse(src)

# Find init_wandb_secondary function
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "init_wandb_secondary":
        # Get all argument names including kwonlyargs
        args = [a.arg for a in node.args.args]
        args += [a.arg for a in node.args.kwonlyargs]

        if "router_addr" in args:
            print("FAIL: router_addr still in init_wandb_secondary signature")
            sys.exit(1)

        # Check function body is non-trivial (>3 non-docstring statements)
        body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Constant)]
        if len(body) <= 3:
            print("FAIL: init_wandb_secondary body too small (likely stub)")
            sys.exit(1)

        print("PASS: router_addr removed, body non-trivial")
        sys.exit(0)

print("FAIL: init_wandb_secondary function not found")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_router_removed]=1

# ---------- BEHAVIORAL 2 (10%): reinit function exists and is callable ----------
# [pr_diff] (0.10): reinit_wandb_primary_with_open_metrics function added
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/slime/slime/utils/wandb_utils.py") as f:
    src = f.read()

if "def reinit_wandb_primary_with_open_metrics" not in src:
    print("FAIL: reinit_wandb_primary_with_open_metrics not found")
    sys.exit(1)

tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
        # Check body is non-trivial (>5 non-docstring statements for this complex function)
        body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Constant)]
        if len(body) <= 5:
            print("FAIL: reinit function body too small (likely stub)")
            sys.exit(1)
        print("PASS: reinit function exists with non-trivial body")
        sys.exit(0)

print("FAIL: reinit function not found via AST")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_reinit_exists]=1

# ---------- BEHAVIORAL 3 (20%): reinit function has correct logic ----------
# [pr_diff] (0.20): reinit calls wandb.finish(), wandb.init(), and configures metrics endpoints
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/slime/slime/utils/wandb_utils.py") as f:
    src = f.read()

tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "reinit_wandb_primary_with_open_metrics":
        src_upper = src.upper()
        node_src = ast.unparse(node).upper()

        # Check for key logic components
        checks = {
            "wandb.finish": "WANB.FINISH" in node_src,
            "wandb.init": "WANB.INIT" in node_src,
            "resume_allow": "RESUME" in node_src and "ALLOW" in node_src,
            "engine_metrics": "ENGINE_METRICS" in node_src or "SGl_ENGINE" in node_src,
            "args_check": "ARGS.USE_WANDB" in node_src or "_IS_OFFLINE_MODE" in node_src,
        }

        passed = sum(checks.values())
        if passed >= 4:  # At least 4 of 5 key logic components
            print(f"PASS: Reinit has correct logic ({passed}/5 components)")
            sys.exit(0)
        else:
            print(f"FAIL: Missing logic components: {checks}")
            sys.exit(1)

print("FAIL: reinit function not found")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_reinit_logic]=1

# ---------- BEHAVIORAL 4 (15%): get_metrics_router_addr exists and is non-trivial ----------
# [pr_diff] (0.15): get_metrics_router_addr public method added to rollout manager
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/slime/slime/ray/rollout.py") as f:
    src = f.read()

tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_metrics_router_addr":
        # Check it's not just a stub
        body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Constant)]
        if len(body) < 1:
            print("FAIL: get_metrics_router_addr is empty stub")
            sys.exit(1)

        # Check it calls _get_metrics_router_addr or accesses server attributes
        node_src = ast.unparse(node).upper()
        if "_GET_METRICS_ROUTER_ADDR" in node_src or "RETURN" in node_src:
            print("PASS: get_metrics_router_addr is non-trivial implementation")
            sys.exit(0)

print("FAIL: get_metrics_router_addr not found or is stub")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_get_router]=1

# ---------- BEHAVIORAL 5 (15%): train.py and train_async.py import and call the new function ----------
# [pr_diff] (0.15): update_tracking_open_metrics called in train scripts after rollout manager creation
python3 << 'PYEOF'
import ast
import sys

def check_train_file(filepath):
    with open(filepath) as f:
        src = f.read()

    # Check import exists
    if "update_tracking_open_metrics" not in src:
        return False, "update_tracking_open_metrics not imported"

    tree = ast.parse(src)

    # Check for call to update_tracking_open_metrics
    has_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "update_tracking_open_metrics":
                has_call = True
                break
            # Also check for module-qualified calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "update_tracking_open_metrics":
                has_call = True
                break

    if not has_call:
        return False, "update_tracking_open_metrics not called"

    return True, "OK"

# Check train.py
train_ok, train_msg = check_train_file("/workspace/slime/train.py")
print(f"train.py: {train_msg}")

# Check train_async.py
train_async_ok, train_async_msg = check_train_file("/workspace/slime/train_async.py")
print(f"train_async.py: {train_async_msg}")

if train_ok and train_async_ok:
    print("PASS: Both train files import and call update_tracking_open_metrics")
    sys.exit(0)
else:
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral_train_integration]=1

# ---------- ANTI-STUB (10%): wandb_utils.py has substantial implementation ----------
# [agent_config] (0.10): "Include meaningful implementation" - extensions/CLAUDE.md @ d4c4d3fb
python3 << 'PYEOF'
import sys

with open("/workspace/slime/slime/utils/wandb_utils.py") as f:
    src = f.read()

tree = ast.parse(src)

# Count actual function definitions with non-trivial bodies
func_count = 0
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        body = [stmt for stmt in node.body if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Constant)]
        if len(body) >= 3:
            func_count += 1

# Check for multiple wandb references (indicates real usage)
wandb_refs = src.count("wandb.")

# Check total lines (excluding comments/whitespace)
lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]
line_count = len(lines)

if func_count >= 3 and wandb_refs >= 5 and line_count >= 40:
    print(f"PASS: Non-trivial implementation ({func_count} funcs, {wandb_refs} wandb refs, {line_count} lines)")
    sys.exit(0)
else:
    print(f"FAIL: Implementation too small ({func_count} funcs, {wandb_refs} wandb refs, {line_count} lines)")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1

# ---------- Config-derived (0.025): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit d4c4d3fb24d45c3cd12f47b64b30fc3301286778
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$WANDB" "$LOGGING" "$ROLLOUT" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.025): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit d4c4d3fb24d45c3cd12f47b64b30fc3301286778
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$WANDB" "$LOGGING" "$ROLLOUT" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

SCORE=$(python3 -c "
w={'behavioral_router_removed':${WEIGHTS[behavioral_router_removed]},'behavioral_reinit_exists':${WEIGHTS[behavioral_reinit_exists]},'behavioral_reinit_logic':${WEIGHTS[behavioral_reinit_logic]},'behavioral_get_router':${WEIGHTS[behavioral_get_router]},'behavioral_train_integration':${WEIGHTS[behavioral_train_integration]},'antistub':${WEIGHTS[antistub]},'config_no_wildcard':${WEIGHTS[config_no_wildcard]},'config_no_bare_print':${WEIGHTS[config_no_bare_print]}}
r={'behavioral_router_removed':${RESULTS[behavioral_router_removed]},'behavioral_reinit_exists':${RESULTS[behavioral_reinit_exists]},'behavioral_reinit_logic':${RESULTS[behavioral_reinit_logic]},'behavioral_get_router':${RESULTS[behavioral_get_router]},'behavioral_train_integration':${RESULTS[behavioral_train_integration]},'antistub':${RESULTS[antistub]},'config_no_wildcard':${RESULTS[config_no_wildcard]},'config_no_bare_print':${RESULTS[config_no_bare_print]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
