#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/modeling_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weighted scoring - behavioral focus
WEIGHTS=(0.40 0.25 0.20 0.10 0.05)  # beh1, beh2, beh3, syntax, p2p
PASSED=(0 0 0 0 0)  # Track which checks passed

echo "=== Test: transformers-dtype-guess-state-dict ==="

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'SYNTAX FAIL: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE: Syntax error - aborting with 0"
    echo "0.00" > "$REWARD_FILE"
    exit 0
fi
PASSED[0]=1
echo "PASS: Syntax valid"

# ---------- BEHAVIORAL 1 (40%): Skip float8/float4 dtypes ----------
# [pr_diff] The fix must skip float8_e4m3fn and similar dtypes
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

import ast
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("FAIL: get_state_dict_dtype not found")
    sys.exit(1)

lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Mock with realistic dtype behavior
class MockDtype:
    def __init__(self, name):
        self.name = name
        self.__module__ = 'torch'
    def __str__(self):
        return f"torch.{self.name}"
    def __repr__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        if isinstance(other, MockDtype):
            return self.name == other.name
        return False
    def __hash__(self):
        return hash(self.name)

class MockTorch:
    float32 = MockDtype("float32")
    float16 = MockDtype("float16")
    bfloat16 = MockDtype("bfloat16")
    float8_e4m3fn = MockDtype("float8_e4m3fn")
    float8_e5m2 = MockDtype("float8_e5m2")
    float4_e2m1fn = MockDtype("float4_e2m1fn")

torch = MockTorch()
namespace = {"torch": torch, "__builtins__": __builtins__}
exec(compile(func_source, "<get_state_dict_dtype>", "exec"), namespace)
get_state_dict_dtype = namespace["get_state_dict_dtype"]

# Simulated tensor with is_floating_point
class SimTensor:
    def __init__(self, dtype_obj):
        self.dtype = dtype_obj
    def is_floating_point(self):
        name = str(self.dtype).lower()
        return any(x in name for x in ['float', 'f16', 'f32'])

import collections

# Test: float8 should be skipped for float16
sd1 = collections.OrderedDict([("w1", SimTensor(torch.float8_e4m3fn)), ("w2", SimTensor(torch.float16))])
result1 = get_state_dict_dtype(sd1)
result1_str = str(result1).lower()
if "float8" in result1_str:
    print(f"FAIL: returned {result1} for float8+float16, should skip float8")
    sys.exit(1)
if "float16" not in result1_str and "16" not in result1_str:
    print(f"FAIL: expected float16, got {result1}")
    sys.exit(1)
print(f"  PASS: float8+float16 -> {result1}")

# Test: float4 should be skipped for bfloat16
sd2 = collections.OrderedDict([("w1", SimTensor(torch.float4_e2m1fn)), ("w2", SimTensor(torch.bfloat16))])
result2 = get_state_dict_dtype(sd2)
result2_str = str(result2).lower()
if "float4" in result2_str:
    print(f"FAIL: returned {result2} for float4+bfloat16, should skip float4")
    sys.exit(1)
if "bfloat16" not in result2_str and "bf16" not in result2_str:
    print(f"FAIL: expected bfloat16, got {result2}")
    sys.exit(1)
print(f"  PASS: float4+bfloat16 -> {result2}")

print("PASS: float8/float4 correctly skipped")
PYEOF

if [ $? -eq 0 ]; then
    PASSED[1]=1
    echo "PASS: Behavioral1 - skip float8/float4"
else
    echo "FAIL: Behavioral1"
fi

# ---------- BEHAVIORAL 2 (25%): Edge case - empty state dict ----------
# [pr_diff] Empty state dict should return float32
python3 << 'PYEOF'
import sys, collections
sys.path.insert(0, '/workspace/transformers')

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

import ast
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("FAIL: Function not found")
    sys.exit(1)

lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

class MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"torch.{self.name}"

torch = type('obj', (object,), {'float32': MockDtype("float32")})()
namespace = {"torch": torch, "__builtins__": __builtins__}
exec(compile(func_source, "<func>", "exec"), namespace)
get_state_dict_dtype = namespace["get_state_dict_dtype"]

# Empty state dict should return float32
sd_empty = collections.OrderedDict()
result_empty = get_state_dict_dtype(sd_empty)
if str(result_empty) != "torch.float32":
    print(f"FAIL: empty dict returned {result_empty}, expected torch.float32")
    sys.exit(1)
print(f"  PASS: empty -> {result_empty}")
print("PASS: edge cases handled correctly")
PYEOF

if [ $? -eq 0 ]; then
    PASSED[2]=1
    echo "PASS: Behavioral2 - edge cases"
else
    echo "FAIL: Behavioral2"
fi

# ---------- BEHAVIORAL 3 (20%): Normal float dtypes still work ----------
# [pr_diff] float32, float16, bfloat16 should still be returned
python3 << 'PYEOF'
import sys, collections
sys.path.insert(0, '/workspace/transformers')

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

import ast
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("FAIL: Function not found")
    sys.exit(1)

lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

class MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        if isinstance(other, MockDtype):
            return self.name == other.name
        return False
    def __hash__(self):
        return hash(self.name)

class MockTensor:
    def __init__(self, dtype_name, is_float=True):
        self.dtype = MockDtype(dtype_name)
        self._is_float = is_float
    def is_floating_point(self):
        return self._is_float

class MockTorch:
    float32 = MockDtype("float32")
    float64 = MockDtype("float64")
    float16 = MockDtype("float16")
    bfloat16 = MockDtype("bfloat16")

torch = MockTorch()
namespace = {"torch": torch, "__builtins__": __builtins__}
exec(compile(func_source, "<func>", "exec"), namespace)
get_state_dict_dtype = namespace["get_state_dict_dtype"]

test_cases = [
    ([("w1", MockTensor("float32", True))], "float32"),
    ([("w1", MockTensor("float16", True))], "float16"),
    ([("w1", MockTensor("bfloat16", True))], "bfloat16"),
]

for weights, expected_contains in test_cases:
    sd = collections.OrderedDict(weights)
    result = get_state_dict_dtype(sd)
    result_str = str(result).lower()
    if expected_contains not in result_str:
        print(f"FAIL: {weights[0][0]} -> {result}, expected {expected_contains}")
        sys.exit(1)
    print(f"  PASS: {weights[0][0]} -> {result}")

print("PASS: normal float dtypes work correctly")
PYEOF

if [ $? -eq 0 ]; then
    PASSED[3]=1
    echo "PASS: Behavioral3 - normal floats"
else
    echo "FAIL: Behavioral3"
fi

# ---------- P2P (5%): Check transformers imports work ----------
python3 -c "
import sys
sys.path.insert(0, '/workspace/transformers')
try:
    from transformers.modeling_utils import get_state_dict_dtype
    print('PASS: Can import get_state_dict_dtype')
except Exception as e:
    print(f'FAIL: Import error: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    PASSED[4]=1
    echo "PASS: P2P - module imports"
else
    echo "NOTE: P2P import test failed (may need dependencies)"
fi

# ---------- Final score ----------
echo ""
echo "=== FINAL SCORE ==="
echo "  Check          Weight  Passed"
echo "  -----------------------------"
echo "  Behavioral1    0.40    ${PASSED[1]}"
echo "  Behavioral2    0.25    ${PASSED[2]}"
echo "  Behavioral3    0.20    ${PASSED[3]}"
echo "  Syntax         0.10    ${PASSED[0]}"
echo "  P2P            0.05    ${PASSED[4]}"
echo "  -----------------------------"

SCORE=$(python3 -c "w=[0.40,0.25,0.20,0.10,0.05]; p=[${PASSED[1]},${PASSED[2]},${PASSED[3]},${PASSED[0]},${PASSED[4]}]; print(f'{sum(wi*pi for wi,pi in zip(w,p)):.2f}')")
echo "  TOTAL: $SCORE"

echo "$SCORE" > "$REWARD_FILE"
echo "Score written to $REWARD_FILE"

# LLM rubric judge hook
source /tests/judge_hook.sh 2>/dev/null || true
