#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
EARNED=0.0

add() {
    EARNED=$(python3 -c "print($EARNED + $1)")
    TOTAL=$(python3 -c "print($TOTAL + $2)")
}

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (gate): gradio/utils.py must be valid Python
python3 -c "
import ast, sys
try:
    ast.parse(open('/repo/gradio/utils.py').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error in utils.py: {e}')
    sys.exit(1)
print('GATE PASS: utils.py syntax OK')
"
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

########################################
# Fail-to-pass: behavioral tests (0.45)
########################################

# [pr_diff] (0.25): get_type_hints returns {} for NameError (unresolvable forward ref)
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

# Function with forward ref that can't be resolved at runtime
def func_with_bad_forward_ref(x: str) -> 'NonExistentType':
    return x

try:
    result = get_type_hints(func_with_bad_forward_ref)
    assert result == {}, f'Expected empty dict, got {result}'
    print('PASS: NameError forward ref returns {}')
except NameError:
    print('FAIL: NameError was not caught')
    sys.exit(1)
except Exception as e:
    print(f'FAIL: unexpected error: {e}')
    sys.exit(1)
" && add 0.25 0.25 || add 0.0 0.25

# [pr_diff] (0.20): get_type_hints returns {} for TypeError (bad annotation)
python3 -c "
import sys, typing
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

# Create a function whose annotations trigger TypeError in typing.get_type_hints
class BadCallable:
    def __call__(self, x):
        return x
    __call__.__annotations__ = {'return': 42}  # int is not a valid type hint

# Verify this would raise TypeError with raw typing.get_type_hints
try:
    typing.get_type_hints(BadCallable().__call__)
    print('SKIP: TypeError not triggered on this Python version')
    sys.exit(0)
except TypeError:
    pass  # Good, confirmed it raises TypeError

try:
    result = get_type_hints(BadCallable())
    assert result == {}, f'Expected empty dict, got {result}'
    print('PASS: TypeError returns {}')
except TypeError:
    print('FAIL: TypeError was not caught')
    sys.exit(1)
" && add 0.20 0.20 || add 0.0 0.20

########################################
# Pass-to-pass: regression tests (0.45)
########################################

# [pr_diff] (0.20): get_type_hints returns correct hints for normal functions (anti-stub)
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

def normal_fn(x: str, y: int) -> float:
    return float(x) + y

hints = get_type_hints(normal_fn)
assert isinstance(hints, dict), f'Expected dict, got {type(hints)}'
assert len(hints) > 0, 'Expected non-empty hints for annotated function'
assert hints.get('x') is str, f'Expected str for x, got {hints.get(\"x\")}'
assert hints.get('y') is int, f'Expected int for y, got {hints.get(\"y\")}'
assert hints.get('return') is float, f'Expected float for return, got {hints.get(\"return\")}'
print('PASS: normal function type hints work')
" && add 0.20 0.20 || add 0.0 0.20

# [pr_diff] (0.15): get_type_hints works for callable objects with annotations (anti-stub)
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

class MyCallable:
    def __call__(self, x: str, y: int) -> bool:
        return len(x) > y

hints = get_type_hints(MyCallable())
assert isinstance(hints, dict), f'Expected dict, got {type(hints)}'
assert len(hints) > 0, 'Expected non-empty hints for annotated callable'
assert hints.get('x') is str, f'Expected str for x, got {hints.get(\"x\")}'
assert hints.get('y') is int, f'Expected int for y, got {hints.get(\"y\")}'
assert hints.get('return') is bool, f'Expected bool for return, got {hints.get(\"return\")}'
print('PASS: callable object type hints work')
" && add 0.15 0.15 || add 0.0 0.15

# [pr_diff] (0.05): get_type_hints returns {} for non-callable
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

result = get_type_hints('not_callable')
assert result == {}, f'Expected empty dict for non-callable, got {result}'
print('PASS: non-callable returns {}')
" && add 0.05 0.05 || add 0.0 0.05

# [pr_diff] (0.05): get_type_hints works for unannotated functions (returns empty dict)
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

def no_annotations(x, y):
    return x + y

hints = get_type_hints(no_annotations)
assert isinstance(hints, dict), f'Expected dict, got {type(hints)}'
assert len(hints) == 0, f'Expected empty hints for unannotated function, got {hints}'
print('PASS: unannotated function returns empty dict')
" && add 0.05 0.05 || add 0.0 0.05

########################################
# Config-derived checks (0.10)
########################################

# [agent_config] (0.05): "Be consistent with the style of the surrounding code" — AGENTS.md:45
# All return paths should return a dict (consistent with existing behavior)
python3 -c "
import sys
sys.path.insert(0, '/repo')
from gradio.utils import get_type_hints

# Verify all return paths produce dicts
def bad_ref(x: str) -> 'DoesNotExist':
    return x

for input_val, label in [
    (bad_ref, 'bad forward ref'),
    ('not_callable', 'non-callable'),
    (lambda x: x, 'lambda'),
]:
    try:
        result = get_type_hints(input_val)
        assert isinstance(result, dict), f'{label}: Expected dict, got {type(result)}'
    except (NameError, TypeError):
        print(f'FAIL: {label} raised an exception instead of returning dict')
        sys.exit(1)

print('PASS: all return paths return dict')
" && add 0.05 0.05 || add 0.0 0.05

# [agent_config] (0.05): "Python code is formatted with ruff" — AGENTS.md:43
# Verify modified function parses and exists
python3 -c "
import ast, sys
source = open('/repo/gradio/utils.py').read()
tree = ast.parse(source)
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_type_hints':
        found = True
        # Reject trivial stubs: must have at least 3 meaningful statements
        body_stmts = [s for s in node.body if not isinstance(s, (ast.Expr,)) or not isinstance(getattr(s, 'value', None), ast.Constant)]
        assert len(body_stmts) >= 3, f'Function body too simple ({len(body_stmts)} stmts) — likely a stub'
        break
assert found, 'get_type_hints function not found'
print('PASS: get_type_hints function exists and is non-trivial')
" && add 0.05 0.05 || add 0.0 0.05

########################################
# Compute final reward
########################################
REWARD=$(python3 -c "print(round($EARNED / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo "$REWARD" > /logs/verifier/reward.txt

# Build JSON breakdown
python3 -c "
import json
reward = $REWARD
earned = $EARNED
total = $TOTAL
behavioral = round(min(0.45, earned * 0.45 / total) if total > 0 else 0.0, 4)
regression = round(min(0.45, earned * 0.45 / total) if total > 0 else 0.0, 4)
config = round(min(0.10, earned * 0.10 / total) if total > 0 else 0.0, 4)
style_rubric = round(reward - behavioral - regression - config, 4)
print(json.dumps({
    'reward': reward,
    'behavioral': behavioral,
    'regression': regression,
    'config': config,
    'style_rubric': max(0.0, style_rubric)
}))
" > /logs/verifier/reward.json

echo "Final reward: $REWARD (earned $EARNED / $TOTAL)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
