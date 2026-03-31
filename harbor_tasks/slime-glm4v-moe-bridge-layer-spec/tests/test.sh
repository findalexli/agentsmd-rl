#!/usr/bin/env bash
set +e

FILE="/workspace/slime/slime_plugins/megatron_bridge/glm4v_moe.py"
REWARD=0.0

add() { REWARD=$(python3 -c "print(round($REWARD + $1, 4))"); }

echo "=== GATE: Syntax check ==="
# [static] (0): Python syntax must be valid
if ! python3 -c "
import ast, sys
with open('$FILE') as f:
    try:
        ast.parse(f.read())
        print('PASS: syntax OK')
    except SyntaxError as e:
        print(f'FAIL: {e}')
        sys.exit(1)
"; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

echo ""
echo "=== F2P: moe_layer_freq evaluates to a list (not a string) ==="
# [pr_diff] (0.30): Extract moe_layer_freq computation from provider_bridge, eval with mock values
# WHY AST-extract: megatron not installable, but we CAN eval the RHS expression
python3 -c "
import ast, sys

FILE = '$FILE'
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find provider_bridge method
provider_bridge = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'provider_bridge':
        provider_bridge = node
        break

if provider_bridge is None:
    print('FAIL: provider_bridge method not found')
    sys.exit(1)

# Strategy 1: Find assignment to a variable containing 'moe_layer_freq'
# and eval the RHS with mock values
tested = False
for child in ast.walk(provider_bridge):
    if isinstance(child, ast.Assign):
        for target in child.targets:
            if isinstance(target, ast.Name) and 'moe_layer_freq' in target.id:
                rhs_src = ast.get_source_segment(source, child.value)
                if rhs_src:
                    ns = {
                        'first_k_dense': 1,
                        'num_layers': 46,
                        'first_k_dense_replace': 1,
                        'num_hidden_layers': 46,
                    }
                    try:
                        result = eval(rhs_src, {'__builtins__': __builtins__}, ns)
                    except Exception as e:
                        print(f'FAIL: could not eval moe_layer_freq expression: {e}')
                        sys.exit(1)
                    if isinstance(result, str):
                        print(f'FAIL: moe_layer_freq evaluates to string: {result!r}')
                        sys.exit(1)
                    if isinstance(result, (list, tuple)):
                        print(f'PASS: moe_layer_freq evaluates to {type(result).__name__} of length {len(result)}')
                        tested = True
                    else:
                        print(f'FAIL: moe_layer_freq is unexpected type: {type(result).__name__}')
                        sys.exit(1)
                break

# Strategy 2: Check the keyword arg value directly in the function call
if not tested:
    for child in ast.walk(provider_bridge):
        if isinstance(child, ast.keyword) and child.arg == 'moe_layer_freq':
            val = child.value
            # If it's a direct list/tuple literal or list comprehension, that's fine
            if isinstance(val, (ast.List, ast.Tuple, ast.ListComp)):
                print('PASS: moe_layer_freq is a list/tuple literal')
                tested = True
                break
            # If it's a variable, check that the variable was assigned a non-string
            if isinstance(val, ast.Name):
                varname = val.id
                for child2 in ast.walk(provider_bridge):
                    if isinstance(child2, ast.Assign):
                        for t in child2.targets:
                            if isinstance(t, ast.Name) and t.id == varname:
                                rhs = ast.get_source_segment(source, child2.value)
                                if rhs:
                                    try:
                                        r = eval(rhs, {'__builtins__': __builtins__}, {'first_k_dense': 1, 'num_layers': 46})
                                        if isinstance(r, str):
                                            print(f'FAIL: variable {varname} evaluates to string')
                                            sys.exit(1)
                                        if isinstance(r, (list, tuple)):
                                            print(f'PASS: variable {varname} evaluates to {type(r).__name__}')
                                            tested = True
                                    except:
                                        pass
                                break
                break
            # If it's an f-string or string constant, fail
            if isinstance(val, ast.JoinedStr):
                print('FAIL: moe_layer_freq is an f-string')
                sys.exit(1)
            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                print('FAIL: moe_layer_freq is a string constant')
                sys.exit(1)

if not tested:
    print('FAIL: could not find or verify moe_layer_freq computation')
    sys.exit(1)
" && add 0.30 || echo "FAILED (0.30)"

echo ""
echo "=== F2P: moe_layer_freq values are correct ==="
# [pr_diff] (0.15): The list must have correct dense/MoE pattern
python3 -c "
import ast, sys

FILE = '$FILE'
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'provider_bridge':
        for child in ast.walk(node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name) and 'moe_layer_freq' in target.id:
                        rhs_src = ast.get_source_segment(source, child.value)
                        if not rhs_src:
                            continue
                        # Test with different configs
                        for dk, nl in [(1, 46), (2, 10), (0, 5), (3, 3)]:
                            ns = {'first_k_dense': dk, 'num_layers': nl, 'num_hidden_layers': nl, 'first_k_dense_replace': dk}
                            try:
                                result = eval(rhs_src, {'__builtins__': __builtins__}, ns)
                            except Exception as e:
                                print(f'FAIL: eval error with dk={dk}, nl={nl}: {e}')
                                sys.exit(1)
                            if not isinstance(result, (list, tuple)):
                                print(f'FAIL: result is {type(result).__name__}, not list/tuple')
                                sys.exit(1)
                            if len(result) != nl:
                                print(f'FAIL: length {len(result)} != num_layers {nl}')
                                sys.exit(1)
                            # First dk entries should be 0 (dense), rest should be 1 (MoE)
                            for i in range(dk):
                                if i < len(result) and result[i] != 0:
                                    print(f'FAIL: layer {i} should be dense (0), got {result[i]}')
                                    sys.exit(1)
                            for i in range(dk, nl):
                                if result[i] != 1:
                                    print(f'FAIL: layer {i} should be MoE (1), got {result[i]}')
                                    sys.exit(1)
                        print('PASS: moe_layer_freq values correct for all test configs')
                        sys.exit(0)
        break

print('FAIL: could not find moe_layer_freq computation')
sys.exit(1)
" && add 0.15 || echo "FAILED (0.15)"

echo ""
echo "=== Behavioral: provide() calls correct spec function ==="
# [pr_diff] (0.15): provide() must use get_gpt_decoder_block_spec, not the old function
# WHY AST: megatron not installable in CPU test env
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'provide':
        calls = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.add(child.func.attr)

        if 'get_gpt_layer_with_transformer_engine_spec' in calls:
            print('FAIL: still using old get_gpt_layer_with_transformer_engine_spec')
            sys.exit(1)
        if 'get_gpt_decoder_block_spec' in calls:
            print('PASS: uses get_gpt_decoder_block_spec')
            sys.exit(0)

        print('FAIL: no recognized spec function called in provide()')
        sys.exit(1)

print('FAIL: provide() not found')
sys.exit(1)
" && add 0.15 || echo "FAILED (0.15)"

echo ""
echo "=== Behavioral: provide() passes config to spec function ==="
# [pr_diff] (0.05): get_gpt_decoder_block_spec must receive config
# WHY AST: megatron not installable
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'provide':
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                name = None
                if isinstance(child.func, ast.Name):
                    name = child.func.id
                elif isinstance(child.func, ast.Attribute):
                    name = child.func.attr
                if name == 'get_gpt_decoder_block_spec':
                    # Accept config as keyword OR first positional arg
                    kw_names = {kw.arg for kw in child.keywords}
                    has_config_kw = 'config' in kw_names
                    has_positional = len(child.args) >= 1
                    if has_config_kw or has_positional:
                        print('PASS: passes config to get_gpt_decoder_block_spec')
                        sys.exit(0)
                    else:
                        print('FAIL: get_gpt_decoder_block_spec called without config')
                        sys.exit(1)

print('FAIL: get_gpt_decoder_block_spec call not found in provide()')
sys.exit(1)
" && add 0.05 || echo "FAILED (0.05)"

echo ""
echo "=== Regression: key classes still exist ==="
# [repo_tests] (0.10): Core classes must still be defined
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
required = {'Glm4vMoeVLModel', 'Glm4vMoeVLModelProvider', 'Glm4vMoeBridge'}
missing = required - classes
if missing:
    print(f'FAIL: missing classes: {missing}')
    sys.exit(1)
print(f'PASS: all required classes present: {required}')
" && add 0.10 || echo "FAILED (0.10)"

echo ""
echo "=== Regression: key methods have substance ==="
# [repo_tests] (0.10): Core methods must not be stubbed
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

required_methods = {
    'Glm4vMoeVLModelProvider': ['provide', 'provider_bridge'],
    'Glm4vMoeVLModel': ['__init__', 'forward'],
}
for cls_name, methods in required_methods.items():
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            found_methods = {}
            for item in ast.walk(node):
                if isinstance(item, ast.FunctionDef) and item.name in methods:
                    # Count non-docstring, non-pass statements
                    stmts = 0
                    for s in ast.walk(item):
                        if isinstance(s, (ast.Assign, ast.Return, ast.If, ast.For,
                                          ast.Call, ast.AugAssign, ast.AnnAssign)):
                            stmts += 1
                    found_methods[item.name] = stmts
            for m in methods:
                if m not in found_methods:
                    print(f'FAIL: {cls_name}.{m} not found')
                    sys.exit(1)
                if found_methods[m] < 3:
                    print(f'FAIL: {cls_name}.{m} has only {found_methods[m]} statements (likely stub)')
                    sys.exit(1)
            break
    else:
        print(f'FAIL: class {cls_name} not found')
        sys.exit(1)
print('PASS: all key methods have substance')
" && add 0.10 || echo "FAILED (0.10)"

echo ""
echo "=== Anti-stub: file has substantial content ==="
# [static] (0.05): File must not be stubbed out
python3 -c "
import sys
with open('$FILE') as f:
    lines = [l for l in f.readlines() if l.strip() and not l.strip().startswith('#')]
if len(lines) < 150:
    print(f'FAIL: file too short ({len(lines)} non-empty non-comment lines), likely stubbed')
    sys.exit(1)
print(f'PASS: file has {len(lines)} substantive lines')
" && add 0.05 || echo "FAILED (0.05)"

echo ""
echo "=== Behavioral: correct import ==="
# [pr_diff] (0.05): imports get_gpt_decoder_block_spec (not old function)
# WHY AST: megatron not installable
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

imports = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            real_name = alias.name
            used_name = alias.asname if alias.asname else alias.name
            imports[used_name] = real_name

# Check the old function is not imported
for used, real in imports.items():
    if real == 'get_gpt_layer_with_transformer_engine_spec':
        print('FAIL: still imports get_gpt_layer_with_transformer_engine_spec')
        sys.exit(1)

# Check new function is imported (under any alias)
for used, real in imports.items():
    if real == 'get_gpt_decoder_block_spec':
        print(f'PASS: imports get_gpt_decoder_block_spec (as {used})')
        sys.exit(0)

print('FAIL: get_gpt_decoder_block_spec not imported')
sys.exit(1)
" && add 0.05 || echo "FAILED (0.05)"

echo ""
echo "=== Behavioral: ModuleSpec type annotation removed ==="
# [pr_diff] (0.05): __init__ param should not have ModuleSpec annotation
# WHY AST: megatron not installable
python3 -c "
import ast, sys

with open('$FILE') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'Glm4vMoeVLModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for arg in item.args.args:
                    if arg.arg == 'language_transformer_layer_spec':
                        if arg.annotation is not None:
                            ann_src = ast.dump(arg.annotation)
                            if 'ModuleSpec' in ann_src:
                                print('FAIL: still has ModuleSpec in type annotation')
                                sys.exit(1)
                        print('PASS: no ModuleSpec annotation on language_transformer_layer_spec')
                        sys.exit(0)

# Parameter might have been renamed or restructured — that's OK if classes exist
print('PASS: language_transformer_layer_spec param not found (acceptable if restructured)')
" && add 0.05 || echo "FAILED (0.05)"

echo ""
echo "=== Results ==="
echo "Total reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Compute breakdown
python3 -c "
import json
r = $REWARD
# F2P behavioral: 0.30 + 0.15 = 0.45
# AST behavioral: 0.15 + 0.05 + 0.05 + 0.05 = 0.30
# Regression: 0.10 + 0.10 = 0.20
# Anti-stub: 0.05
behavioral = min(0.45, r)
remaining = max(0, r - 0.45)
ast_beh = min(0.30, remaining)
remaining2 = max(0, remaining - 0.30)
regression = min(0.20, remaining2)
print(json.dumps({'reward': r, 'behavioral': round(behavioral + ast_beh, 4), 'regression': round(regression, 4), 'config': 0.0, 'style_rubric': 0.0}))
" > /logs/verifier/reward.json

cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
