#!/usr/bin/env bash
set +e

REPO="/workspace/sglang"
LOG_DIR="/logs/verifier"
mkdir -p "$LOG_DIR"

TARGET="$REPO/python/sglang/test/test_utils.py"
SCORE=0

add() { SCORE=$(python3 -c "print(round($SCORE + $1, 4))"); }

# Helper: extract CustomTestCase from source and define it in a temp module
# This avoids importing heavy sglang deps (torch, triton, etc.)
EXTRACT_HELPER='
import sys, types, unittest, textwrap

def extract_custom_testcase(path):
    """Extract CustomTestCase class from source without importing sglang."""
    with open(path) as f:
        source = f.read()
    lines = source.split("\n")
    in_class = False
    indent = None
    method_lines = []
    for line in lines:
        if "class CustomTestCase(unittest.TestCase):" in line:
            in_class = True
            indent = len(line) - len(line.lstrip())
            continue
        if in_class:
            if line.strip() == "":
                method_lines.append(line)
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent and line.strip():
                break
            method_lines.append(line)
    if not method_lines:
        return None
    min_indent = min((len(l) - len(l.lstrip()) for l in method_lines if l.strip()), default=0)
    reindented = ["    " + l[min_indent:] if l.strip() else "" for l in method_lines]
    ns = {"__builtins__": __builtins__}
    exec("import unittest\n\nclass CustomTestCase(unittest.TestCase):\n" + "\n".join(reindented), ns)
    return ns["CustomTestCase"]
'

# ============================================================
# GATE: Syntax check
# ============================================================
# [pr_diff] (gate): Modified file must be valid Python
echo "=== GATE: Syntax check ==="
if ! python3 -c "import py_compile; py_compile.compile('$TARGET', doraise=True)" 2>/dev/null; then
    echo "GATE FAILED: test_utils.py has syntax errors"
    echo "0" > "$LOG_DIR/reward.txt"
    echo '{"reward": 0}' > "$LOG_DIR/reward.json"
    exit 0
fi
echo "GATE passed: syntax OK"
echo ""

# ============================================================
# GATE: Wrapping mechanism must still work
# ============================================================
# [pr_diff] (gate): tearDownClass must be called when setUpClass fails
# This is the core behavior of the wrapping mechanism. If __init_subclass__
# is deleted, this gate fails and the score is 0.
echo "=== GATE: Wrapping mechanism (tearDownClass on setUpClass failure) ==="
GATE_PASS=$(python3 -c "
$EXTRACT_HELPER

CTC = extract_custom_testcase('$TARGET')
if CTC is None:
    print('FAIL')
    raise SystemExit(0)

teardown_called = []

class GateTest(CTC):
    @classmethod
    def setUpClass(cls):
        raise RuntimeError('intentional failure')
    @classmethod
    def tearDownClass(cls):
        teardown_called.append(True)

try:
    GateTest.setUpClass()
except RuntimeError:
    pass

if teardown_called:
    print('PASS')
else:
    print('FAIL')
" 2>&1 | tail -1)

if [ "$GATE_PASS" != "PASS" ]; then
    echo "GATE FAILED: wrapping mechanism broken — tearDownClass not called on setUpClass failure"
    echo "0" > "$LOG_DIR/reward.txt"
    echo '{"reward": 0, "behavioral": 0, "regression": 0}' > "$LOG_DIR/reward.json"
    exit 0
fi
echo "GATE passed: wrapping mechanism works"
echo ""

# ============================================================
# Behavioral fail-to-pass tests (0.55 total)
# ============================================================
echo "=== Behavioral: fail-to-pass ==="

# [pr_diff] (0.30): dill can serialize a CustomTestCase subclass without circular ref error
echo "--- F2P: dill serialization of CustomTestCase subclass ---"
python3 -c "
$EXTRACT_HELPER
import dill

CTC = extract_custom_testcase('$TARGET')

class SerTest(CTC):
    @classmethod
    def setUpClass(cls):
        pass
    def test_example(self):
        pass

# The core bug: dill.dumps fails on classes related to wrapped subclasses
# because the bound method default parameter creates a reference cycle
class InnerClass:
    parent = SerTest

dill.dumps(InnerClass)
dill.dumps(SerTest)
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.30
    echo "PASS (0.30): [pr_diff] dill serialization of CustomTestCase subclass succeeds"
else
    echo "FAIL (0.30): [pr_diff] dill serialization of CustomTestCase subclass succeeds"
fi

# [pr_diff] (0.25): dill round-trip works (dumps + loads)
echo "--- F2P: dill round-trip serialization ---"
python3 -c "
$EXTRACT_HELPER
import dill

CTC = extract_custom_testcase('$TARGET')

class RoundTripTest(CTC):
    CLASS_VAR = 'hello'
    @classmethod
    def setUpClass(cls):
        pass
    def test_example(self):
        pass

# Full round-trip: serialize and deserialize
data = dill.dumps(RoundTripTest)
restored = dill.loads(data)
assert restored.CLASS_VAR == 'hello', f'Round-trip lost class var: {restored.CLASS_VAR}'
assert restored.__name__ == 'RoundTripTest', f'Round-trip lost name: {restored.__name__}'
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.25
    echo "PASS (0.25): [pr_diff] dill round-trip serialization works"
else
    echo "FAIL (0.25): [pr_diff] dill round-trip serialization works"
fi

echo ""

# ============================================================
# Behavioral pass-to-pass tests (0.35 total)
# ============================================================
echo "=== Behavioral: pass-to-pass ==="

# [pr_diff] (0.15): tearDownClass called when setUpClass fails (also gated above)
echo "--- P2P: tearDownClass on setUpClass failure ---"
python3 -c "
$EXTRACT_HELPER

CTC = extract_custom_testcase('$TARGET')

teardown_order = []

class TeardownTest(CTC):
    @classmethod
    def setUpClass(cls):
        raise ValueError('setup failed')
    @classmethod
    def tearDownClass(cls):
        teardown_order.append('teardown')

try:
    TeardownTest.setUpClass()
except ValueError:
    pass

assert teardown_order == ['teardown'], f'Expected teardown call, got: {teardown_order}'
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.15
    echo "PASS (0.15): [pr_diff] tearDownClass called when setUpClass fails"
else
    echo "FAIL (0.15): [pr_diff] tearDownClass called when setUpClass fails"
fi

# [pr_diff] (0.10): Normal setUpClass/tearDownClass flow works
echo "--- P2P: Normal setUp flow ---"
python3 -c "
$EXTRACT_HELPER

CTC = extract_custom_testcase('$TARGET')

class NormalTest(CTC):
    @classmethod
    def setUpClass(cls):
        cls.data = 42
    @classmethod
    def tearDownClass(cls):
        pass

NormalTest.setUpClass()
assert NormalTest.data == 42, f'setUpClass did not run correctly: {NormalTest.data}'
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.10
    echo "PASS (0.10): [pr_diff] Normal setUpClass/tearDownClass flow works"
else
    echo "FAIL (0.10): [pr_diff] Normal setUpClass/tearDownClass flow works"
fi

# [pr_diff] (0.10): Double-wrapping prevention — subclass of subclass doesn't wrap twice
echo "--- P2P: Double-wrapping prevention ---"
python3 -c "
$EXTRACT_HELPER

CTC = extract_custom_testcase('$TARGET')

call_count = []

class Parent(CTC):
    @classmethod
    def setUpClass(cls):
        call_count.append(1)
    @classmethod
    def tearDownClass(cls):
        pass

class Child(Parent):
    pass  # inherits setUpClass from Parent

# setUpClass should only run once, not be double-wrapped
Child.setUpClass()
assert len(call_count) == 1, f'setUpClass called {len(call_count)} times (double-wrapped?)'
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.10
    echo "PASS (0.10): [pr_diff] Double-wrapping prevention works"
else
    echo "FAIL (0.10): [pr_diff] Double-wrapping prevention works"
fi

echo ""

# ============================================================
# Anti-stub / structural (0.10 total)
# ============================================================
echo "=== Structural: anti-stub ==="

# [pr_diff] (0.05): _safe_setup_wrapped sentinel still set on wrapper
echo "--- Structural: sentinel attribute ---"
python3 -c "
$EXTRACT_HELPER

CTC = extract_custom_testcase('$TARGET')

class SentinelTest(CTC):
    @classmethod
    def setUpClass(cls):
        pass

func = SentinelTest.setUpClass
if hasattr(func, '__func__'):
    func = func.__func__
assert getattr(func, '_safe_setup_wrapped', False), '_safe_setup_wrapped not found on wrapper'
print('OK')
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.05
    echo "PASS (0.05): [pr_diff] _safe_setup_wrapped sentinel preserved"
else
    echo "FAIL (0.05): [pr_diff] _safe_setup_wrapped sentinel preserved"
fi

# [pr_diff] (0.05): __init_subclass__ hook exists with meaningful body
echo "--- Structural: __init_subclass__ exists ---"
python3 -c "
import ast

with open('$TARGET') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'CustomTestCase':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init_subclass__':
                # Must have more than just 'pass' or a docstring
                stmts = [s for s in item.body if not isinstance(s, (ast.Expr,)) or not isinstance(s.value, (ast.Constant, ast.Str))]
                assert len(stmts) >= 3, f'__init_subclass__ too shallow ({len(stmts)} stmts)'
                print('OK')
                raise SystemExit(0)
        print('FAIL: no __init_subclass__')
        raise SystemExit(1)
print('FAIL: no CustomTestCase')
raise SystemExit(1)
" 2>&1 | grep -q "OK"
if [ $? -eq 0 ]; then
    add 0.05
    echo "PASS (0.05): [pr_diff] __init_subclass__ exists with meaningful body"
else
    echo "FAIL (0.05): [pr_diff] __init_subclass__ exists with meaningful body"
fi

echo ""

# ============================================================
# Summary
# ============================================================
echo "=== Final Score ==="
echo "Score: $SCORE / 1.0"
echo "$SCORE" > "$LOG_DIR/reward.txt"

python3 -c "
import json
s = $SCORE
print(json.dumps({'reward': s, 'behavioral': min(s, 0.55), 'regression': min(max(s - 0.55, 0), 0.35), 'structural': min(max(s - 0.90, 0), 0.10)}))
" > "$LOG_DIR/reward.json" 2>/dev/null || echo "{\"reward\": $SCORE}" > "$LOG_DIR/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
