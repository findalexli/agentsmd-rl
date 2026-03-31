#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/modeling_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[gate]=0.00
WEIGHTS[behavioral_tp]=0.35
WEIGHTS[behavioral_pp]=0.35
WEIGHTS[behavioral_setter]=0.15
WEIGHTS[structural_enum]=0.05
WEIGHTS[structural_typehint]=0.05
WEIGHTS[config_ruff]=0.05

for key in gate behavioral_tp behavioral_pp behavioral_setter structural_enum structural_typehint config_ruff; do
    RESULTS[$key]=0
done

echo "=== Testing transformers-supports-tp-pp-plan ==="

# ---------- GATE: Must parse and PreTrainedModel must be importable ----------
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

try:
    with open(TARGET) as f:
        source = f.read()
    ast.parse(source)
except SyntaxError as e:
    print(f"GATE FAIL: syntax error: {e}")
    sys.exit(1)

# Verify PreTrainedModel class exists
tree = ast.parse(source)
found_class = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        found_class = True
        break

if not found_class:
    print("GATE FAIL: PreTrainedModel class not found")
    sys.exit(1)

# Verify the properties exist (hard requirement for behavioral tests)
found_tp_property = False
found_pp_property = False
found_pp_setter = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "supports_tp_plan":
                    found_tp_property = True
                if item.name == "supports_pp_plan":
                    found_pp_property = True
                if item.name == "pp_plan":
                    for dec in item.decorator_list:
                        dec_src = ast.get_source_segment(source, dec)
                        if dec_src and "setter" in dec_src:
                            found_pp_setter = True

if not found_tp_property:
    print("GATE FAIL: supports_tp_plan property not found")
    sys.exit(1)
if not found_pp_property:
    print("GATE FAIL: supports_pp_plan property not found")
    sys.exit(1)
if not found_pp_setter:
    print("GATE FAIL: pp_plan setter not found")
    sys.exit(1)

print("GATE PASS: syntax valid, PreTrainedModel with required properties found")
sys.exit(0)
PYEOF

GATE_RESULT=$?
if [ $GATE_RESULT -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
RESULTS[gate]=1
echo "GATE: PASS"

# ---------- BEHAVIORAL: supports_tp_plan returns correct values ----------
# [pr_diff] (0.35): supports_tp_plan must return False for empty dict, True for non-empty
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Extract supports_tp_plan property
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "supports_tp_plan":
                func_node = item
                break

if func_node is None:
    print("BEHAVIORAL_TP: FAIL - supports_tp_plan not found")
    sys.exit(1)

# Extract the property source
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno-1:func_node.end_lineno]))

# Execute the property in a test harness with both positive and negative cases
test_code = f"""
import sys
sys.path.insert(0, '/workspace/transformers/src')

# Mock the minimal needed context
class MockConfig:
    base_model_tp_plan = None
    base_model_pp_plan = None

class MockBaseModel:
    _tp_plan = None
    _pp_plan = None

class TestModel:
    _tp_plan = {{}}  # Empty dict - should be False
    _pp_plan = {{}}
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

# Test 1: Empty dict should return False
m1 = TestModel()
m1._tp_plan = {{}}
result1 = m1.supports_tp_plan
print(f"Test 1: supports_tp_plan with empty dict returned: {{result1}}")

if result1 != False:
    print(f"BEHAVIORAL_TP: FAIL - expected False for empty dict, got {{result1}}")
    sys.exit(1)

# Test 2: Non-empty dict should return True (catches stub that always returns False)
class TestModel2:
    _tp_plan = {{"layer0": "col"}}  # Non-empty dict - should be True
    _pp_plan = {{}}
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

m2 = TestModel2()
result2 = m2.supports_tp_plan
print(f"Test 2: supports_tp_plan with non-empty dict returned: {{result2}}")

if result2 != True:
    print(f"BEHAVIORAL_TP: FAIL - expected True for non-empty dict, got {{result2}}")
    sys.exit(1)

# Test 3: None should return False
class TestModel3:
    _tp_plan = None
    _pp_plan = None
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

m3 = TestModel3()
result3 = m3.supports_tp_plan
print(f"Test 3: supports_tp_plan with None returned: {{result3}}")

if result3 != False:
    print(f"BEHAVIORAL_TP: FAIL - expected False for None, got {{result3}}")
    sys.exit(1)

print("BEHAVIORAL_TP: PASS - returns correct values for all cases")
sys.exit(0)
"""

exec(test_code)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_tp]=1
    echo "TEST behavioral_tp: PASS"
else
    RESULTS[behavioral_tp]=0
    echo "TEST behavioral_tp: FAIL"
fi

# ---------- BEHAVIORAL: supports_pp_plan returns correct values ----------
# [pr_diff] (0.35): supports_pp_plan must return False for empty dict, True for non-empty
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Extract supports_pp_plan property
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "supports_pp_plan":
                func_node = item
                break

if func_node is None:
    print("BEHAVIORAL_PP: FAIL - supports_pp_plan not found")
    sys.exit(1)

# Extract the property source
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno-1:func_node.end_lineno]))

# Execute the property in a test harness
test_code = f"""
import sys
sys.path.insert(0, '/workspace/transformers/src')

# Mock the minimal needed context
class MockConfig:
    base_model_tp_plan = None
    base_model_pp_plan = None

class MockBaseModel:
    _tp_plan = None
    _pp_plan = None

class TestModel:
    _tp_plan = {{}}
    _pp_plan = {{}}  # Empty dict - should be False
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

# Test 1: Empty dict should return False
m1 = TestModel()
m1._pp_plan = {{}}
result1 = m1.supports_pp_plan
print(f"Test 1: supports_pp_plan with empty dict returned: {{result1}}")

if result1 != False:
    print(f"BEHAVIORAL_PP: FAIL - expected False for empty dict, got {{result1}}")
    sys.exit(1)

# Test 2: Non-empty dict should return True
class TestModel2:
    _tp_plan = {{}}
    _pp_plan = {{"layer0": ("input", "output")}}  # Non-empty - should be True
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

m2 = TestModel2()
result2 = m2.supports_pp_plan
print(f"Test 2: supports_pp_plan with non-empty dict returned: {{result2}}")

if result2 != True:
    print(f"BEHAVIORAL_PP: FAIL - expected True for non-empty dict, got {{result2}}")
    sys.exit(1)

# Test 3: None should return False
class TestModel3:
    _tp_plan = None
    _pp_plan = None
    config = MockConfig()
    base_model = MockBaseModel()

    {func_src}

m3 = TestModel3()
result3 = m3.supports_pp_plan
print(f"Test 3: supports_pp_plan with None returned: {{result3}}")

if result3 != False:
    print(f"BEHAVIORAL_PP: FAIL - expected False for None, got {{result3}}")
    sys.exit(1)

# Test 4: config.base_model_pp_plan being non-empty should return True
class MockConfig4:
    base_model_tp_plan = None
    base_model_pp_plan = {{"layer": ("in", "out")}}  # Config has plan

class TestModel4:
    _tp_plan = {{}}
    _pp_plan = {{}}  # Empty
    config = MockConfig4()
    base_model = MockBaseModel()

    {func_src}

m4 = TestModel4()
result4 = m4.supports_pp_plan
print(f"Test 4: supports_pp_plan with config plan returned: {{result4}}")

if result4 != True:
    print(f"BEHAVIORAL_PP: FAIL - expected True when config has pp_plan, got {{result4}}")
    sys.exit(1)

print("BEHAVIORAL_PP: PASS - returns correct values for all cases")
sys.exit(0)
"""

exec(test_code)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_pp]=1
    echo "TEST behavioral_pp: PASS"
else
    RESULTS[behavioral_pp]=0
    echo "TEST behavioral_pp: FAIL"
fi

# ---------- BEHAVIORAL: pp_plan setter validates input ----------
# [pr_diff] (0.15): pp_plan setter must raise ValueError on non-dict input
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find pp_plan setter
setter_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "pp_plan":
                for dec in item.decorator_list:
                    dec_src = ast.get_source_segment(source, dec)
                    if dec_src and "setter" in dec_src:
                        setter_node = item
                        break

if setter_node is None:
    print("BEHAVIORAL_SETTER: FAIL - pp_plan setter not found")
    sys.exit(1)

# Extract the setter source
lines = source.splitlines(keepends=True)
setter_src = textwrap.dedent("".join(lines[setter_node.lineno-1:setter_node.end_lineno]))

# Execute the setter in a test harness - checks that ValueError is raised
test_code = f"""
import sys

class TestModel:
    _pp_plan = None

    {setter_src}

m = TestModel()

# Test 1: Setting valid dict should work
try:
    m.pp_plan = {{"layer1": ("input", "output")}}
    print("Test 1 PASS: valid dict accepted")
except Exception as e:
    print(f"BEHAVIORAL_SETTER: FAIL - valid dict rejected: {{e}}")
    sys.exit(1)

# Test 2: Setting invalid type should raise ValueError
try:
    m.pp_plan = "not a dict"
    print("BEHAVIORAL_SETTER: FAIL - non-dict accepted without error")
    sys.exit(1)
except ValueError as e:
    print(f"Test 2 PASS: ValueError raised for non-dict: {{e}}")
except TypeError as e:
    # TypeError is also acceptable for type validation
    print(f"Test 2 PASS: TypeError raised for non-dict: {{e}}")

# Test 3: Setting None should work (sets to empty dict)
try:
    m.pp_plan = None
    print("Test 3 PASS: None accepted")
except Exception as e:
    print(f"BEHAVIORAL_SETTER: FAIL - None rejected: {{e}}")
    sys.exit(1)

print("BEHAVIORAL_SETTER: PASS - setter validates input correctly")
sys.exit(0)
"""

exec(test_code)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_setter]=1
    echo "TEST behavioral_setter: PASS"
else
    RESULTS[behavioral_setter]=0
    echo "TEST behavioral_setter: FAIL"
fi

# ---------- STRUCTURAL: PipelineParallel enum removed ----------
# [pr_diff] (0.05): PipelineParallel enum should be removed
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check that PipelineParallel enum class is removed
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PipelineParallel":
        print("STRUCTURAL_ENUM: FAIL - PipelineParallel enum still present")
        sys.exit(1)

# Also check Enum import is properly cleaned up (if present, it should be used)
# Look for "from enum import Enum" or "import enum"
import_lines = []
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == "enum":
        for alias in node.names:
            if alias.name == "Enum":
                import_lines.append(node)

if import_lines:
    # Enum is imported - verify it's actually used
    enum_usage_count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "Enum":
            enum_usage_count += 1
        if isinstance(node, ast.Attribute) and node.attr == "Enum":
            enum_usage_count += 1

    # Import line counts as one reference, so > 1 means actual usage
    if enum_usage_count <= 1:
        print("STRUCTURAL_ENUM: FAIL - unused Enum import still present")
        sys.exit(1)

print("STRUCTURAL_ENUM: PASS - PipelineParallel enum removed, Enum import cleaned")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[structural_enum]=1
    echo "TEST structural_enum: PASS"
else
    RESULTS[structural_enum]=0
    echo "TEST structural_enum: FAIL"
fi

# ---------- STRUCTURAL: _pp_plan type hint fixed ----------
# [pr_diff] (0.05): _pp_plan type hint should be dict[str, tuple[str, str]] not PipelineParallel
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/transformers/src/transformers/modeling_utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the _pp_plan annotation
found_fix = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PreTrainedModel":
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if hasattr(item.target, 'id') and item.target.id == "_pp_plan":
                    # Check annotation - should be dict[str, tuple[str, str]] or similar
                    ann_src = ast.get_source_segment(source, item.annotation)
                    if ann_src and "PipelineParallel" in ann_src:
                        print(f"STRUCTURAL_TYPEHINT: FAIL - _pp_plan still references PipelineParallel: {ann_src}")
                        sys.exit(1)
                    if ann_src and ("dict" in ann_src or "Dict" in ann_src):
                        print(f"STRUCTURAL_TYPEHINT: PASS - _pp_plan has dict type hint: {ann_src}")
                        found_fix = True
                        break

if not found_fix:
    # If no annotation found, the type hint was removed (also acceptable)
    print("STRUCTURAL_TYPEHINT: PASS - PipelineParallel reference removed from _pp_plan")
    sys.exit(0)

sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[structural_typehint]=1
    echo "TEST structural_typehint: PASS"
else
    RESULTS[structural_typehint]=0
    echo "TEST structural_typehint: FAIL"
fi

# ---------- CONFIG-DERIVED: ruff format check ----------
# [agent_config] (0.05): "Changed files pass ruff format" from CLAUDE.md provisions
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
    RESULTS[config_ruff]=0
    echo "TEST config_ruff: FAIL"
fi

# ---------- Compute final score ----------
SCORE=$(python3 -c "
weights = {
    'gate': ${WEIGHTS[gate]},
    'behavioral_tp': ${WEIGHTS[behavioral_tp]},
    'behavioral_pp': ${WEIGHTS[behavioral_pp]},
    'behavioral_setter': ${WEIGHTS[behavioral_setter]},
    'structural_enum': ${WEIGHTS[structural_enum]},
    'structural_typehint': ${WEIGHTS[structural_typehint]},
    'config_ruff': ${WEIGHTS[config_ruff]},
}
results = {
    'gate': ${RESULTS[gate]},
    'behavioral_tp': ${RESULTS[behavioral_tp]},
    'behavioral_pp': ${RESULTS[behavioral_pp]},
    'behavioral_setter': ${RESULTS[behavioral_setter]},
    'structural_enum': ${RESULTS[structural_enum]},
    'structural_typehint': ${RESULTS[structural_typehint]},
    'config_ruff': ${RESULTS[config_ruff]},
}
score = sum(weights[k] * results[k] for k in weights if k != 'gate')
print(f'{score:.2f}')
")

echo ""
echo "=== FINAL SCORE ==="
echo "  gate                 (0.00): ${RESULTS[gate]}   (must be 1)"
echo "  behavioral_tp        (${WEIGHTS[behavioral_tp]}): ${RESULTS[behavioral_tp]}"
echo "  behavioral_pp        (${WEIGHTS[behavioral_pp]}): ${RESULTS[behavioral_pp]}"
echo "  behavioral_setter    (${WEIGHTS[behavioral_setter]}): ${RESULTS[behavioral_setter]}"
echo "  structural_enum      (${WEIGHTS[structural_enum]}): ${RESULTS[structural_enum]}"
echo "  structural_typehint  (${WEIGHTS[structural_typehint]}): ${RESULTS[structural_typehint]}"
echo "  config_ruff          (${WEIGHTS[config_ruff]}): ${RESULTS[config_ruff]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
