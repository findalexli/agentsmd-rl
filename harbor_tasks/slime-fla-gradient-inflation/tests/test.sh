#!/usr/bin/env bash
#
# Verification for slime-fla-gradient-inflation
# Tests the SP/CP gradient fix in hf_attention.py and layer_types fallback.
#
set +e

TARGET_HF="/workspace/slime/slime_plugins/models/hf_attention.py"
TARGET_Q35="/workspace/slime/slime_plugins/models/qwen3_5.py"
TARGET_Q3N="/workspace/slime/slime_plugins/models/qwen3_next.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[sp_fix]=0.30
WEIGHTS[cp_fix]=0.25
WEIGHTS[layer_types_works]=0.25
WEIGHTS[load_hf_config]=0.10
WEIGHTS[no_wildcard]=0.05
WEIGHTS[no_bare_print]=0.05

for key in sp_fix cp_fix layer_types_works load_hf_config no_wildcard no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
ALL_VALID=true
for f in "$TARGET_HF" "$TARGET_Q35" "$TARGET_Q3N"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAIL: $f does not exist"
        ALL_VALID=false
        continue
    fi
    python3 -c "
import ast, sys
try:
    with open('$f') as fh:
        ast.parse(fh.read())
except SyntaxError as e:
    print(f'GATE FAIL: {e}')
    sys.exit(1)
" || ALL_VALID=false
done

if [ "$ALL_VALID" = false ]; then
    echo "GATE FAIL: syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: all files have valid syntax"

# ---------- TEST 1 (30%): SP fix - tensor_parallel_output_grad=False ----------
# [pr_diff] (0.30): SP gather backward must use tensor_parallel_output_grad=False
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find HuggingfaceAttention class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HuggingfaceAttention":
        cls_node = node
        break

if cls_node is None:
    print("SP_FIX FAIL: HuggingfaceAttention class not found")
    sys.exit(1)

# Find forward method
fwd_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "forward":
        fwd_node = node
        break

if fwd_node is None:
    print("SP_FIX FAIL: forward method not found")
    sys.exit(1)

# Find call to gather_from_sequence_parallel_region and check for tensor_parallel_output_grad=False
found_fix = False
for node in ast.walk(fwd_node):
    if isinstance(node, ast.Call):
        fn = node.func
        is_gather = False
        if isinstance(fn, ast.Attribute) and fn.attr == "gather_from_sequence_parallel_region":
            is_gather = True
        elif isinstance(fn, ast.Name) and fn.id == "gather_from_sequence_parallel_region":
            is_gather = True
        if is_gather:
            for kw in node.keywords:
                if kw.arg == "tensor_parallel_output_grad":
                    # Check for False (constant False, not just falsy)
                    if isinstance(kw.value, ast.Constant) and kw.value.value is False:
                        found_fix = True
                        break

if found_fix:
    print("SP_FIX PASS: gather_from_sequence_parallel_region has tensor_parallel_output_grad=False")
    sys.exit(0)
else:
    print("SP_FIX FAIL: tensor_parallel_output_grad=False not found on gather call")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[sp_fix]=1; fi

# ---------- TEST 2 (25%): CP fix - custom autograd class with correct structure ----------
# [pr_diff] (0.25): dist.nn.all_gather replaced with custom autograd for duplicated computation
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find a class inheriting from torch.autograd.Function
found_class = None
has_forward = False
has_backward = False
backward_returns_slice = False

for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef):
        # Check for inheritance from torch.autograd.Function
        has_autograd_parent = False
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == "Function":
                    has_autograd_parent = True
            elif isinstance(base, ast.Name):
                if base.id == "Function":
                    has_autograd_parent = True

        if not has_autograd_parent:
            continue

        # Check for forward and backward static methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "forward":
                    # Check it's a staticmethod
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "staticmethod":
                            has_forward = True
                if item.name == "backward":
                    for dec in item.decorator_list:
                        if isinstance(dec, ast.Name) and dec.id == "staticmethod":
                            has_backward = True

                    # Check backward returns (grads[rank], None) pattern
                    for stmt in item.body:
                        if isinstance(stmt, ast.Return):
                            if isinstance(stmt.value, ast.Tuple):
                                if len(stmt.value.elts) == 2:
                                    # Check second element is None (the group arg)
                                    second = stmt.value.elts[1]
                                    if isinstance(second, ast.Constant) and second.value is None:
                                        backward_returns_slice = True

        if has_forward and has_backward:
            found_class = node.name
            break

if found_class is None:
    print("CP_FIX FAIL: no custom autograd Function with forward/backward found")
    sys.exit(1)

if not backward_returns_slice:
    print("CP_FIX PASS: custom autograd " + found_class + " found (forward/backward)")
    sys.exit(0)
else:
    print("CP_FIX PASS: custom autograd " + found_class + " found with correct backward signature")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[cp_fix]=1; fi

# ---------- TEST 3 (25%): layer_types fallback logic correctness ----------
# [pr_diff] (0.25): layer_types computed from full_attention_interval when not on config
python3 << 'PYEOF'
import ast
import sys

TARGET_35 = "/workspace/slime/slime_plugins/models/qwen3_5.py"
TARGET_3N = "/workspace/slime/slime_plugins/models/qwen3_next.py"

def analyze_layer_types_fallback(filepath, func_name):
    """Analyze that layer_types fallback is correctly implemented."""
    with open(filepath) as f:
        source = f.read()

    tree = ast.parse(source)

    # Find the spec function
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_node = node
            break

    if func_node is None:
        return False, f"{func_name} not found"

    # Check for hasattr or getattr pattern
    has_layer_types_check = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                if fn.id == "hasattr":
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and arg.value == "layer_types":
                            has_layer_types_check = True
                elif fn.id == "getattr":
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and arg.value == "layer_types":
                            has_layer_types_check = True

    if not has_layer_types_check:
        return False, "no layer_types check found"

    # Check for full_attention_interval reference
    has_interval = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Attribute):
            if node.attr == "full_attention_interval":
                has_interval = True
        elif isinstance(node, ast.Constant):
            if node.value == "full_attention_interval":
                has_interval = True

    if not has_interval:
        return False, "no full_attention_interval reference found"

    # Check for list comprehension or loop that builds layer_types
    has_list_build = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.ListComp):
            has_list_build = True
        if isinstance(node, ast.For):
            has_list_build = True
        # Also check for range() which is typically used
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "range":
                has_list_build = True

    if not has_list_build:
        return False, "no list building pattern found for layer_types"

    return True, "fallback logic complete"

# Check both files
r35, msg35 = analyze_layer_types_fallback(TARGET_35, "get_qwen3_5_spec")
r3n, msg3n = analyze_layer_types_fallback(TARGET_3N, "get_qwen3_next_spec")

if r35 and r3n:
    print(f"LAYER_TYPES_PASS: both files have correct fallback ({msg35})")
    sys.exit(0)
else:
    if not r35:
        print(f"LAYER_TYPES_FAIL qwen3_5.py: {msg35}")
    if not r3n:
        print(f"LAYER_TYPES_FAIL qwen3_next.py: {msg3n}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[layer_types_works]=1; fi

# ---------- TEST 4 (10%): _load_hf_config exists with fallback ----------
# [pr_diff] (0.10): _load_hf_config with fallback for unsupported model types
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that _load_hf_config function exists at module level
found_func = False
has_error_handling = False
has_config_json = False

for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_load_hf_config":
        found_func = True

        # Check that it has try/except fallback
        for sub in ast.walk(node):
            if isinstance(sub, ast.Try):
                has_error_handling = True

            # Check for config.json reference
            if isinstance(sub, ast.Constant):
                if isinstance(sub.value, str) and "config.json" in sub.value:
                    has_config_json = True

        break

if not found_func:
    print("LOAD_HF_CONFIG FAIL: _load_hf_config not found")
    sys.exit(1)

if not has_error_handling:
    print("LOAD_HF_CONFIG FAIL: no try/except error handling")
    sys.exit(1)

if not has_config_json:
    print("LOAD_HF_CONFIG FAIL: no config.json fallback reference")
    sys.exit(1)

print("LOAD_HF_CONFIG PASS: _load_hf_config with complete fallback found")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[load_hf_config]=1; fi

# ---------- TEST 5 (5%): No wildcard imports in production code ----------
# [agent_config] (0.05): No wildcard imports pattern
python3 << 'PYEOF'
import ast
import sys

TARGETS = [
    "/workspace/slime/slime_plugins/models/hf_attention.py",
    "/workspace/slime/slime_plugins/models/qwen3_5.py",
    "/workspace/slime/slime_plugins/models/qwen3_next.py"
]

has_wildcard = False
for target in TARGETS:
    try:
        with open(target) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        has_wildcard = True
                        print(f"WILDCARD in {target}: from {node.module} import *")
    except Exception as e:
        print(f"ERROR checking {target}: {e}")

if has_wildcard:
    sys.exit(1)
else:
    print("NO_WILDCARD PASS")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[no_wildcard]=1; fi

# ---------- TEST 6 (5%): No bare print() in production code ----------
# [agent_config] (0.05): No bare print statements pattern
python3 << 'PYEOF'
import ast
import sys

TARGETS = [
    "/workspace/slime/slime_plugins/models/hf_attention.py",
    "/workspace/slime/slime_plugins/models/qwen3_5.py",
    "/workspace/slime/slime_plugins/models/qwen3_next.py"
]

has_print = False
for target in TARGETS:
    try:
        with open(target) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    has_print = True
                    print(f"PRINT in {target}")
    except Exception as e:
        print(f"ERROR checking {target}: {e}")

if has_print:
    sys.exit(1)
else:
    print("NO_PRINT PASS")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[no_bare_print]=1; fi

# ---------- SCORE ----------
SCORE=$(python3 -c "
w = {'sp_fix': ${WEIGHTS[sp_fix]}, 'cp_fix': ${WEIGHTS[cp_fix]}, 'layer_types_works': ${WEIGHTS[layer_types_works]}, 'load_hf_config': ${WEIGHTS[load_hf_config]}, 'no_wildcard': ${WEIGHTS[no_wildcard]}, 'no_bare_print': ${WEIGHTS[no_bare_print]}}
r = {'sp_fix': ${RESULTS[sp_fix]}, 'cp_fix': ${RESULTS[cp_fix]}, 'layer_types_works': ${RESULTS[layer_types_works]}, 'load_hf_config': ${RESULTS[load_hf_config]}, 'no_wildcard': ${RESULTS[no_wildcard]}, 'no_bare_print': ${RESULTS[no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
")
echo "$SCORE" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in sp_fix cp_fix layer_types_works load_hf_config no_wildcard no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
