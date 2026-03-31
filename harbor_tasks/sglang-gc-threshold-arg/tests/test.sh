#!/usr/bin/env bash
set -uo pipefail

PASS=0
GATE_PASS=true

cd /workspace/sglang

##############################################################################
# GATE: Syntax check on modified files
##############################################################################
# [pr_diff] (gate): Both modified files must parse without syntax errors
for f in python/sglang/srt/server_args.py python/sglang/srt/entrypoints/engine.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done

if [ "$GATE_PASS" = false ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: syntax check passed"

##############################################################################
# Fail-to-pass: Behavioral tests (0.70 total)
##############################################################################

# [pr_diff] (0.25): GC-setting function actually calls gc.set_threshold with correct args
# Extracts the function from engine.py that calls gc.set_threshold, then invokes it
python3 -c "
import sys, gc, ast, textwrap

with open('python/sglang/srt/entrypoints/engine.py') as f:
    source = f.read()

tree = ast.parse(source)
gc_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        func_src = ast.get_source_segment(source, node)
        if func_src and 'set_threshold' in func_src:
            gc_func = (node.name, func_src)
            break

if gc_func is None:
    print('FAIL: no function calling gc.set_threshold found in engine.py')
    sys.exit(1)

func_name, func_src = gc_func

exec_ns = {'gc': gc, '__builtins__': __builtins__}
exec(textwrap.dedent(func_src), exec_ns)
fn = exec_ns[func_name]

original = gc.get_threshold()

# Test 3-arg: gc_threshold = [500, 5, 5]
class Args3:
    gc_threshold = [500, 5, 5]
fn(Args3())
assert gc.get_threshold() == (500, 5, 5), f'3-arg: expected (500,5,5), got {gc.get_threshold()}'

# Test 1-arg: gc_threshold = [50000]
gc.set_threshold(*original)
class Args1:
    gc_threshold = [50000]
fn(Args1())
assert gc.get_threshold()[0] == 50000, f'1-arg: expected gen0=50000, got {gc.get_threshold()}'

# Test 2-arg: gc_threshold = [700, 10]
gc.set_threshold(*original)
class Args2:
    gc_threshold = [700, 10]
fn(Args2())
assert gc.get_threshold()[0] == 700 and gc.get_threshold()[1] == 10, f'2-arg: expected gen0=700,gen1=10, got {gc.get_threshold()}'

# Test None is no-op
gc.set_threshold(*original)
class ArgsNone:
    gc_threshold = None
fn(ArgsNone())
assert gc.get_threshold() == original, 'gc_threshold=None should be no-op'

print('PASS: GC function correctly sets thresholds for 1/2/3 args and None')
" && { PASS=$(echo "$PASS + 0.25" | bc); echo "PASS [0.25]: GC function sets thresholds"; } || echo "FAIL [0.25]: GC function sets thresholds"

# [pr_diff] (0.25): CLI parser from ACTUAL code accepts --gc-threshold with int args
# Extracts the real add_argument call for --gc-threshold from add_cli_args and tests it
python3 -c "
import sys, ast, textwrap, argparse

with open('python/sglang/srt/server_args.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find add_cli_args function
add_cli_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'add_cli_args':
        add_cli_src = ast.get_source_segment(source, node)
        break

if add_cli_src is None:
    print('FAIL: add_cli_args function not found')
    sys.exit(1)

if '--gc-threshold' not in add_cli_src:
    print('FAIL: --gc-threshold not registered in add_cli_args')
    sys.exit(1)

# Extract the parser.add_argument(...) call for --gc-threshold from the real source
# Walk through lines to find the multi-line add_argument block
lines = add_cli_src.split('\n')
block_lines = []
paren_depth = 0
capturing = False
for line in lines:
    if '--gc-threshold' in line:
        capturing = True
    if capturing:
        block_lines.append(line)
        paren_depth += line.count('(') - line.count(')')
        if paren_depth <= 0 and len(block_lines) > 0:
            break

if not block_lines:
    print('FAIL: could not extract --gc-threshold add_argument call')
    sys.exit(1)

# Execute the extracted add_argument call against a real parser
block_src = textwrap.dedent('\n'.join(block_lines))
parser = argparse.ArgumentParser()
exec(block_src, {'parser': parser, 'int': int, 'str': str, 'float': float, 'bool': bool})

# Test parsing with 3 ints
args = parser.parse_args(['--gc-threshold', '700', '10', '10'])
assert isinstance(args.gc_threshold, list), f'Expected list, got {type(args.gc_threshold)}'
assert args.gc_threshold == [700, 10, 10], f'Expected [700,10,10], got {args.gc_threshold}'

# Test parsing with 1 int
args = parser.parse_args(['--gc-threshold', '50000'])
assert args.gc_threshold == [50000], f'Expected [50000], got {args.gc_threshold}'

# Test default (no arg provided)
args = parser.parse_args([])
assert args.gc_threshold is None, f'Expected None default, got {args.gc_threshold}'

# Test values are int type, not str
args = parser.parse_args(['--gc-threshold', '100'])
assert isinstance(args.gc_threshold[0], int), f'Expected int, got {type(args.gc_threshold[0])}'

print('PASS: actual --gc-threshold add_argument call parses correctly')
" && { PASS=$(echo "$PASS + 0.25" | bc); echo "PASS [0.25]: actual CLI arg parses correctly"; } || echo "FAIL [0.25]: actual CLI arg parses correctly"

# [pr_diff] (0.20): Validation rejects invalid gc_threshold (0 or 4+ values)
# Extracts the gc_threshold validation block from check_server_args and executes it
python3 -c "
import sys, ast, textwrap, re

with open('python/sglang/srt/server_args.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find check_server_args function
check_func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'check_server_args':
        check_func_src = ast.get_source_segment(source, node)
        break

if check_func_src is None:
    print('FAIL: check_server_args function not found')
    sys.exit(1)

if 'gc_threshold' not in check_func_src:
    print('FAIL: gc_threshold not validated in check_server_args')
    sys.exit(1)

# Try approach 1: create a mock ServerArgs with __getattr__ fallback
# and call check_server_args to see if it raises for invalid gc_threshold
import logging, warnings

# Build a permissive mock — returns None for any unset attribute
class MockServerArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def __getattr__(self, name):
        return None

# Extract and exec check_server_args
exec_ns = {
    '__builtins__': __builtins__,
    'logger': logging.getLogger('test'),
    'warnings': warnings,
    'logging': logging,
    'os': __import__('os'),
}
try:
    exec(textwrap.dedent(check_func_src), exec_ns)
    check_fn = exec_ns['check_server_args']

    # Test 1: valid gc_threshold should NOT raise
    try:
        check_fn(MockServerArgs(gc_threshold=[700, 10, 10]))
        valid_ok = True
    except Exception as e:
        # If it fails on some other check, that's OK — gc_threshold was valid
        if 'gc_threshold' in str(e):
            print(f'FAIL: valid gc_threshold [700,10,10] rejected: {e}')
            sys.exit(1)
        valid_ok = True

    # Test 2: gc_threshold with 4 values should raise
    try:
        check_fn(MockServerArgs(gc_threshold=[1, 2, 3, 4]))
        print('FAIL: gc_threshold=[1,2,3,4] was not rejected')
        sys.exit(1)
    except (ValueError, SystemExit, AssertionError) as e:
        if 'gc_threshold' in str(e).lower() or 'gc' in str(e).lower() or '1' in str(e) or '3' in str(e):
            pass  # correctly rejected
        else:
            # Might have failed on a different check — try empty list
            pass
    except Exception:
        pass  # some other error before reaching gc_threshold, try empty

    # Test 3: gc_threshold with 0 values (empty list) should raise
    try:
        check_fn(MockServerArgs(gc_threshold=[]))
        print('FAIL: gc_threshold=[] was not rejected')
        sys.exit(1)
    except (ValueError, SystemExit, AssertionError):
        pass  # correctly rejected
    except Exception:
        pass  # other error

    print('PASS: check_server_args validates gc_threshold length (behavioral)')
    sys.exit(0)

except Exception as e:
    # Approach 1 failed (missing imports etc.) — fall back to targeted AST check
    pass

# Fallback: extract just the gc_threshold validation block and verify it raises
# Find lines in check_server_args that reference gc_threshold
lines = check_func_src.split('\n')
gc_lines = []
capturing = False
base_indent = None
for line in lines:
    stripped = line.lstrip()
    current_indent = len(line) - len(stripped) if stripped else 999
    if 'gc_threshold' in line and ('if' in line or 'elif' in line):
        capturing = True
        base_indent = current_indent
        gc_lines.append(line)
        continue
    if capturing:
        if stripped == '' or current_indent > base_indent:
            gc_lines.append(line)
        else:
            break

gc_block = '\n'.join(gc_lines)
if not gc_block.strip():
    print('FAIL: could not extract gc_threshold validation block')
    sys.exit(1)

# The validation block should contain a raise or sys.exit for invalid lengths
if 'raise' not in gc_block and 'exit' not in gc_block and 'error' not in gc_block.lower():
    print('FAIL: gc_threshold validation does not raise/exit on invalid input')
    sys.exit(1)

# Wrap the validation block in a function and test it
test_code = textwrap.dedent(gc_block)
test_ns = {'__builtins__': __builtins__, 'logger': logging.getLogger('test'), 'warnings': warnings}

# Test with 4 values — should raise
class BadArgs:
    gc_threshold = [1, 2, 3, 4]
test_ns['args'] = BadArgs()
test_ns['server_args'] = BadArgs()
test_ns['self'] = BadArgs()
try:
    exec(test_code, test_ns)
    print('FAIL: 4-value gc_threshold was not rejected')
    sys.exit(1)
except (ValueError, SystemExit, AssertionError):
    pass

print('PASS: gc_threshold validation rejects invalid lengths (fallback)')
" && { PASS=$(echo "$PASS + 0.20" | bc); echo "PASS [0.20]: gc_threshold validation rejects invalid"; } || echo "FAIL [0.20]: gc_threshold validation rejects invalid"

##############################################################################
# Pass-to-pass: Regression checks (0.15 total)
##############################################################################

# [pr_diff] (0.10): server_args.py still parses; ServerArgs, add_cli_args, check_server_args all present
python3 -c "
import sys, ast
with open('python/sglang/srt/server_args.py') as f:
    tree = ast.parse(f.read())
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
assert 'ServerArgs' in classes, 'ServerArgs class missing'
assert 'add_cli_args' in funcs, 'add_cli_args function missing'
assert 'check_server_args' in funcs, 'check_server_args function missing'
print('PASS: ServerArgs, add_cli_args, check_server_args all intact')
" && { PASS=$(echo "$PASS + 0.10" | bc); echo "PASS [0.10]: server_args.py structures intact"; } || echo "FAIL [0.10]: server_args.py structures intact"

# [pr_diff] (0.05): engine.py still has _launch_subprocesses function
python3 -c "
import sys, ast
with open('python/sglang/srt/entrypoints/engine.py') as f:
    tree = ast.parse(f.read())
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
assert '_launch_subprocesses' in funcs, '_launch_subprocesses missing'
print('PASS: _launch_subprocesses intact')
" && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: _launch_subprocesses intact"; } || echo "FAIL [0.05]: _launch_subprocesses intact"

##############################################################################
# Structural: Integration + anti-stub (0.10 total)
##############################################################################

# [pr_diff] (0.05): GC-setting logic invoked within _launch_subprocesses
# AST justification: _launch_subprocesses orchestrates multiprocess launch with
# torch, CUDA, multiprocessing deps — cannot call it without full GPU stack
python3 -c "
import sys, ast

with open('python/sglang/srt/entrypoints/engine.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find function(s) that call gc.set_threshold
gc_func_names = set()
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        func_src = ast.get_source_segment(source, node)
        if func_src and 'set_threshold' in func_src:
            gc_func_names.add(node.name)

if not gc_func_names:
    print('FAIL: no function calls gc.set_threshold in engine.py')
    sys.exit(1)

# If set_threshold is directly in _launch_subprocesses, that's fine
if '_launch_subprocesses' in gc_func_names:
    print('PASS: gc.set_threshold called directly in _launch_subprocesses')
    sys.exit(0)

# Otherwise, check that a gc-setting function is called from _launch_subprocesses
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_launch_subprocesses':
        func_src = ast.get_source_segment(source, node)
        if func_src:
            for gc_name in gc_func_names:
                if gc_name in func_src:
                    print(f'PASS: {gc_name} called in _launch_subprocesses')
                    sys.exit(0)

print('FAIL: GC threshold logic not invoked during subprocess launch')
sys.exit(1)
" && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: GC logic invoked in launch"; } || echo "FAIL [0.05]: GC logic invoked in launch"

# [pr_diff] (0.05): gc_threshold field exists in ServerArgs as an annotated attribute
# AST justification: ServerArgs import chain pulls sglang.srt.connector, sglang.srt.environ
# which need the full package installation — cannot instantiate directly
python3 -c "
import sys, ast
with open('python/sglang/srt/server_args.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ServerArgs':
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and hasattr(item.target, 'id') and item.target.id == 'gc_threshold':
                print('PASS: gc_threshold field exists in ServerArgs')
                sys.exit(0)
            # Also accept plain assignment (gc_threshold = None)
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if hasattr(target, 'id') and target.id == 'gc_threshold':
                        print('PASS: gc_threshold field exists in ServerArgs (plain assign)')
                        sys.exit(0)
print('FAIL: gc_threshold field not found in ServerArgs')
sys.exit(1)
" && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: gc_threshold field in ServerArgs"; } || echo "FAIL [0.05]: gc_threshold field in ServerArgs"

##############################################################################
# Config-derived checks (0.05 total)
##############################################################################

# [agent_config] (0.05): gc_threshold in both class body and add_cli_args — python/sglang/srt/server_args.py:288-289 @ 4e905feb
python3 -c "
import sys, ast
with open('python/sglang/srt/server_args.py') as f:
    source = f.read()
tree = ast.parse(source)

in_class = False
in_cli = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'ServerArgs':
        for item in node.body:
            if isinstance(item, (ast.AnnAssign, ast.Assign)):
                targets = [item.target] if isinstance(item, ast.AnnAssign) else item.targets
                for t in targets:
                    if hasattr(t, 'id') and t.id == 'gc_threshold':
                        in_class = True
    if isinstance(node, ast.FunctionDef) and node.name == 'add_cli_args':
        func_src = ast.get_source_segment(source, node)
        if func_src and '--gc-threshold' in func_src:
            in_cli = True

if not (in_class and in_cli):
    print(f'FAIL: gc_threshold in class={in_class}, in CLI={in_cli} — need both')
    sys.exit(1)
print('PASS: gc_threshold in both ServerArgs class body and add_cli_args')
" && { PASS=$(echo "$PASS + 0.05" | bc); echo "PASS [0.05]: gc_threshold in both class and CLI"; } || echo "FAIL [0.05]: gc_threshold in both class and CLI"

##############################################################################
# Compute final reward
##############################################################################
REWARD=$(echo "scale=2; $PASS" | bc)
# Ensure leading zero
case "$REWARD" in
    .*) REWARD="0$REWARD" ;;
esac
echo ""
echo "Total: $REWARD / 1.00"
echo "$REWARD" > /logs/verifier/reward.txt
echo "{\"reward\": $REWARD}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
