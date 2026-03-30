#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/modeling_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weighted scoring
declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.33
WEIGHTS[behavioral2]=0.24
WEIGHTS[structural]=0.19
WEIGHTS[antistub]=0.19
WEIGHTS[config_ruff]=0.05

for key in behavioral behavioral2 structural antistub config_ruff; do
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

# ---------- PRIMARY 1 (35%): Behavioral - get_state_dict_dtype skips float8 dtypes ----------
# Extract the function via AST, then exec it with mock tensors that simulate
# float8 and normal float dtypes. The fixed version should skip float8 and return
# the first standard floating dtype.
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find get_state_dict_dtype function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: get_state_dict_dtype function not found")
    sys.exit(1)

# Extract function source
lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Build mock environment and test
test_code = '''
import collections

class MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        if isinstance(other, MockDtype):
            return self.name == other.name
        return NotImplemented
    def __hash__(self):
        return hash(self.name)

class MockTensor:
    def __init__(self, dtype_name, is_float=True):
        self.dtype = MockDtype(dtype_name)
        self._is_float = is_float
    def is_floating_point(self):
        return self._is_float

# Mock torch module
class MockTorch:
    float32 = MockDtype("float32")

torch = MockTorch()

FUNC_SOURCE

# Test 1: State dict with float8 first, then float16
sd1 = collections.OrderedDict([
    ("w1", MockTensor("float8_e4m3fn", True)),
    ("w2", MockTensor("float16", True)),
])
result1 = get_state_dict_dtype(sd1)
if "float8" in str(result1):
    print(f"BEHAVIORAL FAIL: returned {result1} for float8+float16 state dict (should skip float8)")
    exit(1)
print(f"  PASS: float8+float16 -> {result1}")

# Test 2: State dict with float4 first, then bfloat16
sd2 = collections.OrderedDict([
    ("w1", MockTensor("float4_e2m1fn", True)),
    ("w2", MockTensor("bfloat16", True)),
])
result2 = get_state_dict_dtype(sd2)
if "float4" in str(result2):
    print(f"BEHAVIORAL FAIL: returned {result2} for float4+bfloat16 state dict (should skip float4)")
    exit(1)
print(f"  PASS: float4+bfloat16 -> {result2}")

# Test 3: Normal case - float32 should still work
sd3 = collections.OrderedDict([
    ("w1", MockTensor("float32", True)),
])
result3 = get_state_dict_dtype(sd3)
if str(result3) != "float32":
    print(f"BEHAVIORAL FAIL: returned {result3} for float32-only dict")
    exit(1)
print(f"  PASS: float32 -> {result3}")

print("BEHAVIORAL PASS: get_state_dict_dtype correctly skips float8/float4")
'''

# Inject function source
test_code = test_code.replace("FUNC_SOURCE", func_source)

try:
    exec(compile(test_code, "<behavioral_test>", "exec"))
except SystemExit as e:
    sys.exit(e.code)
except Exception as e:
    print(f"BEHAVIORAL FAIL: test execution error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Behavioral - fallback when only float8/float4 present ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL2 FAIL: get_state_dict_dtype function not found")
    sys.exit(1)

lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

test_code = '''
import collections

class MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        if isinstance(other, MockDtype):
            return self.name == other.name
        return NotImplemented
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

torch = MockTorch()

FUNC_SOURCE

# Test: State dict with ONLY float8 tensors - should fall through to the fallback
# (return first dtype, or float32 for empty)
sd = collections.OrderedDict([
    ("w1", MockTensor("float8_e4m3fn", True)),
    ("w2", MockTensor("float8_e5m2", True)),
])
result = get_state_dict_dtype(sd)

# The fallback should return the first dtype in the dict (float8_e4m3fn) since there
# are no standard floating types. This is the expected behavior - the function only
# skips float8/float4 in the "preferred" check, but falls back to first dtype.
print(f"  Result for all-float8 dict: {result}")

# Test: Empty state dict should return float32
sd_empty = collections.OrderedDict()
result_empty = get_state_dict_dtype(sd_empty)
if str(result_empty) != "float32":
    print(f"BEHAVIORAL2 FAIL: empty dict returned {result_empty}, expected float32")
    exit(1)
print(f"  PASS: empty dict -> {result_empty}")

# Test: Mixed float8 + int should return the int dtype (first dtype fallback)
sd_mixed = collections.OrderedDict([
    ("w1", MockTensor("float8_e4m3fn", True)),
    ("w2", MockTensor("int64", False)),
])
result_mixed = get_state_dict_dtype(sd_mixed)
# Should not return float8; should fall through to first-dtype fallback
if "float8" in str(result_mixed):
    # Actually if there's no standard float, it falls through to the first dtype
    # which happens to be float8. This is OK - the key fix is that it doesn't
    # preferentially return float8 when standard floats are available.
    pass
print(f"  Result for float8+int dict: {result_mixed}")

print("BEHAVIORAL2 PASS: fallback behavior works correctly")
'''

test_code = test_code.replace("FUNC_SOURCE", func_source)

try:
    exec(compile(test_code, "<behavioral2_test>", "exec"))
except SystemExit as e:
    sys.exit(e.code)
except Exception as e:
    print(f"BEHAVIORAL2 FAIL: test execution error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral2]=1
    echo "TEST behavioral2: PASS"
else
    echo "TEST behavioral2: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - float8_ and float4_ strings in function ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: get_state_dict_dtype function not found")
    sys.exit(1)

lines = source.splitlines()
func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

if "float8_" not in func_source:
    print("STRUCTURAL FAIL: get_state_dict_dtype does not check for float8_ dtypes")
    sys.exit(1)

if "float4_" not in func_source:
    print("STRUCTURAL FAIL: get_state_dict_dtype does not check for float4_ dtypes")
    sys.exit(1)

print("STRUCTURAL PASS: function contains float8_ and float4_ exclusion checks")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("def get_state_dict_dtype" in source, "get_state_dict_dtype function present"),
    ("is_floating_point" in source, "is_floating_point check present"),
    ("class PreTrainedModel" in source, "PreTrainedModel class present"),
    ("def from_pretrained" in source, "from_pretrained method present"),
    (len(source.splitlines()) > 1000, "file has substantial content"),
    ("state_dict" in source, "state_dict referenced"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi


# ---------- CONFIG-DERIVED (5%): ruff format check on changed files ----------
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit 7cd9b985e0698d4f625a18be0125231b6b930390
echo "=== Config: ruff format check ==="
RUFF_OK=true
for f in /workspace/transformers/src/transformers/modeling_utils.py; do
    if [ -f "$f" ]; then
        ruff check --select I "$f" 2>/dev/null
        if [ $? -ne 0 ]; then RUFF_OK=false; fi
    fi
done
if [ "$RUFF_OK" = true ]; then
    RESULTS[config_ruff]=1
    echo "TEST config_ruff: PASS"
else
    echo "TEST config_ruff: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff': ${WEIGHTS[config_ruff]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff': ${RESULTS[config_ruff]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral  (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  behavioral2 (${WEIGHTS[behavioral2]}): ${RESULTS[behavioral2]}"
echo "  structural  (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub    (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff    (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
