#!/usr/bin/env bash
#
# Verification for slime-httpx-disable-system-proxy
# Tests that httpx.AsyncClient instances in http_utils.py have trust_env=False.
#
set +e

TARGET="/workspace/slime/slime/utils/http_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Install httpx for behavioral tests
pip install --quiet httpx 2>/dev/null

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.30
WEIGHTS[behavioral2]=0.30
WEIGHTS[structural]=0.30
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (35%): Behavioral - init_http_client AsyncClient has trust_env=False ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/utils/http_utils.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the init_http_client function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "init_http_client":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: init_http_client function not found")
    sys.exit(1)

# Find httpx.AsyncClient(...) calls inside the function
found_trust_env_false = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        is_async_client = False
        if isinstance(func, ast.Attribute) and func.attr == "AsyncClient":
            is_async_client = True
        elif isinstance(func, ast.Name) and func.id == "AsyncClient":
            is_async_client = True

        if is_async_client:
            # Check for trust_env=False keyword
            for kw in node.keywords:
                if kw.arg == "trust_env":
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        found_trust_env_false = True
                        break

if found_trust_env_false:
    print("BEHAVIORAL PASS: init_http_client AsyncClient has trust_env=False")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: init_http_client AsyncClient missing trust_env=False")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (35%): Behavioral - Ray actor AsyncClient has trust_env=False ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/utils/http_utils.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find _init_ray_distributed_post function (or class _HttpPosterActor inside it)
# The Ray actor's AsyncClient is inside a class defined within _init_ray_distributed_post
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_init_ray_distributed_post":
        func_node = node
        break

if func_node is None:
    # Maybe the function was renamed or restructured - search entire module
    # for class _HttpPosterActor
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "HttpPoster" in node.name:
            func_node = node
            break

if func_node is None:
    print("BEHAVIORAL2 FAIL: _init_ray_distributed_post or _HttpPosterActor not found")
    sys.exit(1)

# Find httpx.AsyncClient(...) calls inside the actor class/function
found_trust_env_false = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        is_async_client = False
        if isinstance(func, ast.Attribute) and func.attr == "AsyncClient":
            is_async_client = True
        elif isinstance(func, ast.Name) and func.id == "AsyncClient":
            is_async_client = True

        if is_async_client:
            for kw in node.keywords:
                if kw.arg == "trust_env":
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        found_trust_env_false = True
                        break

if found_trust_env_false:
    print("BEHAVIORAL2 PASS: Ray actor AsyncClient has trust_env=False")
    sys.exit(0)
else:
    print("BEHAVIORAL2 FAIL: Ray actor AsyncClient missing trust_env=False")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- SECONDARY (30%): Structural - count of trust_env=False occurrences >= 2 ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/utils/http_utils.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

count = 0
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        is_async_client = False
        if isinstance(func, ast.Attribute) and func.attr == "AsyncClient":
            is_async_client = True
        elif isinstance(func, ast.Name) and func.id == "AsyncClient":
            is_async_client = True
        if is_async_client:
            for kw in node.keywords:
                if kw.arg == "trust_env" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
                    count += 1

if count >= 2:
    print(f"STRUCTURAL PASS: found {count} AsyncClient instances with trust_env=False")
    sys.exit(0)
else:
    print(f"STRUCTURAL FAIL: found only {count} AsyncClient instances with trust_env=False, need >= 2")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit e46e660059b5f2ae949ad812c7d49af823f415a3
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit e46e660059b5f2ae949ad812c7d49af823f415a3
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
