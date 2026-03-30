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
WEIGHTS[sp_fix]=0.25
WEIGHTS[cp_fix]=0.20
WEIGHTS[load_hf_config]=0.15
WEIGHTS[layer_types_q35]=0.10
WEIGHTS[layer_types_q3n]=0.10
WEIGHTS[structural]=0.10
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in sp_fix cp_fix load_hf_config layer_types_q35 layer_types_q3n structural config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
ALL_VALID=true
for f in "$TARGET_HF" "$TARGET_Q35" "$TARGET_Q3N"; do
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

# ---------- TEST 1 (25%): SP fix - tensor_parallel_output_grad=False ----------
python3 << 'PYEOF'
import ast, sys

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

# ---------- TEST 2 (20%): CP fix - dist.nn.all_gather replaced ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find HuggingfaceAttention.forward
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "HuggingfaceAttention":
        cls_node = node
        break

fwd_node = None
if cls_node:
    for node in cls_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == "forward":
            fwd_node = node
            break

if fwd_node is None:
    print("CP_FIX FAIL: forward method not found")
    sys.exit(1)

# Check that dist.nn.all_gather is NOT used in forward
# and instead _AllGatherForDuplicatedComputation.apply is used
uses_dist_all_gather = False
uses_custom_gather = False

for node in ast.walk(fwd_node):
    if isinstance(node, ast.Call):
        fn = node.func
        # Check for dist.nn.all_gather
        if isinstance(fn, ast.Attribute) and fn.attr == "all_gather":
            if isinstance(fn.value, ast.Attribute) and fn.value.attr == "nn":
                uses_dist_all_gather = True
        # Check for _AllGatherForDuplicatedComputation.apply or similar custom autograd
        if isinstance(fn, ast.Attribute) and fn.attr == "apply":
            if isinstance(fn.value, ast.Name) and "AllGather" in fn.value.id:
                uses_custom_gather = True

if uses_custom_gather and not uses_dist_all_gather:
    print("CP_FIX PASS: dist.nn.all_gather replaced with custom autograd function")
    sys.exit(0)
elif uses_custom_gather:
    print("CP_FIX PASS: custom autograd function present (dist.nn.all_gather may be in other code paths)")
    sys.exit(0)
else:
    print(f"CP_FIX FAIL: custom_gather={uses_custom_gather}, dist_all_gather={uses_dist_all_gather}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[cp_fix]=1; fi

# ---------- TEST 3 (20%): _load_hf_config in hf_attention.py ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that _load_hf_config function exists at module level
found_func = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_load_hf_config":
        found_func = True
        # Check that it has a try/except fallback
        has_try = False
        for sub in ast.walk(node):
            if isinstance(sub, ast.Try) or isinstance(sub, ast.ExceptHandler):
                has_try = True
                break
        if has_try:
            print("LOAD_HF_CONFIG PASS: _load_hf_config with fallback found in hf_attention.py")
            sys.exit(0)
        else:
            print("LOAD_HF_CONFIG FAIL: _load_hf_config has no try/except fallback")
            sys.exit(1)

if not found_func:
    print("LOAD_HF_CONFIG FAIL: _load_hf_config not found in hf_attention.py")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[load_hf_config]=1; fi

# ---------- TEST 4 (15%): layer_types fallback in qwen3_5.py ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/models/qwen3_5.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find get_qwen3_5_spec function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_qwen3_5_spec":
        func_node = node
        break

if func_node is None:
    print("LAYER_TYPES_Q35 FAIL: get_qwen3_5_spec not found")
    sys.exit(1)

# Check for hasattr check on layer_types
has_layer_types_check = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "hasattr":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "layer_types":
                    has_layer_types_check = True

if has_layer_types_check:
    print("LAYER_TYPES_Q35 PASS: layer_types fallback with hasattr check found")
    sys.exit(0)
else:
    # Also check for getattr pattern
    has_getattr = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "getattr":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "layer_types":
                        has_getattr = True
    if has_getattr:
        print("LAYER_TYPES_Q35 PASS: layer_types fallback with getattr found")
        sys.exit(0)
    else:
        print("LAYER_TYPES_Q35 FAIL: no layer_types fallback found in get_qwen3_5_spec")
        sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[layer_types_q35]=1; fi

# ---------- TEST 5 (10%): layer_types fallback in qwen3_next.py ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/models/qwen3_next.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find get_qwen3_next_spec function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_qwen3_next_spec":
        func_node = node
        break

if func_node is None:
    print("LAYER_TYPES_Q3N FAIL: get_qwen3_next_spec not found")
    sys.exit(1)

has_layer_types_check = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id in ("hasattr", "getattr"):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "layer_types":
                    has_layer_types_check = True

if has_layer_types_check:
    print("LAYER_TYPES_Q3N PASS: layer_types fallback found in get_qwen3_next_spec")
    sys.exit(0)
else:
    print("LAYER_TYPES_Q3N FAIL: no layer_types fallback found in get_qwen3_next_spec")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[layer_types_q3n]=1; fi

# ---------- TEST 6 (10%): Structural - _AllGatherForDuplicatedComputation class exists ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/models/hf_attention.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

found_class = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ClassDef) and "AllGather" in node.name:
        # Check it has forward and backward static methods
        has_forward = False
        has_backward = False
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "forward":
                    has_forward = True
                if item.name == "backward":
                    has_backward = True
        if has_forward and has_backward:
            found_class = True
            break

if found_class:
    print("STRUCTURAL PASS: custom AllGather autograd class with forward/backward found")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: custom AllGather autograd class not found or incomplete")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 051e91a33093cf3201acbbf96ca6748193a7eb1b
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET_HF" "$TARGET_Q35" "$TARGET_Q3N" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 051e91a33093cf3201acbbf96ca6748193a7eb1b
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET_HF" "$TARGET_Q35" "$TARGET_Q3N" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
python3 -c "
w = {'sp_fix': ${WEIGHTS[sp_fix]}, 'cp_fix': ${WEIGHTS[cp_fix]}, 'load_hf_config': ${WEIGHTS[load_hf_config]}, 'layer_types_q35': ${WEIGHTS[layer_types_q35]}, 'layer_types_q3n': ${WEIGHTS[layer_types_q3n]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'sp_fix': ${RESULTS[sp_fix]}, 'cp_fix': ${RESULTS[cp_fix]}, 'load_hf_config': ${RESULTS[load_hf_config]}, 'layer_types_q35': ${RESULTS[layer_types_q35]}, 'layer_types_q3n': ${RESULTS[layer_types_q3n]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in sp_fix cp_fix load_hf_config layer_types_q35 layer_types_q3n structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
