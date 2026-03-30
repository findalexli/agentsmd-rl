#!/usr/bin/env bash
# Verifier for slime-misc-bugfix-cleanup
# Bug: Wrong var in checkpoint loading, unused multimodal_num_items, missing text_kwargs
# Files: checkpoint.py, data.py, processing_utils.py
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

CHECKPOINT="/workspace/slime/slime/backends/megatron_utils/checkpoint.py"
DATA="/workspace/slime/slime/backends/megatron_utils/data.py"
PROCESSING="/workspace/slime/slime/utils/processing_utils.py"

echo "=== slime-misc-bugfix-cleanup verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
for f in "$CHECKPOINT" "$DATA" "$PROCESSING"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f missing"
        echo "0.0000" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS"

# -- GATE: Python syntax --
echo ""
echo "GATE: Python syntax validity"
for f in "$CHECKPOINT" "$DATA" "$PROCESSING"; do
    python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "GATE FAIL: syntax error in $f"
        echo "0.0000" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_LOAD_PATH=0.20
W_BEHAV_NO_NUM_ITEMS=0.20
W_BEHAV_MM_TOKEN_TYPE=0.20
W_STRUCTURAL_CHECKPOINT=0.10
W_STRUCTURAL_DATA=0.10
W_ANTISTUB=0.10
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): checkpoint.py uses load_path instead of args.hf_checkpoint --
echo ""
echo "TEST 1: behavioral -- _load_checkpoint_hf uses load_path parameter (weight=$W_BEHAV_LOAD_PATH)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/slime/slime/backends/megatron_utils/checkpoint.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find _load_checkpoint_hf function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_load_checkpoint_hf":
        func_node = node
        break

if func_node is None:
    print("FAIL: _load_checkpoint_hf function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

# The fix: from_hf_pretrained should use load_path, not args.hf_checkpoint
has_load_path = "from_hf_pretrained(load_path" in func_src
has_buggy = "from_hf_pretrained(args.hf_checkpoint" in func_src

if has_load_path and not has_buggy:
    print("PASS: from_hf_pretrained uses load_path parameter")
    sys.exit(0)
elif has_load_path:
    print("PASS: from_hf_pretrained uses load_path (but buggy call also present)")
    sys.exit(0)
else:
    print("FAIL: from_hf_pretrained still uses args.hf_checkpoint")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_LOAD_PATH)")
fi

# -- TEST 2 (BEHAVIORAL): data.py no longer has multimodal_num_items --
echo ""
echo "TEST 2: behavioral -- multimodal_num_items removed from get_batch (weight=$W_BEHAV_NO_NUM_ITEMS)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/slime/slime/backends/megatron_utils/data.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find get_batch function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "get_batch":
        func_node = node
        break

if func_node is None:
    print("FAIL: get_batch function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

if "multimodal_num_items" in func_src:
    print("FAIL: multimodal_num_items still present in get_batch")
    sys.exit(1)
else:
    print("PASS: multimodal_num_items removed from get_batch")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_NO_NUM_ITEMS)")
fi

# -- TEST 3 (BEHAVIORAL): processing_utils.py includes return_mm_token_type_ids=False --
echo ""
echo "TEST 3: behavioral -- text_kwargs includes return_mm_token_type_ids=False (weight=$W_BEHAV_MM_TOKEN_TYPE)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/slime/slime/utils/processing_utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find build_processor_kwargs function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "build_processor_kwargs":
        func_node = node
        break

if func_node is None:
    print("FAIL: build_processor_kwargs function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

if "return_mm_token_type_ids" in func_src:
    # Verify it's set to False
    if "False" in func_src and "return_mm_token_type_ids" in func_src:
        print("PASS: return_mm_token_type_ids=False in text_kwargs")
        sys.exit(0)
    else:
        print("FAIL: return_mm_token_type_ids present but not set to False")
        sys.exit(1)
else:
    print("FAIL: return_mm_token_type_ids not found in build_processor_kwargs")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MM_TOKEN_TYPE)")
fi

# -- TEST 4 (STRUCTURAL): checkpoint.py load_path in function signature --
echo ""
echo "TEST 4: structural -- _load_checkpoint_hf has load_path parameter (weight=$W_STRUCTURAL_CHECKPOINT)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/slime/slime/backends/megatron_utils/checkpoint.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_load_checkpoint_hf":
        param_names = [arg.arg for arg in node.args.args]
        if "load_path" in param_names:
            print(f"PASS: _load_checkpoint_hf has load_path parameter: {param_names}")
            sys.exit(0)
        else:
            print(f"FAIL: _load_checkpoint_hf params: {param_names}")
            sys.exit(1)

print("FAIL: _load_checkpoint_hf not found")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_CHECKPOINT)")
fi

# -- TEST 5 (STRUCTURAL): data.py still has multimodal_data --
echo ""
echo "TEST 5: structural -- get_batch still processes multimodal_data (weight=$W_STRUCTURAL_DATA)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/slime/slime/backends/megatron_utils/data.py") as f:
    source = f.read()

# multimodal_data should still be there (only multimodal_num_items removed)
if "multimodal_data" in source and "multimodal_train_inputs" in source:
    print("PASS: multimodal_data processing preserved")
    sys.exit(0)
else:
    print("FAIL: multimodal_data processing missing")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_DATA)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- files retain core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

checks = [
    ("/workspace/slime/slime/backends/megatron_utils/checkpoint.py",
     ["_load_checkpoint_hf", "AutoBridge", "from_hf_pretrained", "load_hf_weights"]),
    ("/workspace/slime/slime/backends/megatron_utils/data.py",
     ["get_batch", "multimodal_data", "torch.cat"]),
    ("/workspace/slime/slime/utils/processing_utils.py",
     ["build_processor_kwargs", "text_kwargs", "return_tensors"]),
]

for path, required in checks:
    with open(path) as f:
        source = f.read()
    missing = [r for r in required if r not in source]
    if missing:
        print(f"FAIL: {path} missing: {missing}")
        sys.exit(1)

print("PASS: all files retain expected content")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 64e1e68f524e1da6ca646606c22e785eeb845268
echo ""
echo "TEST 7: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$CHECKPOINT" "$DATA" "$PROCESSING" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 64e1e68f524e1da6ca646606c22e785eeb845268
echo ""
echo "TEST 8: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" "$CHECKPOINT" "$DATA" "$PROCESSING" 2>/dev/null
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
