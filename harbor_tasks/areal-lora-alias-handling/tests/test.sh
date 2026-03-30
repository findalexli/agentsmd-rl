#!/usr/bin/env bash
# Verifier for areal-lora-alias-handling
# Task: harden runtime LoRA alias handling for XCCL updates
# File: areal/engine/vllm_ext/areal_vllm_server.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py"

echo "=== areal lora alias handling verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAVIORAL_HELPER_EXISTS=0.20
W_BEHAVIORAL_STALE_CLEANUP=0.15
W_BEHAVIORAL_NEW_LORAREQUEST=0.15
W_BEHAVIORAL_SUCCESS_CHECK=0.15
W_STRUCTURAL_IMPORT=0.10
W_ANTISTUB=0.15
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- dedicated helper function exists --
echo ""
echo "TEST 1: behavioral -- dedicated LoRA registration helper exists (weight=$W_BEHAVIORAL_HELPER_EXISTS)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Look for a helper function that handles LoRA registration
helper_funcs = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        name = node.name.lower()
        if "lora" in name and ("register" in name or "alias" in name or "runtime" in name or "infer" in name):
            helper_funcs.append(node.name)

if len(helper_funcs) >= 1:
    print(f"PASS: found LoRA helper function(s): {helper_funcs}")
    sys.exit(0)
else:
    # Also check for inline refactoring - does update_weight_lora_xccl create new LoRARequest?
    if "_register_runtime_lora_name" in source or "_infer_runtime_lora_path" in source:
        print("PASS: found registration helper functions")
        sys.exit(0)
    print("FAIL: no dedicated LoRA registration helper found")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_HELPER_EXISTS)")
fi

# -- TEST 2 (PRIMARY): behavioral -- stale alias cleanup (removes old names for same adapter id) --
echo ""
echo "TEST 2: behavioral -- stale alias cleanup for same adapter id (weight=$W_BEHAVIORAL_STALE_CLEANUP)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

# The fix should iterate over existing entries and delete stale ones
# Check for pattern: loop over lora_requests and delete entries with matching int_id but different name
has_cleanup = False

# Look for del requests[name] or del requests[old_name] pattern
if "del requests[" in source or "del models_obj.lora_requests[" in source:
    # Check if it's inside a loop that checks lora_int_id
    if "lora_int_id" in source and ("for " in source):
        has_cleanup = True

if has_cleanup:
    print("PASS: stale alias cleanup pattern found (delete by adapter id)")
    sys.exit(0)
else:
    # Alternative: the update_weight_lora_xccl function may replace entries
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if "lora" in node.name.lower() and ("register" in node.name.lower() or "update" in node.name.lower()):
                lines = source.splitlines(keepends=True)
                func_src = "".join(lines[node.lineno - 1:node.end_lineno])
                if "del " in func_src and "lora_int_id" in func_src:
                    print("PASS: stale alias cleanup in function " + node.name)
                    sys.exit(0)
    print("FAIL: no stale alias cleanup pattern found")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_STALE_CLEANUP)")
fi

# -- TEST 3 (PRIMARY): behavioral -- creates new LoRARequest instead of mutating --
echo ""
echo "TEST 3: behavioral -- creates new LoRARequest (weight=$W_BEHAVIORAL_NEW_LORAREQUEST)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

# Check that LoRARequest is constructed somewhere (not just mutated)
if "LoRARequest(" in source:
    # Verify it's used in a registration context, not just imports
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'id') and node.func.id == 'LoRARequest':
                print("PASS: new LoRARequest is constructed")
                sys.exit(0)
            elif hasattr(node.func, 'attr') and node.func.attr == 'LoRARequest':
                print("PASS: new LoRARequest is constructed")
                sys.exit(0)
    print("PASS: LoRARequest() call found in source")
    sys.exit(0)
else:
    print("FAIL: no new LoRARequest construction found")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_NEW_LORAREQUEST)")
fi

# -- TEST 4 (PRIMARY): behavioral -- only updates registry after XCCL success --
echo ""
echo "TEST 4: behavioral -- registry update gated on XCCL success (weight=$W_BEHAVIORAL_SUCCESS_CHECK)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find update_weight_lora_xccl function
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

# Check that registry update is gated on success
# Look for patterns like: if all(success ...) or if all(ret ...) before registration
if "all(" in func_src and ("success" in func_src or "ret" in func_src):
    print("PASS: registry update gated on all() success check")
    sys.exit(0)
elif "if " in func_src and ("success" in func_src):
    print("PASS: registry update appears gated on success check")
    sys.exit(0)
else:
    # The old code just always updated -- check that the new code at least
    # calls the helper function rather than inline mutation
    if "_register_runtime_lora_name" in func_src:
        print("PASS: uses dedicated registration helper (may have success check)")
        sys.exit(0)
    print("FAIL: no success check before registry update")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_SUCCESS_CHECK)")
fi

# -- TEST 5 (SUPPLEMENTARY): structural -- imports LoRARequest --
echo ""
echo "TEST 5: structural -- imports LoRARequest (weight=$W_STRUCTURAL_IMPORT)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

if "from vllm.lora.request import LoRARequest" in source or "from vllm.lora import" in source:
    print("PASS: LoRARequest import found")
    sys.exit(0)
elif "LoRARequest" in source:
    print("PASS: LoRARequest referenced in source")
    sys.exit(0)
else:
    print("FAIL: no LoRARequest import or reference")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_IMPORT)")
fi

# -- TEST 6: anti-stub check --
echo ""
echo "TEST 6: anti-stub -- file retains original logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/engine/vllm_ext/areal_vllm_server.py") as f:
    source = f.read()

required = ["update_weight_lora_xccl", "build_response", "router", "UpdateWeightsFromXcclRequestLora",
            "engine_core", "call_utility_async", "lora_name", "lora_int_id"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 200:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit 02a25454bc8ff348b05ae2a62040d5ec48237e16
echo ""
echo "TEST 7: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit 02a25454bc8ff348b05ae2a62040d5ec48237e16
echo ""
echo "TEST 8: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
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
