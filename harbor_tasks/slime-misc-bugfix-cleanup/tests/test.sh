#!/usr/bin/env bash
# Verifier for slime-misc-bugfix-cleanup
# Bug: Wrong var in checkpoint loading, unused multimodal_num_items, missing text_kwargs
# Files: checkpoint.py, data.py, processing_utils.py
#
# Self-audit:
#   Max stub score: <=0.15 (config checks only)
#   Alternative fix score: >=0.85 (valid semantic alternatives pass)
#   Behavioral: 75% | Structural: 25% (target: >=60% behavioral)
#   AST checks: 3 (justified: code requires torch.distributed + megatron, can't execute)
#   P2P: none available (upstream tests require GPU/distributed)
#
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

# -- GATE: Core functions exist (prevent empty stub files) --
echo ""
echo "GATE: Core functions exist"
python3 << 'PYEOF'
import ast, sys

required = [
    ("/workspace/slime/slime/backends/megatron_utils/checkpoint.py", "_load_checkpoint_hf"),
    ("/workspace/slime/slime/backends/megatron_utils/data.py", "get_batch"),
    ("/workspace/slime/slime/utils/processing_utils.py", "build_processor_kwargs"),
]

for path, func_name in required:
    with open(path) as f:
        tree = ast.parse(f.read())
    found = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == func_name for n in ast.walk(tree))
    if not found:
        print(f"GATE FAIL: {func_name} not found in {path}")
        sys.exit(1)

print("GATE PASS")
PYEOF

if [ $? -ne 0 ]; then
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_CHECKPOINT_FIX=0.25      # [pr_diff] _load_checkpoint_hf uses load_path, not args.hf_checkpoint
W_BEHAV_DATA_CLEANUP=0.25        # [pr_diff] multimodal_num_items removed but multimodal_data preserved
W_BEHAV_PROCESSOR_KWARGS=0.25    # [pr_diff] text_kwargs has return_mm_token_type_ids=False
W_STRUCTURAL_FUNC_SIG=0.10       # [agent_config] _load_checkpoint_hf has load_path param
W_ANTISTUB_DEPTH=0.10            # [static] Functions have meaningful body depth (>3 stmts)
W_CONFIG_NO_WILDCARD=0.05        # [agent_config] No wildcard imports

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): checkpoint.py uses load_path parameter --
# [pr_diff] (0.25): _load_checkpoint_hf should use load_path arg, not args.hf_checkpoint
echo ""
echo "TEST 1: behavioral -- _load_checkpoint_hf uses load_path parameter (weight=$W_BEHAV_CHECKPOINT_FIX)"
T1=$(python3 << 'PYEOF'
import ast, sys, re

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
    print("FAIL: _load_checkpoint_hf not found")
    sys.exit(1)

# Extract parameter names
param_names = [arg.arg for arg in func_node.args.args]
if "load_path" not in param_names:
    print("FAIL: load_path parameter not found")
    sys.exit(1)

# Track usage patterns
uses_load_path = False
uses_hf_checkpoint = False

# Walk through all nodes in function body
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        # Check for from_hf_pretrained call
        is_from_hf = False
        if isinstance(node.func, ast.Attribute) and node.func.attr == "from_hf_pretrained":
            is_from_hf = True
        elif isinstance(node.func, ast.Name) and node.func.id == "from_hf_pretrained":
            is_from_hf = True

        if is_from_hf and node.args:
            first_arg = node.args[0]
            # Check for args.hf_checkpoint
            if isinstance(first_arg, ast.Attribute):
                if isinstance(first_arg.value, ast.Name) and first_arg.value.id == "args" and \
                   first_arg.attr == "hf_checkpoint":
                    uses_hf_checkpoint = True
            # Check for load_path
            elif isinstance(first_arg, ast.Name) and first_arg.id == "load_path":
                uses_load_path = True

# The fix: must NOT use args.hf_checkpoint
if uses_hf_checkpoint:
    print("FAIL: still uses args.hf_checkpoint (bug not fixed)")
    sys.exit(1)
elif uses_load_path:
    print("PASS: from_hf_pretrained uses load_path parameter")
    sys.exit(0)
else:
    # Fallback: string check for edge cases
    func_lines = source.splitlines()[func_node.lineno-1:func_node.end_lineno]
    func_src = "\n".join(func_lines)

    has_buggy = re.search(r'from_hf_pretrained\s*\(\s*args\.hf_checkpoint', func_src)
    has_fix = re.search(r'from_hf_pretrained\s*\(\s*load_path', func_src)

    if has_buggy and not has_fix:
        print("FAIL: uses args.hf_checkpoint (string check)")
        sys.exit(1)
    elif has_fix:
        print("PASS: from_hf_pretrained uses load_path (string check)")
        sys.exit(0)
    else:
        print("FAIL: cannot determine which variable is used")
        sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CHECKPOINT_FIX)")
fi

# -- TEST 2 (BEHAVIORAL): data.py removes multimodal_num_items, preserves multimodal_data --
# [pr_diff] (0.25): multimodal_num_items removed from get_batch; multimodal_train_inputs still works
echo ""
echo "TEST 2: behavioral -- multimodal_num_items removed but multimodal_data preserved (weight=$W_BEHAV_DATA_CLEANUP)"
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
    print("FAIL: get_batch not found")
    sys.exit(1)

# Check for multimodal_num_items assignment
has_num_items = False
has_mm_data = False
has_mm_train_inputs = False

for node in ast.walk(func_node):
    # Check assignments
    if isinstance(node, ast.Assign):
        for target in node.targets:
            # Direct variable assignment
            if isinstance(target, ast.Name):
                if target.id == "multimodal_num_items":
                    has_num_items = True
                elif target.id == "multimodal_data":
                    has_mm_data = True
            # Subscript assignment batch[...] = ...
            elif isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name) and target.value.id == "batch":
                    slice_val = None
                    if isinstance(target.slice, ast.Constant):
                        slice_val = target.slice.value
                    elif hasattr(target.slice, 's'):
                        slice_val = target.slice.s
                    if slice_val == "multimodal_num_items":
                        has_num_items = True

    # Check for batch.get("multimodal_train_inputs", ...)
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "batch":
                if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == "multimodal_train_inputs":
                    has_mm_train_inputs = True

# Check for multimodal_data = {} (empty dict creation)
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "multimodal_data":
                if isinstance(node.value, ast.Dict) and len(node.value.keys) == 0:
                    has_mm_data = True

# Verify the fix
if has_num_items:
    print("FAIL: multimodal_num_items still assigned in get_batch")
    sys.exit(1)

if not has_mm_train_inputs:
    print("FAIL: multimodal_train_inputs processing removed")
    sys.exit(1)

if not has_mm_data:
    print("FAIL: multimodal_data dictionary not created")
    sys.exit(1)

print("PASS: multimodal_num_items removed, multimodal_data preserved")
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_DATA_CLEANUP)")
fi

# -- TEST 3 (BEHAVIORAL): processing_utils.py includes return_mm_token_type_ids=False in text_kwargs --
# [pr_diff] (0.25): text_kwargs includes return_mm_token_type_ids=False
echo ""
echo "TEST 3: behavioral -- text_kwargs includes return_mm_token_type_ids=False (weight=$W_BEHAV_PROCESSOR_KWARGS)"
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
    print("FAIL: build_processor_kwargs not found")
    sys.exit(1)

def check_return_mm_token_type_ids(node):
    """Check if node is a dict containing return_mm_token_type_ids=False."""
    if not isinstance(node, ast.Dict):
        return False, False

    has_return_mm = False
    is_false = False

    for key, value in zip(node.keys, node.values):
        if key is None:  # **kwargs unpacking
            continue
        key_val = None
        if isinstance(key, ast.Constant):
            key_val = key.value
        elif hasattr(key, 's'):
            key_val = key.s

        if key_val == "return_mm_token_type_ids":
            has_return_mm = True
            if isinstance(value, ast.Constant) and value.value is False:
                is_false = True
            elif isinstance(value, ast.NameConstant) and value.value is False:
                is_false = True

    return has_return_mm, is_false

# Find text_kwargs assignment
has_return_mm = False
is_false = False

for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            slice_val = None
            # Check result["text_kwargs"] = ...
            if isinstance(target, ast.Subscript):
                if isinstance(target.value, ast.Name) and target.value.id == "result":
                    if isinstance(target.slice, ast.Constant):
                        slice_val = target.slice.value
                    elif hasattr(target.slice, 's'):
                        slice_val = target.slice.s
            # Check direct text_kwargs = ...
            elif isinstance(target, ast.Name) and target.id == "text_kwargs":
                slice_val = "text_kwargs"

            if slice_val == "text_kwargs":
                # Check the value being assigned
                if isinstance(node.value, ast.Dict):
                    has_return_mm, is_false = check_return_mm_token_type_ids(node.value)
                elif isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.BitOr):
                    # Python 3.9+ dict merge: {..} | {..}
                    for side in [node.value.left, node.value.right]:
                        hm, iff = check_return_mm_token_type_ids(side)
                        if hm:
                            has_return_mm = True
                        if iff:
                            is_false = True

if not has_return_mm:
    print("FAIL: return_mm_token_type_ids not found in text_kwargs")
    sys.exit(1)

if not is_false:
    print("FAIL: return_mm_token_type_ids present but not set to False")
    sys.exit(1)

print("PASS: return_mm_token_type_ids=False in text_kwargs")
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_PROCESSOR_KWARGS)")
fi

# -- TEST 4 (STRUCTURAL): checkpoint.py has load_path parameter in function signature --
# [agent_config] (0.10): Function signature validation for API contract
echo ""
echo "TEST 4: structural -- _load_checkpoint_hf has load_path parameter (weight=$W_STRUCTURAL_FUNC_SIG)"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/slime/slime/backends/megatron_utils/checkpoint.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_load_checkpoint_hf":
        param_names = [arg.arg for arg in node.args.args]
        if "load_path" in param_names:
            print("PASS: load_path parameter found")
            sys.exit(0)
        else:
            print(f"FAIL: params are {param_names}")
            sys.exit(1)

print("FAIL: _load_checkpoint_hf not found")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_FUNC_SIG)")
fi

# -- TEST 5: Anti-stub depth check --
# [static] (0.10): Functions must have meaningful implementation (not just pass/ellipsis)
echo ""
echo "TEST 5: anti-stub -- functions have meaningful body depth (weight=$W_ANTISTUB_DEPTH)"
python3 << 'PYEOF'
import ast, sys

def count_meaningful_statements(body):
    """Count non-docstring, non-pass statements."""
    count = 0
    for stmt in body:
        # Skip docstrings
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Str, ast.Constant)):
            continue
        # Skip pass
        if isinstance(stmt, ast.Pass):
            continue
        # Skip ellipsis
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value == ...:
            continue
        # Count compound statements with their body
        if isinstance(stmt, (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.FunctionDef)):
            count += 1 + count_meaningful_statements(getattr(stmt, 'body', []))
            if hasattr(stmt, 'orelse'):
                count += count_meaningful_statements(stmt.orelse)
        elif isinstance(stmt, ast.Assign):
            # Count assignments with non-empty values
            if not (isinstance(stmt.value, ast.Constant) and stmt.value.value is None):
                count += 1
        else:
            count += 1
    return count

files_funcs = [
    ("/workspace/slime/slime/backends/megatron_utils/checkpoint.py", "_load_checkpoint_hf"),
    ("/workspace/slime/slime/backends/megatron_utils/data.py", "get_batch"),
    ("/workspace/slime/slime/utils/processing_utils.py", "build_processor_kwargs"),
]

for path, func_name in files_funcs:
    with open(path) as f:
        tree = ast.parse(f.read())

    found = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            found = True
            depth = count_meaningful_statements(node.body)
            if depth < 3:
                print(f"FAIL: {func_name} in {path} has only {depth} meaningful statements (need >= 3)")
                sys.exit(1)
            break

    if not found:
        print(f"FAIL: {func_name} not found in {path}")
        sys.exit(1)

print("PASS: all functions have meaningful implementation depth")
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB_DEPTH)")
fi

# -- TEST 6: Config-derived checks --
# -- Config-derived (0.05): No wildcard imports --
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 64e1e68f524e1da6ca646606c22e785eeb845268
echo ""
echo "TEST 6: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$CHECKPOINT" "$DATA" "$PROCESSING" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
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
