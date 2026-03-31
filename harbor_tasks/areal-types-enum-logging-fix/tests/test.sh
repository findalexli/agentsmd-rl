#!/usr/bin/env bash
set +e

REPO="/workspace/AReaL"
REWARD=0

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (gate): Both modified files must parse
python3 -c "
import ast, sys
for f in ['areal/experimental/openai/types.py', 'areal/reward/clevr_count_70k.py']:
    try:
        ast.parse(open('$REPO/' + f).read())
    except SyntaxError as e:
        print(f'GATE FAIL: {f}: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE PASS: syntax OK', file=sys.stderr)
"
if [ $? -ne 0 ]; then
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward": 0.0}' > "/logs/verifier/reward.json"
    exit 0
fi

########################################
# F2P-BEHAVIORAL (0.25): Reward function returns float, not int
########################################
# [pr_diff] (0.25): Buggy code returns int 0/1; fix returns float 0.0/1.0
python3 -c "
import sys, re
src = open('$REPO/areal/reward/clevr_count_70k.py').read()

# Mock areal.utils.logging to avoid heavy imports
mock_logging = '''
import logging as _stdlib_logging
class _MockLogging:
    @staticmethod
    def getLogger(name):
        return _stdlib_logging.getLogger(name)
logging = _MockLogging()
'''
modified = src.replace('from areal.utils import logging', mock_logging)
# Also handle 'from areal.utils.logging import' variant
if 'from areal.utils import logging' not in src:
    modified = mock_logging + '\n' + src

ns = {'re': re, '__builtins__': __builtins__}
try:
    exec(compile(modified, '<clevr>', 'exec'), ns)
except Exception as e:
    print(f'FAIL: could not exec module: {e}', file=sys.stderr)
    sys.exit(1)

fn = ns.get('clevr_count_70k_reward_fn')
if fn is None:
    print('FAIL: clevr_count_70k_reward_fn not found', file=sys.stderr)
    sys.exit(1)

# Correct answer
r1 = fn('prompt', 'the answer is [42]', [], [], '42')
if not isinstance(r1, float):
    print(f'FAIL: correct answer returned {type(r1).__name__}, expected float', file=sys.stderr)
    sys.exit(1)
if r1 != 1.0:
    print(f'FAIL: correct answer returned {r1}, expected 1.0', file=sys.stderr)
    sys.exit(1)

# Wrong answer
r2 = fn('prompt', 'the answer is [99]', [], [], '42')
if not isinstance(r2, float):
    print(f'FAIL: wrong answer returned {type(r2).__name__}, expected float', file=sys.stderr)
    sys.exit(1)
if r2 != 0.0:
    print(f'FAIL: wrong answer returned {r2}, expected 0.0', file=sys.stderr)
    sys.exit(1)

# No match
r3 = fn('prompt', 'no brackets here', [], [], '42')
if not isinstance(r3, float):
    print(f'FAIL: no-match returned {type(r3).__name__}, expected float', file=sys.stderr)
    sys.exit(1)
if r3 != 0.0:
    print(f'FAIL: no-match returned {r3}, expected 0.0', file=sys.stderr)
    sys.exit(1)

print('PASS: reward function returns correct float values', file=sys.stderr)
" 2>/dev/null && add 0.25 || true

########################################
# F2P-BEHAVIORAL (0.20): Enum classes exist with correct values
########################################
# [pr_diff] (0.20): Buggy code has no enum classes; fix adds ApiType and InputName
# AST extraction + exec: extracts classes, instantiates, checks members
python3 -c "
import ast, sys, textwrap
from enum import Enum

src = open('$REPO/areal/experimental/openai/types.py').read()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

# Collect all imports and enum-like class definitions
# Include any 'from enum import ...' or 'import enum' at the top
code_parts = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        chunk = ''.join(lines[node.lineno-1:node.end_lineno])
        # Skip heavy imports (torch, openai, areal) and __future__
        if any(kw in chunk for kw in ['torch', 'openai', 'areal', '__future__']):
            continue
        code_parts.append(chunk)
    elif isinstance(node, ast.ClassDef) and node.name in ('ApiType', 'InputName'):
        chunk = ''.join(lines[node.lineno-1:node.end_lineno])
        code_parts.append(chunk)

# Also ensure enum import is present
extracted = '\n'.join(code_parts)
if 'from enum import' not in extracted and 'import enum' not in extracted:
    extracted = 'from enum import Enum, StrEnum\n' + extracted

# Add StrEnum fallback for older Python
if 'StrEnum' not in extracted:
    extracted = 'try:\n    from enum import StrEnum\nexcept ImportError:\n    pass\n' + extracted

ns = {'__builtins__': __builtins__}
try:
    exec(extracted, ns)
except Exception as e:
    print(f'FAIL: could not exec enums: {e}', file=sys.stderr)
    sys.exit(1)

ApiType = ns.get('ApiType')
InputName = ns.get('InputName')

if ApiType is None:
    print('FAIL: ApiType class not found', file=sys.stderr)
    sys.exit(1)
if InputName is None:
    print('FAIL: InputName class not found', file=sys.stderr)
    sys.exit(1)

# Must be Enum subclass
if not issubclass(ApiType, Enum):
    print('FAIL: ApiType does not inherit from Enum', file=sys.stderr)
    sys.exit(1)
if not issubclass(InputName, Enum):
    print('FAIL: InputName does not inherit from Enum', file=sys.stderr)
    sys.exit(1)

# Must be str-compatible (str mixin or StrEnum) for backward compat
if not issubclass(ApiType, str):
    print('FAIL: ApiType is not str-compatible (need str,Enum or StrEnum)', file=sys.stderr)
    sys.exit(1)
if not issubclass(InputName, str):
    print('FAIL: InputName is not str-compatible', file=sys.stderr)
    sys.exit(1)

# Must have at least 2 members (anti-stub)
if len(ApiType) < 2:
    print(f'FAIL: ApiType has only {len(ApiType)} members (need >=2)', file=sys.stderr)
    sys.exit(1)
if len(InputName) < 2:
    print(f'FAIL: InputName has only {len(InputName)} members (need >=2)', file=sys.stderr)
    sys.exit(1)

# Must have the expected string values (behavioral: backward compat with old code)
api_values = {m.value for m in ApiType}
input_values = {m.value for m in InputName}

if 'completion' not in api_values:
    print('FAIL: ApiType missing \"completion\" value', file=sys.stderr)
    sys.exit(1)
if 'response' not in api_values:
    print('FAIL: ApiType missing \"response\" value', file=sys.stderr)
    sys.exit(1)
if 'messages' not in input_values:
    print('FAIL: InputName missing \"messages\" value', file=sys.stderr)
    sys.exit(1)
if 'input_data' not in input_values:
    print('FAIL: InputName missing \"input_data\" value', file=sys.stderr)
    sys.exit(1)

# str(enum_member) == value for backward compat
for m in ApiType:
    if str(m) != m.value:
        print(f'FAIL: str(ApiType.{m.name}) != \"{m.value}\"', file=sys.stderr)
        sys.exit(1)

print('PASS: enum classes have correct types and values', file=sys.stderr)
" 2>/dev/null && add 0.20 || true

########################################
# F2P-BEHAVIORAL (0.15): No bare print() in clevr, uses logger
########################################
# [pr_diff] (0.15): Buggy code has print() in reward fn; fix replaces with logger
python3 -c "
import ast, sys

tree = ast.parse(open('$REPO/areal/reward/clevr_count_70k.py').read())
src = open('$REPO/areal/reward/clevr_count_70k.py').read()

# Check no bare print() calls via AST
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == 'print':
            print('FAIL: bare print() found in clevr_count_70k.py', file=sys.stderr)
            sys.exit(1)

# Verify some form of logger usage exists (flexible: logger.X, logging.X, log.X)
import re
if not re.search(r'\b(logger|log|logging)\.\s*(info|debug|warning|error|critical)\b', src):
    print('FAIL: no logger/logging call found', file=sys.stderr)
    sys.exit(1)

print('PASS: no bare print, uses logging', file=sys.stderr)
" 2>/dev/null && add 0.15 || true

########################################
# F2P-STRUCTURAL (0.10): Space in log message
########################################
# [pr_diff] (0.10): Implicit string concat bug — "properly." must have space before "Ignoring"
# AST justified: to_tensor_dict method requires torch tensors, cannot call
python3 -c "
import ast, sys

src = open('$REPO/areal/experimental/openai/types.py').read()
tree = ast.parse(src)

# Find string literals inside logger.warning() calls within to_tensor_dict
# Check that no string literal ends with 'properly.\"' immediately before another
# string that starts with a capital letter (the implicit concat bug)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'to_tensor_dict':
        func_src = ast.get_source_segment(src, node) or ''
        # The bug is implicit string concat producing 'properly.Ignoring'
        # Check that the rendered log message doesn't have this pattern
        if 'properly.\"' in func_src or \"properly.'\" in func_src:
            # Found the raw buggy pattern — check if space was added
            if 'properly. ' not in func_src and 'properly.\" ' not in func_src and \"properly.' \" not in func_src:
                print('FAIL: missing space bug still present in to_tensor_dict', file=sys.stderr)
                sys.exit(1)
        # If 'properly.' not in func_src, the message was restructured — OK
        break
else:
    # to_tensor_dict not found — accept if message was rewritten elsewhere
    pass

print('PASS: space fix applied or message restructured', file=sys.stderr)
" 2>/dev/null && add 0.10 || true

########################################
# P2P-BEHAVIORAL (0.10): extract_answer still works correctly
########################################
# [pr_diff] (0.10): extract_answer must still parse bracketed numbers
python3 -c "
import sys, re
src = open('$REPO/areal/reward/clevr_count_70k.py').read()

mock_logging = '''
import logging as _stdlib_logging
class _MockLogging:
    @staticmethod
    def getLogger(name):
        return _stdlib_logging.getLogger(name)
logging = _MockLogging()
'''
modified = src.replace('from areal.utils import logging', mock_logging)
if 'from areal.utils import logging' not in src:
    modified = mock_logging + '\n' + src

ns = {'re': re, '__builtins__': __builtins__}
try:
    exec(compile(modified, '<clevr>', 'exec'), ns)
except Exception:
    sys.exit(1)

fn = ns.get('extract_answer')
if fn is None:
    print('FAIL: extract_answer not found', file=sys.stderr)
    sys.exit(1)

assert fn('[42]', '') == '42', 'single number extraction failed'
assert fn('text [1.5] more [2.0]', '') == '2.0', 'last-match extraction failed'
assert fn('no brackets here', '') == '', 'no-match should return empty'
print('PASS: extract_answer works correctly', file=sys.stderr)
" 2>/dev/null && add 0.10 || true

########################################
# P2P-BEHAVIORAL (0.10): Reward fn edge cases
########################################
# [pr_diff] (0.10): reward fn handles None answer and whitespace
python3 -c "
import sys, re
src = open('$REPO/areal/reward/clevr_count_70k.py').read()

mock_logging = '''
import logging as _stdlib_logging
class _MockLogging:
    @staticmethod
    def getLogger(name):
        return _stdlib_logging.getLogger(name)
logging = _MockLogging()
'''
modified = src.replace('from areal.utils import logging', mock_logging)
if 'from areal.utils import logging' not in src:
    modified = mock_logging + '\n' + src

ns = {'re': re, '__builtins__': __builtins__}
try:
    exec(compile(modified, '<clevr>', 'exec'), ns)
except Exception:
    sys.exit(1)

fn = ns.get('clevr_count_70k_reward_fn')
if fn is None:
    sys.exit(1)

# None answer should return 0
r = fn('p', '[42]', [], [], None)
assert isinstance(r, float) and r == 0.0, f'None answer should return float 0.0, got {r!r}'

# Whitespace-padded answer still matches
r2 = fn('p', '[ 5 ]', [], [], '5')
# This may or may not match depending on regex — just check it returns a number
assert isinstance(r2, (int, float)), f'Expected numeric, got {type(r2).__name__}'

print('PASS: edge cases handled', file=sys.stderr)
" 2>/dev/null && add 0.10 || true

########################################
# CONFIG (0.10): getLogger with PascalCase name
########################################
# [agent_config] (0.10): "Use areal.utils.logging.getLogger(name) with PascalCase" — .claude/rules/code-style.md:16-17 @ 4f5a294
python3 -c "
import ast, sys

tree = ast.parse(open('$REPO/areal/reward/clevr_count_70k.py').read())

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'getLogger':
        if node.args:
            arg = node.args[0]
            # Accept string constant
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                name = arg.value
                if name and name[0].isupper():
                    found = True
                    break
                else:
                    print(f'FAIL: getLogger(\"{name}\") is not PascalCase', file=sys.stderr)
                    sys.exit(1)
            # Also accept variable reference (flexible)
            elif isinstance(arg, ast.Name):
                found = True
                break

if not found:
    print('FAIL: no getLogger call found', file=sys.stderr)
    sys.exit(1)

print('PASS: getLogger uses PascalCase name', file=sys.stderr)
" 2>/dev/null && add 0.10 || true

########################################
# Final score
########################################
echo "Total: $REWARD / 1.0" >&2
echo "$REWARD" > "/logs/verifier/reward.txt"

# Build reward.json with category breakdown
python3 -c "
import json
score = $REWARD
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.80), 4),
    'config': round(min(max(score - 0.90, 0), 0.10), 4)
}))
" > "/logs/verifier/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
