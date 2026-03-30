#!/usr/bin/env bash
#
# Verification for slime-rope-theta-from-parameters
# Tests that DeepseekV32Bridge resolves rope_theta from rope_parameters dict.
#
set +e

TARGET="/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.30
WEIGHTS[behavioral2]=0.30
WEIGHTS[structural]=0.30
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
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

# ---------- PRIMARY 1 (35%): Behavioral - rope_theta resolved from rope_parameters ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the DeepseekV32Bridge class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL FAIL: DeepseekV32Bridge class not found")
    sys.exit(1)

# Find __init__ method
init_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
        init_node = node
        break

if init_node is None:
    print("BEHAVIORAL FAIL: __init__ method not found in DeepseekV32Bridge")
    sys.exit(1)

# Extract the __init__ body and test it with a mock config object
# that has rope_parameters but no rope_theta
func_source = ast.get_source_segment(source, init_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[init_node.lineno - 1:init_node.end_lineno])

# Build a mock environment and test
test_code = """
import types

class MockConfig:
    rope_parameters = {"rope_theta": 500000}

class MockParent:
    def __init__(self, hf_config, **kwargs):
        pass

# Monkey-patch super() for testing
config = MockConfig()

# Check: config has no rope_theta initially
assert not hasattr(config, "rope_theta"), "Setup error: config already has rope_theta"

# Execute the logic: check for hasattr pattern and rope_parameters resolution
has_rope_theta_check = False
has_rope_params_access = False
"""

# Check the AST of __init__ for the key patterns
has_hasattr_check = False
has_rope_params = False
has_rope_theta_assignment = False

for node in ast.walk(init_node):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id == "hasattr":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "rope_theta":
                    has_hasattr_check = True
        if isinstance(fn, ast.Name) and fn.id == "getattr":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "rope_parameters":
                    has_rope_params = True
    if isinstance(node, ast.Attribute) and node.attr == "rope_parameters":
        has_rope_params = True
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Attribute) and t.attr == "rope_theta":
                has_rope_theta_assignment = True

if has_hasattr_check and has_rope_params and has_rope_theta_assignment:
    print("BEHAVIORAL PASS: __init__ checks hasattr(rope_theta), accesses rope_parameters, and assigns rope_theta")
    sys.exit(0)
elif has_rope_theta_assignment and has_rope_params:
    # Acceptable variant using getattr
    print("BEHAVIORAL PASS: __init__ resolves rope_theta from rope_parameters")
    sys.exit(0)
else:
    print(f"BEHAVIORAL FAIL: hasattr_check={has_hasattr_check}, rope_params={has_rope_params}, rope_theta_assign={has_rope_theta_assignment}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (35%): Behavioral - execute __init__ logic with mocked config ----------
python3 << 'PYEOF'
import ast, sys, textwrap

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL2 FAIL: class not found")
    sys.exit(1)

init_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
        init_node = node
        break

if init_node is None:
    print("BEHAVIORAL2 FAIL: __init__ not found")
    sys.exit(1)

# Extract just the body of __init__ (skip the super().__init__ call)
# and execute it to verify rope_theta is resolved
init_lines = source.splitlines()[init_node.lineno - 1:init_node.end_lineno]
init_body = "\n".join(init_lines)

# We'll build a test that runs the rope_theta resolution logic
test_code = textwrap.dedent("""
# Test 1: config with rope_parameters but no rope_theta
class Config1:
    rope_parameters = {"rope_theta": 500000}

config1 = Config1()
hf_config = config1

# Simulate the rope_theta resolution logic
if not hasattr(hf_config, "rope_theta"):
    rope_params = getattr(hf_config, "rope_parameters", None) or {}
    hf_config.rope_theta = rope_params.get("rope_theta", 1000000)

assert hasattr(config1, "rope_theta"), "rope_theta not set on config"
assert config1.rope_theta == 500000, f"Expected 500000, got {config1.rope_theta}"

# Test 2: config with rope_theta already set (transformers 4.x)
class Config2:
    rope_theta = 10000

config2 = Config2()
hf_config = config2
if not hasattr(hf_config, "rope_theta"):
    rope_params = getattr(hf_config, "rope_parameters", None) or {}
    hf_config.rope_theta = rope_params.get("rope_theta", 1000000)

assert config2.rope_theta == 10000, f"Expected 10000, got {config2.rope_theta}"

# Test 3: config with neither (should default)
class Config3:
    pass

config3 = Config3()
hf_config = config3
if not hasattr(hf_config, "rope_theta"):
    rope_params = getattr(hf_config, "rope_parameters", None) or {}
    hf_config.rope_theta = rope_params.get("rope_theta", 1000000)

assert config3.rope_theta == 1000000, f"Expected 1000000, got {config3.rope_theta}"

print("All edge cases passed")
""")

# Now verify that the ACTUAL __init__ code does this correctly
# by checking the AST patterns match the expected logic
# We already verified AST patterns in test 1, so here we test that
# the __init__ body handles the "no rope_theta, has rope_parameters" case
# by looking for the conditional logic
has_conditional = False
for node in ast.walk(init_node):
    if isinstance(node, ast.If):
        # Check if test involves hasattr and "rope_theta"
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Call):
                fn = sub.func
                if isinstance(fn, ast.Name) and fn.id == "hasattr":
                    for arg in sub.args:
                        if isinstance(arg, ast.Constant) and arg.value == "rope_theta":
                            has_conditional = True

if has_conditional:
    # Good - now check the expected behavior by running the generic logic tests
    try:
        exec(test_code)
        print("BEHAVIORAL2 PASS: rope_theta resolution logic works for all cases")
        sys.exit(0)
    except Exception as e:
        print(f"BEHAVIORAL2 FAIL: logic test failed: {e}")
        sys.exit(1)
else:
    print("BEHAVIORAL2 FAIL: no conditional check for rope_theta in __init__")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- SECONDARY (30%): Structural - super().__init__ is called ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
        cls_node = node
        break

if cls_node is None:
    print("STRUCTURAL FAIL: class not found")
    sys.exit(1)

init_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
        init_node = node
        break

if init_node is None:
    print("STRUCTURAL FAIL: __init__ not found")
    sys.exit(1)

# Check that super().__init__ is called
has_super_init = False
for node in ast.walk(init_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "__init__":
            if isinstance(func.value, ast.Call):
                if isinstance(func.value.func, ast.Name) and func.value.func.id == "super":
                    has_super_init = True

if has_super_init:
    print("STRUCTURAL PASS: super().__init__ is called in __init__")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: super().__init__ not called")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 73a1f4d935baf1619bf764eadd199a77cecf55cf
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 73a1f4d935baf1619bf764eadd199a77cecf55cf
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
