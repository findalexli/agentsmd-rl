#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=100
TARGET="python/sglang/multimodal_gen/runtime/loader/fsdp_load.py"

cd /workspace/sglang

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): File must be valid Python
if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$TARGET').read())
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"; then
    echo "FAIL: syntax error — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "PASS: syntax OK"

echo ""
echo "=== F2P: _format_dtype_mismatch_summary produces readable aggregated output ==="
# [pr_diff] (0.35): Summary formatter aggregates dtype mismatches into readable string
if python3 -c "
import sys, ast, textwrap
from collections import Counter, defaultdict

source = open('$TARGET').read()
tree = ast.parse(source)

# Extract the function via AST (robust to surrounding imports)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_format_dtype_mismatch_summary':
        func_node = node
        break

if func_node is None:
    print('FAIL: _format_dtype_mismatch_summary function not found')
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent(''.join(lines[func_node.lineno - 1 : func_node.end_lineno]))

env = {'Counter': Counter, 'defaultdict': defaultdict, '__builtins__': __builtins__}
exec(func_src, env)
fmt = env['_format_dtype_mismatch_summary']

# --- Test 1: multiple mismatch types ---
counts = Counter()
examples = defaultdict(list)
counts[('torch.float32', 'torch.bfloat16')] = 5
examples[('torch.float32', 'torch.bfloat16')] = ['layer.0.weight', 'layer.1.bias', 'embed.pos']
counts[('torch.float16', 'torch.bfloat16')] = 2
examples[('torch.float16', 'torch.bfloat16')] = ['norm.weight']

result = fmt(counts, examples)
assert isinstance(result, str), f'Expected str, got {type(result)}'
assert len(result) > 0, 'Empty result'

# Must NOT be a raw repr dump
assert 'Counter(' not in result, f'Raw Counter repr in output: {result}'
assert 'defaultdict(' not in result, f'Raw defaultdict repr in output: {result}'

# Both dtype pairs must appear with their counts
# We check that for EACH pair, its count and at least one dtype name is present nearby
# This is format-agnostic: allows 'float32->bfloat16 x5' or '5 params: float32 to bfloat16' etc.
assert 'float32' in result, f'Missing float32 dtype in: {result}'
assert 'bfloat16' in result, f'Missing bfloat16 dtype in: {result}'
assert 'float16' in result, f'Missing float16 dtype in: {result}'

# Both counts must be present (as strings)
assert '5' in result, f'Missing count 5 in: {result}'
assert '2' in result, f'Missing count 2 in: {result}'

# At least one example param name must appear
assert 'layer.0.weight' in result or 'layer.1.bias' in result or 'embed.pos' in result, \
    f'Missing example param names in: {result}'

# --- Test 2: single mismatch type ---
counts2 = Counter()
examples2 = defaultdict(list)
counts2[('torch.int8', 'torch.float32')] = 10
examples2[('torch.int8', 'torch.float32')] = ['fc.weight']
result2 = fmt(counts2, examples2)
assert 'int8' in result2, f'Missing int8 in single-pair result: {result2}'
assert '10' in result2, f'Missing count 10 in single-pair result: {result2}'
assert 'fc.weight' in result2, f'Missing example in single-pair result: {result2}'

print('PASS')
" 2>&1; then
    echo "PASS: _format_dtype_mismatch_summary produces correct aggregated output"
    SCORE=$((SCORE + 35))
else
    echo "FAIL: _format_dtype_mismatch_summary behavioral test"
fi

echo ""
echo "=== F2P: _format_dtype_mismatch_summary handles edge cases ==="
# [pr_diff] (0.15): Summary formatter handles empty examples and is callable
if python3 -c "
import sys, ast, textwrap
from collections import Counter, defaultdict

source = open('$TARGET').read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_format_dtype_mismatch_summary':
        func_node = node
        break

if func_node is None:
    print('FAIL: function not found')
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent(''.join(lines[func_node.lineno - 1 : func_node.end_lineno]))
env = {'Counter': Counter, 'defaultdict': defaultdict, '__builtins__': __builtins__}
exec(func_src, env)
fmt = env['_format_dtype_mismatch_summary']

# Anti-stub: function body must have real logic (not just return str(...))
# Check AST has loop or comprehension or join
body_has_logic = False
for inner in ast.walk(func_node):
    if isinstance(inner, (ast.For, ast.ListComp, ast.GeneratorExp, ast.DictComp, ast.SetComp)):
        body_has_logic = True
        break
    if isinstance(inner, ast.Call):
        if isinstance(inner.func, ast.Attribute) and inner.func.attr == 'join':
            body_has_logic = True
            break
if not body_has_logic:
    print('FAIL: function body lacks iteration/formatting logic (likely a stub)')
    sys.exit(1)

# Edge case: empty examples list for a pair
counts_e = Counter()
examples_e = defaultdict(list)
counts_e[('torch.float32', 'torch.bfloat16')] = 3
examples_e[('torch.float32', 'torch.bfloat16')] = []  # no examples
result_e = fmt(counts_e, examples_e)
assert isinstance(result_e, str), 'Expected string'
assert '3' in result_e, f'Missing count with empty examples: {result_e}'
assert 'float32' in result_e, f'Missing dtype with empty examples: {result_e}'

# Edge case: three different mismatch types
counts3 = Counter()
examples3 = defaultdict(list)
for i, pair in enumerate([('a', 'b'), ('c', 'd'), ('e', 'f')]):
    counts3[pair] = i + 1
    examples3[pair] = [f'p{i}']
result3 = fmt(counts3, examples3)
assert 'p0' in result3 or 'p1' in result3 or 'p2' in result3, \
    f'Missing examples for multi-pair: {result3}'
# All three counts should appear
assert '1' in result3 and '2' in result3 and '3' in result3, \
    f'Missing counts for multi-pair: {result3}'

print('PASS')
" 2>&1; then
    echo "PASS: edge cases handled"
    SCORE=$((SCORE + 15))
else
    echo "FAIL: edge case handling"
fi

echo ""
echo "=== P2P: Existing function signatures preserved ==="
# [repo_tests] (0.10): Core function signatures unchanged
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

required_funcs = {
    'load_model_from_full_model_state_dict': ['model', 'full_sd_iterator', 'device', 'param_dtype'],
    '_make_param_like': ['actual_param', 'tensor'],
    'shard_model': ['model'],
}

for func_name, required_args in required_funcs.items():
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            found = True
            arg_names = [a.arg for a in node.args.args]
            for req in required_args:
                if req not in arg_names:
                    print(f'FAIL: {func_name} missing arg {req}')
                    sys.exit(1)
            break
    if not found:
        print(f'FAIL: {func_name} not found')
        sys.exit(1)

print('PASS')
" 2>&1; then
    echo "PASS: function signatures preserved"
    SCORE=$((SCORE + 10))
else
    echo "FAIL: function signatures changed"
fi

echo ""
echo "=== Structural: Per-parameter logger.warning removed from loading loop ==="
# [pr_diff] (0.15): No per-parameter logger.warning calls inside the param iteration loop
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

# Find load_model_from_full_model_state_dict
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'load_model_from_full_model_state_dict':
        func = node
        break

if func is None:
    print('FAIL: function not found')
    sys.exit(1)

# Find the for-loop over sorted param names
for_loop = None
for node in ast.walk(func):
    if isinstance(node, ast.For):
        # Check if the iterator involves sorted() or param_names
        iter_src = ast.dump(node.iter)
        if 'sorted' in iter_src or 'param_name' in iter_src.lower() or 'sorted_param' in iter_src:
            for_loop = node
            break

if for_loop is None:
    print('FAIL: main parameter loading loop not found')
    sys.exit(1)

# Check for logger.warning calls inside the for loop that emit per-parameter messages
# We look for logger.warning calls that include the loop variable in their arguments
# (indicating per-parameter logging rather than aggregated logging)
loop_var = for_loop.target
if isinstance(loop_var, ast.Name):
    loop_var_name = loop_var.id
else:
    loop_var_name = None

per_param_warnings = 0
for node in ast.walk(for_loop):
    if isinstance(node, ast.Call):
        # Check if it's logger.warning(...)
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr == 'warning' and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'logger'):
            # Check if the loop variable is used in the call args
            # (indicates per-parameter warning)
            call_src = ast.dump(node)
            if loop_var_name and loop_var_name in call_src:
                per_param_warnings += 1
            # Also check for 'Dtype mismatch' in string constants
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if 'Dtype mismatch for' in arg.value:
                        per_param_warnings += 1
                if isinstance(arg, ast.JoinedStr):
                    for val in arg.values:
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            if 'Dtype mismatch for' in val.value:
                                per_param_warnings += 1

if per_param_warnings > 0:
    print(f'FAIL: found {per_param_warnings} per-parameter logger.warning calls in loop')
    sys.exit(1)

print('PASS')
" 2>&1; then
    echo "PASS: no per-parameter warnings in loop"
    SCORE=$((SCORE + 15))
else
    echo "FAIL: per-parameter warnings still present in loop"
fi

echo ""
echo "=== Structural: Aggregated summary logging after loading loop ==="
# [pr_diff] (0.10): Summary log call exists after the main loading loop
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

# Find load_model_from_full_model_state_dict
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'load_model_from_full_model_state_dict':
        func = node
        break

if func is None:
    print('FAIL: function not found')
    sys.exit(1)

# Find the main for-loop end line
for_loop_end = 0
for node in ast.walk(func):
    if isinstance(node, ast.For):
        iter_src = ast.dump(node.iter)
        if 'sorted' in iter_src or 'param_name' in iter_src.lower():
            for_loop_end = node.end_lineno
            break

if for_loop_end == 0:
    print('FAIL: main loop not found')
    sys.exit(1)

# Look for logger calls (debug, warning, info) AFTER the for loop
# that reference dtype/mismatch/summary related content
found_summary_log = False
for node in ast.walk(func):
    if not hasattr(node, 'lineno'):
        continue
    if node.lineno <= for_loop_end:
        continue
    if isinstance(node, ast.Call):
        if (isinstance(node.func, ast.Attribute) and
            node.func.attr in ('debug', 'warning', 'info') and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'logger'):
            # Check if the call references dtype/mismatch/cast keywords
            call_dump = ast.dump(node)
            if any(kw in call_dump.lower() for kw in ['dtype', 'mismatch', 'cast', 'quantiz', 'format_dtype', 'summary']):
                found_summary_log = True
                break

if not found_summary_log:
    print('FAIL: no aggregated summary log found after loading loop')
    sys.exit(1)

print('PASS')
" 2>&1; then
    echo "PASS: aggregated summary log found"
    SCORE=$((SCORE + 10))
else
    echo "FAIL: no aggregated summary log"
fi

echo ""
echo "=== Structural: Quantized dtype set at module scope ==="
# [pr_diff] (0.10): Quantized dtype set/tuple not re-created inside the loading loop
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

# Check that the loading function does NOT define a tuple/set of quantized dtypes
# inside the for loop (it was being re-created every iteration in the buggy code)
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'load_model_from_full_model_state_dict':
        func = node
        break

if func is None:
    print('FAIL: function not found')
    sys.exit(1)

# Find for loops and check for quantized dtype definitions inside them
for node in ast.walk(func):
    if isinstance(node, ast.For):
        for inner in ast.walk(node):
            if isinstance(inner, ast.Assign):
                for target in inner.targets:
                    if isinstance(target, ast.Name) and 'quantiz' in target.id.lower():
                        # Found a quantized dtype set defined inside a loop
                        print(f'FAIL: {target.id} defined inside loop (should be at broader scope)')
                        sys.exit(1)

# Also verify some quantized dtype reference exists at module or function scope
# (not narrowly tied to one variable name)
has_quantized_ref = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        src = ast.dump(node)
        if 'uint8' in src or 'float8' in src or 'quantiz' in src.lower():
            has_quantized_ref = True
            break
if not has_quantized_ref:
    # Also check at function level (top-level assigns in the function, not in loops)
    for node in ast.iter_child_nodes(func):
        if isinstance(node, ast.Assign):
            src = ast.dump(node)
            if 'uint8' in src or 'float8' in src or 'quantiz' in src.lower():
                has_quantized_ref = True
                break

if not has_quantized_ref:
    print('FAIL: no quantized dtype reference at module or function scope')
    sys.exit(1)

print('PASS')
" 2>&1; then
    echo "PASS: quantized dtypes not re-created in loop"
    SCORE=$((SCORE + 10))
else
    echo "FAIL: quantized dtypes still defined inside loop"
fi

echo ""
echo "=== Config: No wildcard imports ==="
# [agent_config] (0.05): Clean imports — CLAUDE.md
if python3 -c "
import ast, sys

source = open('$TARGET').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.names:
        for alias in node.names:
            if alias.name == '*':
                print(f'FAIL: wildcard import from {node.module}')
                sys.exit(1)

print('PASS')
" 2>&1; then
    echo "PASS: no wildcard imports"
    SCORE=$((SCORE + 5))
else
    echo "FAIL: wildcard imports found"
fi

echo ""
echo "=== Results ==="
FINAL=$(python3 -c "print(f'{$SCORE / $TOTAL:.4f}')")
echo "Score: $SCORE / $TOTAL = $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
behavioral = min($SCORE, 60) / 100.0
structural = max(0, $SCORE - 60) / 100.0
json.dump({
    'reward': $SCORE / $TOTAL,
    'behavioral': behavioral,
    'regression': min(0.10, $SCORE / $TOTAL),
    'config': min(0.05, $SCORE / $TOTAL),
    'style_rubric': 0.0
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
