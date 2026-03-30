#!/usr/bin/env bash
# Verifier for areal-lora-xccl-versioning
# Task: LoRA and XCCL versioning bug (registry update + payload forwarding)
# Files: areal_vllm_server.py, vllm_remote.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== areal lora xccl versioning verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
GATE_PASS=true
for f in areal/engine/vllm_ext/areal_vllm_server.py areal/engine/vllm_remote.py; do
    python3 -c "
import ast, sys
try:
    with open('/workspace/AReaL/$f') as fh:
        ast.parse(fh.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'  FAIL: $f SyntaxError: {e}')
    sys.exit(1)
"
    if [ $? -ne 0 ]; then
        GATE_PASS=false
    fi
done
if [ "$GATE_PASS" = false ]; then
    echo "GATE FAIL: syntax error -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAVIORAL_REQUEST_PARAM=0.20
W_BEHAVIORAL_REGISTRY_UPDATE=0.20
W_BEHAVIORAL_PAYLOAD=0.20
W_STRUCTURAL_FUNCTION_SIG=0.10
W_ANTISTUB=0.20
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- update_weight_lora_xccl accepts request parameter --
echo ""
echo "TEST 1: behavioral -- update_weight_lora_xccl accepts request parameter (weight=$W_BEHAVIORAL_REQUEST_PARAM)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weight_lora_xccl":
        func_node = node
        break

if func_node is None:
    print("FAIL: update_weight_lora_xccl not found")
    sys.exit(1)

# Check function parameters -- should have more than just raw_request
param_names = [arg.arg for arg in func_node.args.args]
if len(param_names) >= 2:
    # Should have something like (request, raw_request) or (request: UpdateWeightsFromXcclRequestLora, raw_request: Request)
    has_request = any("request" in p.lower() for p in param_names if p != "raw_request" and p != "self")
    if has_request:
        print(f"PASS: update_weight_lora_xccl has request parameter: {param_names}")
        sys.exit(0)

# Check if the function body accesses request.lora_name
lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

if "request.lora_name" in func_src or "request.lora_int_id" in func_src:
    print("PASS: function accesses request.lora_name/lora_int_id")
    sys.exit(0)

print(f"FAIL: update_weight_lora_xccl only has params: {param_names}")
sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_REQUEST_PARAM)")
fi

# -- TEST 2 (PRIMARY): behavioral -- registry is updated after weight update --
echo ""
echo "TEST 2: behavioral -- lora_requests registry updated after weight update (weight=$W_BEHAVIORAL_REGISTRY_UPDATE)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weight_lora_xccl":
        func_node = node
        break

if func_node is None:
    print("FAIL: update_weight_lora_xccl not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# Check that the function updates lora_requests
has_registry_update = (
    "lora_requests" in func_src and
    ("lora_name" in func_src or "new_name" in func_src)
)

# Also check for helper function call
has_helper = "_register_runtime_lora_name" in func_src

if has_registry_update or has_helper:
    print("PASS: update_weight_lora_xccl updates the LoRA registry")
    sys.exit(0)
else:
    print("FAIL: no registry update found in update_weight_lora_xccl")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_REGISTRY_UPDATE)")
fi

# -- TEST 3 (PRIMARY): behavioral -- vllm_remote passes payload for LoRA XCCL updates --
echo ""
echo "TEST 3: behavioral -- vllm_remote passes payload for LoRA XCCL (weight=$W_BEHAVIORAL_PAYLOAD)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_remote.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find build_distributed_weight_update_requests
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "build_distributed_weight_update_requests":
        func_node = node
        break

if func_node is None:
    print("FAIL: build_distributed_weight_update_requests not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# The fix changes `payload={}` to `payload={} if not meta.use_lora else payload`
# or some equivalent that passes the LoRA payload

# Check that the update_endpoint HttpRequest does NOT always use empty payload
# Look for pattern: the second HttpRequest has conditional payload
if "meta.use_lora" in func_src and ("payload" in func_src):
    # More specifically, check that the update endpoint request uses payload conditionally
    # Count occurrences of 'payload={}' -- should be at most 1 (non-lora case) or 0
    empty_payload_count = func_src.count("payload={}")

    if empty_payload_count <= 1:
        print(f"PASS: update endpoint conditionally passes payload for LoRA (empty_payload count: {empty_payload_count})")
        sys.exit(0)
    elif "if not meta.use_lora" in func_src or "else payload" in func_src:
        print("PASS: conditional payload logic found")
        sys.exit(0)
    else:
        print(f"FAIL: found {empty_payload_count} empty payload assignments, expected conditional")
        sys.exit(1)
else:
    print("FAIL: no conditional LoRA payload logic in build_distributed_weight_update_requests")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_PAYLOAD)")
fi

# -- TEST 4 (SUPPLEMENTARY): structural -- function signature includes typed request --
echo ""
echo "TEST 4: structural -- function uses UpdateWeightsFromXcclRequestLora type (weight=$W_STRUCTURAL_FUNCTION_SIG)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "update_weight_lora_xccl":
        func_node = node
        break

if func_node is None:
    print("FAIL: update_weight_lora_xccl not found")
    sys.exit(1)

# Check annotations for UpdateWeightsFromXcclRequestLora
for arg in func_node.args.args:
    if arg.annotation:
        ann_src = ast.dump(arg.annotation)
        if "UpdateWeightsFromXcclRequestLora" in ann_src:
            print("PASS: parameter typed as UpdateWeightsFromXcclRequestLora")
            sys.exit(0)

# Also check function source for type reference
lines = source.splitlines(keepends=True)
func_line = "".join(lines[func_node.lineno - 1:func_node.lineno + 3])
if "UpdateWeightsFromXcclRequestLora" in func_line:
    print("PASS: UpdateWeightsFromXcclRequestLora in function definition")
    sys.exit(0)

print("FAIL: no UpdateWeightsFromXcclRequestLora type annotation found")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_FUNCTION_SIG)")
fi

# -- TEST 5: anti-stub check --
echo ""
echo "TEST 5: anti-stub -- files retain original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys

files = {
    "/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py": [
        "update_weight_lora_xccl", "build_response", "router",
        "engine_core", "call_utility_async", "UpdateWeightsFromXcclRequestLora"
    ],
    "/workspace/AReaL/areal/engine/vllm_remote.py": [
        "build_distributed_weight_update_requests", "WeightUpdateRequests",
        "HttpRequest", "use_lora", "lora_name"
    ],
}

for path, required in files.items():
    with open(path) as f:
        source = f.read()
    missing = [r for r in required if r not in source]
    if missing:
        print(f"FAIL: {path} is missing: {missing}")
        sys.exit(1)
    if len(source.splitlines()) < 100:
        print(f"FAIL: {path} too short -- likely stubbed")
        sys.exit(1)

print("PASS: all files retain original logic")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit 1927decc369d30df0037854b5d58ec7a9ca2a3b7
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" /workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py /workspace/AReaL/areal/engine/vllm_remote.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit 1927decc369d30df0037854b5d58ec7a9ca2a3b7
echo ""
echo "TEST 7: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" /workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py /workspace/AReaL/areal/engine/vllm_remote.py 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    echo "PASS"
else
    echo "FAIL: bare print() found"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
