#!/usr/bin/env bash
#
# Verification for slime-rope-theta-from-parameters
# Tests that DeepseekV32Bridge resolves rope_theta from rope_parameters dict.
#
set +e

TARGET="/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weights: >=60% behavioral, <=40% structural
WEIGHTS=(0.45 0.30 0.15 0.10)
LABELS=("f2p_fixes_bug" "p2p_regression" "struct_init_exists" "config_style")
RESULTS=(0 0 0 0)

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError:
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY (45%): Fail-to-pass - __init__ actually fixes the bug ----------
# [pr_diff] (0.45): rope_theta resolved from rope_parameters when missing
python3 << 'PYEOF'
import ast
import sys
import textwrap
import types

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find DeepseekV32Bridge class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
        cls_node = node
        break

if cls_node is None:
    print("F2P FAIL: DeepseekV32Bridge not found")
    sys.exit(1)

# Find __init__ method
init_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
        init_node = node
        break

if init_node is None:
    print("F2P FAIL: __init__ not found")
    sys.exit(1)

# Extract __init__ source and exec it with mock objects
lines = source.splitlines(keepends=True)
func_source = "".join(lines[init_node.lineno - 1:init_node.end_lineno])
func_source = textwrap.dedent(func_source)

# Mock classes for testing
class MockConfigV5:
    """Simulates transformers 5.x: rope_theta in rope_parameters"""
    rope_parameters = {"rope_theta": 500000}

class MockConfigV4:
    """Simulates transformers 4.x: rope_theta directly"""
    rope_theta = 10000

class MockConfigNeither:
    """Config with neither - should use default"""
    pass

class MockParent:
    """Mock for DeepseekV3Bridge"""
    def __init__(self, hf_config, **kwargs):
        pass

# Test harness that executes the actual agent code
def test_fix():
    """Execute the agent's __init__ and verify it fixes the bug"""

    # Create a test class using the agent's actual __init__
    test_class_source = f"""
class TestBridge(MockParent):
{chr(10).join('    ' + line for line in func_source.split(chr(10)))}
"""

    namespace = {'MockParent': MockParent}
    exec(test_class_source, namespace)
    TestBridge = namespace['TestBridge']

    # Test 1: transformers 5.x - the BUG case
    # This is what was broken: accessing hf_config.rope_theta when it doesn't exist
    config1 = MockConfigV5()
    assert not hasattr(config1, 'rope_theta'), "Setup error"

    try:
        bridge1 = TestBridge(config1)
    except AttributeError as e:
        print(f"F2P FAIL: Bug not fixed - AttributeError: {e}")
        return False

    if not hasattr(config1, 'rope_theta'):
        print("F2P FAIL: rope_theta not set on config1")
        return False
    if config1.rope_theta != 500000:
        print(f"F2P FAIL: Expected 500000, got {config1.rope_theta}")
        return False

    # Test 2: transformers 4.x - backward compatibility
    config2 = MockConfigV4()
    assert hasattr(config2, 'rope_theta') and config2.rope_theta == 10000, "Setup error"

    try:
        bridge2 = TestBridge(config2)
    except Exception as e:
        print(f"F2P FAIL: Backward compat broken: {e}")
        return False

    if config2.rope_theta != 10000:
        print(f"F2P FAIL: Backward compat broken - 4.x value changed")
        return False

    # Test 3: Neither present - should use default 1000000
    config3 = MockConfigNeither()
    assert not hasattr(config3, 'rope_theta'), "Setup error"

    try:
        bridge3 = TestBridge(config3)
    except Exception as e:
        print(f"F2P FAIL: Default case failed: {e}")
        return False

    if not hasattr(config3, 'rope_theta'):
        print("F2P FAIL: rope_theta not set (default case)")
        return False
    if config3.rope_theta != 1000000:
        print(f"F2P FAIL: Expected default 1000000, got {config3.rope_theta}")
        return False

    return True

if test_fix():
    print("F2P PASS: Bug fixed, backward compat preserved, default case works")
    sys.exit(0)
else:
    sys.exit(1)
PYEOF
RESULTS[0]=$?

# ---------- SECONDARY (30%): Pass-to-pass - No regression ----------
# [pr_diff] (0.30): Existing functionality preserved
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find DeepseekV32Bridge class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
        cls_node = node
        break

if cls_node is None:
    print("P2P FAIL: class not found")
    sys.exit(1)

# Check that _DSA_ATTENTION_MAPPING is still present
has_mapping = False
for node in cls_node.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "_DSA_ATTENTION_MAPPING":
                has_mapping = True
                break

if not has_mapping:
    print("P2P FAIL: _DSA_ATTENTION_MAPPING removed")
    sys.exit(1)

# Check that _weight_to_hf_format still exists
has_hf_format = False
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "_weight_to_hf_format":
        has_hf_format = True
        break

if not has_hf_format:
    print("P2P FAIL: _weight_to_hf_format removed")
    sys.exit(1)

# Check that _weight_to_mcore_format still exists
has_mcore_format = False
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "_weight_to_mcore_format":
        has_mcore_format = True
        break

if not has_mcore_format:
    print("P2P FAIL: _weight_to_mcore_format removed")
    sys.exit(1)

print("P2P PASS: Original methods preserved")
sys.exit(0)
PYEOF
RESULTS[1]=$?

# ---------- STRUCTURAL (15%): __init__ exists and is meaningful ----------
# [agent_config] (0.15): Proper __init__ structure
python3 << 'PYEOF'
import ast
import sys

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
    sys.exit(1)

init_node = None
for node in cls_node.body:
    if isinstance(node, ast.FunctionDef) and node.name == "__init__":
        init_node = node
        break

if init_node is None:
    print("STRUCT FAIL: __init__ not found")
    sys.exit(1)

# Check signature: (self, hf_config, **kwargs)
args = init_node.args
if len(args.args) < 2 or args.args[0].arg != "self" or args.args[1].arg != "hf_config":
    print("STRUCT FAIL: bad signature")
    sys.exit(1)

if args.kwarg is None:
    print("STRUCT FAIL: missing **kwargs")
    sys.exit(1)

# Check body is meaningful (>3 non-docstring statements)
stmt_count = 0
for stmt in init_node.body:
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
        continue
    stmt_count += 1

if stmt_count < 2:
    print("STRUCT FAIL: body too short (stub)")
    sys.exit(1)

# Check super().__init__ is called
has_super = False
for node in ast.walk(init_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "__init__":
            if isinstance(func.value, ast.Call):
                if isinstance(func.value.func, ast.Name) and func.value.func.id == "super":
                    has_super = True

if not has_super:
    print("STRUCT FAIL: super().__init__ not called")
    sys.exit(1)

print("STRUCT PASS: __init__ properly structured")
sys.exit(0)
PYEOF
RESULTS[2]=$?

# ---------- CONFIG (10%): Code style ----------
# [agent_config] (0.10): No wildcard imports, no bare print
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime_plugins/mbridge/deepseek_v32.py"
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Check for wildcard imports
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "*":
                print("STYLE FAIL: wildcard import")
                sys.exit(1)

# Check for bare print calls
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            print("STYLE FAIL: bare print()")
            sys.exit(1)

print("STYLE PASS")
sys.exit(0)
PYEOF
RESULTS[3]=$?

# ---------- CALCULATE SCORE ----------
python3 -c "
weights = [0.45, 0.30, 0.15, 0.10]
results = [${RESULTS[0]}, ${RESULTS[1]}, ${RESULTS[2]}, ${RESULTS[3]}]
score = sum(w * r for w, r in zip(weights, results))
print(f'{score:.4f}')
" > "$REWARD_FILE"

# ---------- OUTPUT ----------
echo "=== slime-rope-theta-from-parameters Results ==="
echo "  f2p_fixes_bug: ${RESULTS[0]} (weight 0.45)"
echo "  p2p_regression: ${RESULTS[1]} (weight 0.30)"
echo "  struct_init_exists: ${RESULTS[2]} (weight 0.15)"
echo "  config_style: ${RESULTS[3]} (weight 0.10)"
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
