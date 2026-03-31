#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
TARGET="/workspace/sglang/python/sglang/srt/models/qwen3_next.py"
REWARD_JSON="{}"

add_score() {
    TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))")
    REWARD_JSON=$(python3 -c "
import json
d = json.loads('$REWARD_JSON')
d['$2'] = d.get('$2', 0) + $1
print(json.dumps(d))
")
}

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if ! python3 -c "
import ast, sys
with open('$TARGET') as f:
    try:
        ast.parse(f.read())
        sys.exit(0)
    except SyntaxError as e:
        print(f'SyntaxError: {e}')
        sys.exit(1)
"; then
    echo "GATE FAILED: syntax error in $TARGET"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"

echo ""
echo "=== Behavioral: _override_weight_loader handles property-backed params ==="
# [pr_diff] (0.30): Fix must handle ModelWeightParameter with read-only weight_loader property
if python3 -c "
import ast, types, sys

# Extract _override_weight_loader from the source
with open('$TARGET') as f:
    tree = ast.parse(f.read())

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_override_weight_loader':
        import textwrap
        lines = open('$TARGET').readlines()
        func_lines = lines[node.lineno - 1 : node.end_lineno]
        func_src = textwrap.dedent(''.join(func_lines))
        break

if func_src is None:
    print('FAIL: _override_weight_loader not found')
    sys.exit(1)

# Compile and extract the function
ns = {}
exec(func_src, ns)
override = ns['_override_weight_loader']

# Simulate a ModelWeightParameter (property-backed weight_loader)
class FakeQuantizedParam:
    def __init__(self):
        self._weight_loader = 'original'
    @property
    def weight_loader(self):
        return self._weight_loader

class FakeModule:
    def __init__(self):
        self.weight = FakeQuantizedParam()

m = FakeModule()
new_loader = lambda p, w, s=None: None
override(m, new_loader)

assert m.weight._weight_loader is new_loader, 'Expected _weight_loader to be set'
assert m.weight.weight_loader is new_loader, 'Expected weight_loader property to return new loader'
print('PASS')
" 2>&1; then
    add_score 0.30 "behavioral"
    echo "SCORE: +0.30"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: _override_weight_loader handles plain attribute params ==="
# [pr_diff] (0.20): Fix must also handle non-quantized plain attribute weight_loader
if python3 -c "
import ast, types, sys

with open('$TARGET') as f:
    tree = ast.parse(f.read())

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_override_weight_loader':
        import textwrap
        lines = open('$TARGET').readlines()
        func_lines = lines[node.lineno - 1 : node.end_lineno]
        func_src = textwrap.dedent(''.join(func_lines))
        break

if func_src is None:
    print('FAIL: _override_weight_loader not found')
    sys.exit(1)

ns = {}
exec(func_src, ns)
override = ns['_override_weight_loader']

# Simulate a plain parameter (non-quantized, no _weight_loader)
class FakePlainParam:
    def __init__(self):
        self.weight_loader = 'original'

class FakeModule:
    def __init__(self):
        self.weight = FakePlainParam()

m = FakeModule()
new_loader = lambda p, w, s=None: None
override(m, new_loader)

assert m.weight.weight_loader is new_loader, 'Expected weight_loader to be updated'
print('PASS')
" 2>&1; then
    add_score 0.20 "behavioral"
    echo "SCORE: +0.20"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: Direct assignment to property-backed weight_loader raises error ==="
# [pr_diff] (0.15): Buggy direct assignment must fail on property-backed params
if python3 -c "
import sys

# Prove that the bug existed: direct assignment to a read-only property fails
class FakeQuantizedParam:
    def __init__(self):
        self._weight_loader = 'original'
    @property
    def weight_loader(self):
        return self._weight_loader

param = FakeQuantizedParam()
try:
    param.weight_loader = 'new_value'
    print('FAIL: Expected AttributeError was not raised')
    sys.exit(1)
except AttributeError:
    print('PASS: Direct assignment correctly raises AttributeError')
" 2>&1; then
    add_score 0.15 "behavioral"
    echo "SCORE: +0.15"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Behavioral: __init__ uses _override_weight_loader for both projections ==="
# [pr_diff] (0.10): Both in_proj_qkvz and in_proj_ba must use the override helper
if python3 -c "
import ast, sys

with open('$TARGET') as f:
    source = f.read()
    tree = ast.parse(source)

# Find Qwen3GatedDeltaNet.__init__
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Qwen3GatedDeltaNet':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_src = ast.get_source_segment(source, item)
                # Check that _override_weight_loader is called for both projections
                count = init_src.count('_override_weight_loader')
                if count >= 2:
                    print(f'PASS: _override_weight_loader called {count} times in __init__')
                    sys.exit(0)
                else:
                    print(f'FAIL: _override_weight_loader called only {count} times')
                    sys.exit(1)

print('FAIL: Could not find Qwen3GatedDeltaNet.__init__')
sys.exit(1)
" 2>&1; then
    add_score 0.10 "behavioral"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Regression: _make_packed_weight_loader still exists ==="
# [pr_diff] (0.10): Existing packed weight loader must be preserved
if python3 -c "
import ast, sys

with open('$TARGET') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_make_packed_weight_loader':
        print('PASS: _make_packed_weight_loader found')
        sys.exit(0)

print('FAIL: _make_packed_weight_loader not found')
sys.exit(1)
" 2>&1; then
    add_score 0.10 "regression"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Structural: No direct .weight.weight_loader assignment in __init__ ==="
# [pr_diff] (0.10): Buggy direct assignment pattern must be removed
if python3 -c "
import ast, sys

with open('$TARGET') as f:
    source = f.read()
    tree = ast.parse(source)

# Find Qwen3GatedDeltaNet.__init__ and check for direct weight_loader assignment
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Qwen3GatedDeltaNet':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for child in ast.walk(item):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Attribute) and target.attr == 'weight_loader':
                                # Check if it's self.xxx.weight.weight_loader = ...
                                if isinstance(target.value, ast.Attribute) and target.value.attr == 'weight':
                                    print('FAIL: Direct .weight.weight_loader assignment found in __init__')
                                    sys.exit(1)
                print('PASS: No direct .weight.weight_loader assignment')
                sys.exit(0)

print('FAIL: Could not find Qwen3GatedDeltaNet.__init__')
sys.exit(1)
" 2>&1; then
    add_score 0.10 "structural"
    echo "SCORE: +0.10"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== Structural: Anti-stub check ==="
# [static] (0.05): File must not be stubbed out or emptied
if python3 -c "
import os, sys
size = os.path.getsize('$TARGET')
if size < 5000:
    print(f'FAIL: File suspiciously small ({size} bytes)')
    sys.exit(1)
print(f'PASS: File size {size} bytes')
" 2>&1; then
    add_score 0.05 "structural"
    echo "SCORE: +0.05"
else
    echo "SCORE: +0.00"
fi

echo ""
echo "=== TOTAL: $TOTAL ==="

# Write final reward
echo "$TOTAL" > /logs/verifier/reward.txt
REWARD_JSON=$(python3 -c "
import json
d = json.loads('$REWARD_JSON')
d['reward'] = $TOTAL
print(json.dumps(d))
")
echo "$REWARD_JSON" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
