#!/usr/bin/env bash
set -uo pipefail

cd /repo

TOTAL=0.0
PASS=0.0

add() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }
award() { PASS=$(python3 -c "print($PASS + $1)"); }

# ── GATE (0): Syntax check ──────────────────────────────────────────────────
# [pr_diff] (gate): Both modified files must parse
python3 -c "
import ast, sys
for f in ['vllm/envs.py', 'vllm/platforms/xpu.py']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'GATE FAIL: {f}: {e}')
        sys.exit(1)
print('GATE: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "reward: 0.0"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ── Discover the XPU graph env var name ──────────────────────────────────────
# Accept any VLLM_* env var relating to XPU graph (not just the gold patch name)
XPU_VAR=$(python3 -c "
import re
with open('vllm/envs.py') as f:
    content = f.read()
# Match VLLM_ vars containing both XPU and GRAPH (case-insensitive via pattern)
candidates = re.findall(r'\"(VLLM_\w*(?:XPU)\w*(?:GRAPH)\w*)\"', content)
if not candidates:
    candidates = re.findall(r'\"(VLLM_\w*(?:GRAPH)\w*(?:XPU)\w*)\"', content)
if not candidates:
    # Broader: any VLLM_XPU_ var not present in the base commit
    candidates = re.findall(r'\"(VLLM_XPU_\w+)\"', content)
if candidates:
    print(candidates[0])
else:
    print('')
")

if [ -z "$XPU_VAR" ]; then
    echo "FAIL: No XPU graph env var found in envs.py"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo "Discovered XPU graph env var: $XPU_VAR"

# ── BEHAVIORAL F2P #1 (0.35): Extract and call the actual lambda from envs.py ──
# [pr_diff] (0.35): Env var lambda defaults to disabled and parses "1" as truthy, "0" as falsy
add 0.35
python3 << 'PYEOF'
import ast, os, sys

VAR_NAME = os.environ.get("_TEST_VAR", "") or "$XPU_VAR"

with open("vllm/envs.py") as f:
    source = f.read()
tree = ast.parse(source)

# Find the environment_variables dict entry for this var and extract the lambda
found_lambda = None
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == VAR_NAME:
                if isinstance(value, ast.Lambda):
                    found_lambda = value
                break
        if found_lambda:
            break

assert found_lambda is not None, f"Lambda for {VAR_NAME} not found in environment_variables dict"

# Compile and call the actual lambda with os module available
lambda_expr = ast.Expression(body=found_lambda)
ast.fix_missing_locations(lambda_expr)
code = compile(lambda_expr, "vllm/envs.py", "eval")
fn = eval(code, {"os": os, "__builtins__": __builtins__})

# Test 1: Default (env var not set) → must be falsy
os.environ.pop(VAR_NAME, None)
result = fn()
assert not result, f"Default should be falsy (disabled), got {result}"

# Test 2: Set to "1" → must be truthy
os.environ[VAR_NAME] = "1"
result = fn()
assert result, f"Set to '1' should be truthy (enabled), got {result}"

# Test 3: Set to "0" → must be falsy
os.environ[VAR_NAME] = "0"
result = fn()
assert not result, f"Set to '0' should be falsy (disabled), got {result}"

os.environ.pop(VAR_NAME, None)
print(f"PASS: {VAR_NAME} lambda defaults disabled, parses 0/1 correctly")
PYEOF
if [ $? -eq 0 ]; then award 0.35; else echo "FAIL: env var lambda behavior"; fi

# ── BEHAVIORAL F2P #2 (0.20): xpu.py check_and_update_config references env var and disables cudagraph ──
# WHY AST: xpu.py imports vllm_xpu_kernels (Intel XPU C extension) — cannot import in CPU-only env
# [pr_diff] (0.20): check_and_update_config conditionally disables cudagraph based on XPU graph env var
add 0.20
python3 << 'PYEOF'
import ast, os

VAR_NAME = "$XPU_VAR"

with open("vllm/platforms/xpu.py") as f:
    source = f.read()
tree = ast.parse(source)

# Verify envs module is imported (needed to read the env var)
has_envs_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if "envs" in alias.name:
                has_envs_import = True
    if isinstance(node, ast.ImportFrom) and node.module and "envs" in node.module:
        has_envs_import = True
assert has_envs_import, "vllm.envs not imported in xpu.py"

# Find check_and_update_config and verify it references the env var + disables cudagraph
found_method = False
has_env_ref = False
has_cudagraph_assign = False

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "check_and_update_config":
        found_method = True
        for child in ast.walk(node):
            # Accept envs.VLLM_XPU_... attribute access
            if isinstance(child, ast.Attribute) and child.attr == VAR_NAME:
                has_env_ref = True
            # Accept string references (e.g., getattr(envs, "VLLM_XPU_..."))
            if isinstance(child, ast.Constant) and isinstance(child.value, str) and VAR_NAME in child.value:
                has_env_ref = True
            # Accept cudagraph_mode or cudagraph assignment (any attribute containing "cudagraph")
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Attribute) and "cudagraph" in target.attr.lower():
                        has_cudagraph_assign = True
        break

assert found_method, "check_and_update_config method not found in xpu.py"
assert has_env_ref, f"{VAR_NAME} not referenced in check_and_update_config"
assert has_cudagraph_assign, "No cudagraph_mode assignment found in check_and_update_config"
print("PASS: xpu.py disables cudagraph based on env var")
PYEOF
if [ $? -eq 0 ]; then award 0.20; else echo "FAIL: xpu.py cudagraph disable logic"; fi

# ── PASS-TO-PASS (0.15): Existing env vars and XPU platform class preserved ──
# [repo_tests] (0.15): Existing functionality not broken
add 0.15
python3 << 'PYEOF'
with open("vllm/envs.py") as f:
    content = f.read()

# Key existing env vars must still be present
for var in ["VLLM_HOST_IP", "VLLM_CONFIGURE_LOGGING", "VLLM_TARGET_DEVICE"]:
    assert var in content, f"Existing env var {var} missing from envs.py"
assert "environment_variables" in content, "environment_variables dict missing"

with open("vllm/platforms/xpu.py") as f:
    xpu = f.read()
assert "class XPUPlatform" in xpu, "XPUPlatform class missing"
assert "check_and_update_config" in xpu, "check_and_update_config method missing"

print("PASS: existing functionality preserved")
PYEOF
if [ $? -eq 0 ]; then award 0.15; else echo "FAIL: existing functionality"; fi

# ── BEHAVIORAL (0.10): TYPE_CHECKING block declares the env var with falsy default ──
# [pr_diff] (0.10): Env var declared in TYPE_CHECKING block
add 0.10
python3 << 'PYEOF'
import ast

VAR_NAME = "$XPU_VAR"

with open("vllm/envs.py") as f:
    tree = ast.parse(f.read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.If):
        test = node.test
        is_tc = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or \
                (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
        if is_tc:
            for child in ast.walk(node):
                # Accept annotated assignment (var: bool = False) or plain (var = False)
                if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                    if child.target.id == VAR_NAME:
                        if child.value and isinstance(child.value, ast.Constant):
                            assert not child.value.value, f"Default should be falsy, got {child.value.value}"
                        found = True
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and target.id == VAR_NAME:
                            if isinstance(child.value, ast.Constant):
                                assert not child.value.value, f"Default should be falsy, got {child.value.value}"
                            found = True

assert found, f"{VAR_NAME} not declared in TYPE_CHECKING block"
print("PASS: TYPE_CHECKING declaration found")
PYEOF
if [ $? -eq 0 ]; then award 0.10; else echo "FAIL: TYPE_CHECKING declaration"; fi

# ── CONFIG (0.10): Env var follows VLLM_ naming convention ──
# [agent_config] (0.10): "Env vars use VLLM_ prefix" — AGENTS.md @ a9213c0
add 0.10
python3 << 'PYEOF'
VAR_NAME = "$XPU_VAR"
assert VAR_NAME.startswith("VLLM_"), f"{VAR_NAME} does not start with VLLM_"
assert VAR_NAME == VAR_NAME.upper(), f"{VAR_NAME} is not all uppercase"
print("PASS: naming convention followed")
PYEOF
if [ $? -eq 0 ]; then award 0.10; else echo "FAIL: naming convention"; fi

# ── ANTI-STUB (0.10): Lambda must not be trivial ──
# [static] (0.10): Lambda body contains function calls (not a constant stub)
add 0.10
python3 << 'PYEOF'
import ast

VAR_NAME = "$XPU_VAR"

with open("vllm/envs.py") as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            if isinstance(key, ast.Constant) and key.value == VAR_NAME:
                if isinstance(value, ast.Lambda):
                    body = value.body
                    # Reject trivial stubs: lambda: False, lambda: None, lambda: 0
                    assert not (isinstance(body, ast.Constant) and body.value in (None, False, True, 0, "")), \
                        "Lambda is a trivial stub (returns a constant)"
                    # Body should have at least one function call (e.g., os.getenv, int, bool)
                    has_call = any(isinstance(c, ast.Call) for c in ast.walk(body))
                    assert has_call, "Lambda body has no function calls (likely a stub)"
                    print("PASS: lambda is non-trivial")
                    exit(0)
                else:
                    # Not a lambda — at minimum check it's callable-shaped
                    print("PASS: value is non-lambda callable")
                    exit(0)
print("FAIL: env var entry not found in dict")
exit(1)
PYEOF
if [ $? -eq 0 ]; then award 0.10; else echo "FAIL: anti-stub check"; fi

# ── Compute final reward ─────────────────────────────────────────────────────
REWARD=$(python3 -c "print(round($PASS, 2))")
echo ""
echo "=== RESULTS ==="
echo "reward: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
reward = $PASS
data = {
    'reward': round(reward, 2),
    'behavioral': round(min(reward, 0.65), 2),
    'regression': round(min(max(reward - 0.65, 0), 0.15), 2),
    'config': round(min(max(reward - 0.80, 0), 0.10), 2),
    'style_rubric': 0.0
}
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
print(json.dumps(data, indent=2))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
