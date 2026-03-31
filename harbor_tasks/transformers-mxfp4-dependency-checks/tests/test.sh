#!/usr/bin/env bash
# Verifier for transformers-mxfp4-dependency-checks
# Bug: combined kernels_available boolean prevents identifying which dependency is missing
# File: src/transformers/quantizers/quantizer_mxfp4.py
#
# F2P tests check that specific error/warning messages are raised for each missing dependency

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py"

echo "=== transformers-mxfp4-dependency-checks verifier ==="

# ── GATE 1: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# ── GATE 2: Bug is actually fixed (no combined boolean) ───────────────────
echo ""
echo "GATE: Bug is fixed (no combined kernels_available)"
python3 << 'PYEOF'
import sys
with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

# Check that the buggy pattern is NOT present
if "kernels_available = is_triton_available" in source or \
   "kernels_available=is_triton_available" in source:
    print("GATE FAIL: still using combined kernels_available variable (the bug)")
    sys.exit(1)

# Check that separate variables exist
if not ("triton" in source.lower() and "kernel" in source.lower()):
    print("GATE FAIL: missing triton or kernels references")
    sys.exit(1)

print("GATE PASS: combined boolean pattern removed")
sys.exit(0)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi

# Weights - 70% behavioral (F2P), 15% P2P, 10% anti-stub, 5% config
W_F2P_SEPARATE=0.20       # [pr_diff] Separate variables for triton/kernels
W_F2P_TRITON_MSG=0.15     # [pr_diff] Triton-specific warning/error messages
W_F2P_KERNELS_MSG=0.15    # [pr_diff] Kernels-specific warning/error messages
W_F2P_SPECIFIC_MSG=0.20   # [pr_diff] Messages don't say "triton and kernels" together
W_P2P=0.15                # [repo_tests] Method structure preserved
W_ANTISTUB=0.10           # [static] Not a stub implantation
W_CONFIG=0.05             # [agent_config] Follows quantizer_higgs.py pattern

SCORE="0.0"

# ── TEST 1: Separate variables exist ─────────────────────────────────────
echo ""
echo "TEST 1: F2P — triton and kernels have separate variables (weight=$W_F2P_SEPARATE)"
T1=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                func_node = item
                break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Look for assignment statements with triton and kernels in names
assignments = []
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                assignments.append(target.id.lower())

has_triton_assign = any("triton" in a for a in assignments)
has_kernels_assign = any("kernel" in a for a in assignments)

if has_triton_assign and has_kernels_assign:
    print("PASS: separate variables for triton and kernels")
    sys.exit(0)
else:
    print(f"FAIL: missing separate variable assignments (found: {assignments})")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_SEPARATE)")
fi

# ── TEST 2: Triton-specific messages ─────────────────────────────────────
echo ""
echo "TEST 2: F2P — triton-specific messages (weight=$W_F2P_TRITON_MSG)"
T2=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                func_node = item
                break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Check for triton-specific warning message
has_triton_warning = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if "warning" in func_name.lower():
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg = arg.value.lower()
                    if "triton" in msg and "triton and kernels" not in msg:
                        has_triton_warning = True
                        break

# Check for triton-specific ValueError
has_triton_error = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Raise):
        exc = node.exc
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "ValueError":
            for arg in exc.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg = arg.value.lower()
                    if "triton" in msg and "triton and kernels" not in msg:
                        has_triton_error = True
                        break

if has_triton_warning and has_triton_error:
    print("PASS: triton-specific warning and error messages found")
    sys.exit(0)
elif has_triton_warning or has_triton_error:
    print("PARTIAL: only triton warning or error found (need both)")
    sys.exit(1)
else:
    print("FAIL: no triton-specific messages found")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_TRITON_MSG)")
fi

# ── TEST 3: Kernels-specific messages ────────────────────────────────────
echo ""
echo "TEST 3: F2P — kernels-specific messages (weight=$W_F2P_KERNELS_MSG)"
T3=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                func_node = item
                break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Check for kernels-specific warning message
has_kernels_warning = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if "warning" in func_name.lower():
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg = arg.value.lower()
                    if "kernel" in msg and "triton and kernels" not in msg:
                        has_kernels_warning = True
                        break

# Check for kernels-specific ValueError
has_kernels_error = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Raise):
        exc = node.exc
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "ValueError":
            for arg in exc.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg = arg.value.lower()
                    if "kernel" in msg and "triton and kernels" not in msg:
                        has_kernels_error = True
                        break

if has_kernels_warning and has_kernels_error:
    print("PASS: kernels-specific warning and error messages found")
    sys.exit(0)
elif has_kernels_warning or has_kernels_error:
    print("PARTIAL: only kernels warning or error found (need both)")
    sys.exit(1)
else:
    print("FAIL: no kernels-specific messages found")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_KERNELS_MSG)")
fi

# ── TEST 4: Messages are separated, not combined ─────────────────────────
echo ""
echo "TEST 4: F2P — no combined 'triton and kernels' messages (weight=$W_F2P_SPECIFIC_MSG)"
T4=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                func_node = item
                break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Check all string literals in the function
has_combined_message = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        msg = node.value.lower()
        if "triton and kernels" in msg or ("triton" in msg and "kernels" in msg and "requires" in msg):
            has_combined_message = True
            break

if has_combined_message:
    print("FAIL: still has combined 'triton and kernels' message")
    sys.exit(1)
else:
    print("PASS: no combined messages found")
    sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_SPECIFIC_MSG)")
fi

# ── TEST 5: Pass-to-pass — structure preserved ───────────────────────────
echo ""
echo "TEST 5: P2P — validate_environment structure preserved (weight=$W_P2P)"
T5=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check class exists
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Mxfp4HfQuantizer":
        class_node = node
        break

if not class_node:
    print("FAIL: Mxfp4HfQuantizer class not found")
    sys.exit(1)

# Check method exists
methods = [m.name for m in class_node.body if isinstance(m, ast.FunctionDef)]
if "validate_environment" not in methods:
    print("FAIL: validate_environment method missing")
    sys.exit(1)

# Check essential references are still present
required = ["is_triton_available", "is_kernels_available", "pre_quantized", "dequantize"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing essential references: {missing}")
    sys.exit(1)

print("PASS: validate_environment structure intact")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P)")
fi

# ── TEST 6: Anti-stub ────────────────────────────────────────────────────
echo ""
echo "TEST 6: Anti-stub — meaningful implementation (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find class
class_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Mxfp4HfQuantizer":
        class_node = node
        break

if not class_node:
    print("FAIL: Mxfp4HfQuantizer class not found")
    sys.exit(1)

func_node = None
for item in class_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
        func_node = item
        break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Count actual AST nodes in the function (more granular than statement count)
node_count = len(list(ast.walk(func_node)))

# Original function has ~200+ AST nodes; stubs have <50
if node_count < 100:
    print(f"FAIL: only ~{node_count} AST nodes — looks stubbed")
    sys.exit(1)

# Check for platform-specific logic (XPU, CUDA, CPU branches)
has_device_logic = False
devices_found = set()
for node in ast.walk(func_node):
    if isinstance(node, ast.Attribute):
        if node.attr in ["xpu", "cuda", "is_available", "get_device_capability"]:
            devices_found.add(node.attr)

if len(devices_found) >= 2:
    has_device_logic = True

if not has_device_logic:
    print(f"FAIL: missing device platform logic (found: {devices_found})")
    sys.exit(1)

# Check the method has the pre_quantized branching logic
has_preq_branch = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Attribute) and node.attr == "pre_quantized":
        has_preq_branch = True
        break

if not has_preq_branch:
    print("FAIL: missing pre_quantized branching")
    sys.exit(1)

# File size check
line_count = len(source.splitlines())
if line_count < 80:
    print(f"FAIL: file too small ({line_count} lines)")
    sys.exit(1)

print(f"PASS: substantial implementation ({node_count} AST nodes, platforms: {devices_found}, {line_count} lines)")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── TEST 7: Config — follows quantizer_higgs pattern ───────────────────────
echo ""
echo "TEST 7: CONFIG — follows quantizer_higgs pattern (weight=$W_CONFIG)"
T7=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                func_node = item
                break

if not func_node:
    print("FAIL: validate_environment not found")
    sys.exit(1)

# Look for separate if-statements checking triton and kernels
has_triton_check = False
has_kernels_check = False

for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        # Convert condition to string representation
        try:
            if hasattr(ast, 'unparse'):
                condition = ast.unparse(node.test).lower()
            else:
                condition = str(node.test).lower()

            if 'triton' in condition:
                has_triton_check = True
            if 'kernel' in condition:
                has_kernels_check = True
        except:
            pass

# Also check for separate ValueError raises
triton_raises = 0
kernels_raises = 0
for node in ast.walk(func_node):
    if isinstance(node, ast.Raise):
        exc = node.exc
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "ValueError":
            for arg in exc.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    msg = arg.value.lower()
                    if "triton" in msg and "kernels" not in msg:
                        triton_raises += 1
                    if "kernel" in msg and "triton" not in msg:
                        kernels_raises += 1

if (has_triton_check and has_kernels_check) or (triton_raises >= 1 and kernels_raises >= 1):
    print("PASS: separate checks for triton and kernels (matches quantizer_higgs.py pattern)")
    sys.exit(0)
else:
    print(f"PARTIAL: triton_check={has_triton_check}, kernels_check={has_kernels_check}")
    sys.exit(1)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
