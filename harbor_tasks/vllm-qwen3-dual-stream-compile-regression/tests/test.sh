#!/usr/bin/env bash
set +e

SCORE=0
QWEN3_NEXT="/workspace/vllm/vllm/model_executor/models/qwen3_next.py"
QWEN3_5="/workspace/vllm/vllm/model_executor/models/qwen3_5.py"

echo "=== vllm-qwen3-dual-stream-compile-regression ==="
echo ""

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): Both files must be valid Python
echo "--- GATE: Python syntax check ---"
GATE_OK=1
for f in "$QWEN3_NEXT" "$QWEN3_5"; do
    if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$f').read())
except SyntaxError as e:
    print(f'Syntax error in $f: {e}')
    sys.exit(1)
"; then
        GATE_OK=0
    fi
done
if [ "$GATE_OK" -eq 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"
echo ""

########################################
# BEHAVIORAL FAIL-TO-PASS: Core bug checks
########################################
# The bug: forward methods route input projection through a custom op
# (torch.ops.vllm.gdn_in_proj) that passes layer_name strings, causing
# torch.compile to retrace per layer (~4x compile regression).
# Fix: call the linear layers directly instead.

# [pr_diff] (0.25): qwen3_next.py forward must NOT call gdn_in_proj custom op
echo "--- F2P: qwen3_next forward does not use gdn_in_proj custom op ---"
F2P1_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

# Find the Qwen3NextGDNAttention class and its forward method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                # Check for any call to torch.ops.vllm.gdn_in_proj in forward
                forward_src = ast.get_source_segment(source, item)
                if forward_src is None:
                    # Fallback: extract from line range
                    lines = source.splitlines()
                    forward_src = '\n'.join(lines[item.lineno-1:item.end_lineno])
                forward_tree = ast.parse(forward_src)
                for call_node in ast.walk(forward_tree):
                    if isinstance(call_node, ast.Call):
                        call_src = ast.get_source_segment(forward_src, call_node.func)
                        if call_src and 'gdn_in_proj' in call_src:
                            print('FAIL: forward still calls gdn_in_proj custom op')
                            sys.exit(0)
                print('OK')
                sys.exit(0)

print('FAIL: could not find GDNAttention.forward method')
" 2>&1)
echo "  $F2P1_RESULT"
if echo "$F2P1_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    echo "  +0.25"
fi
echo ""

# [pr_diff] (0.15): qwen3_5.py forward must NOT call gdn_in_proj custom op
echo "--- F2P: qwen3_5 forward does not use gdn_in_proj custom op ---"
F2P2_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_5') as f:
    source = f.read()
tree = ast.parse(source)

# Find the GDNAttention subclass and its forward method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                forward_src = ast.get_source_segment(source, item)
                if forward_src is None:
                    lines = source.splitlines()
                    forward_src = '\n'.join(lines[item.lineno-1:item.end_lineno])
                forward_tree = ast.parse(forward_src)
                for call_node in ast.walk(forward_tree):
                    if isinstance(call_node, ast.Call):
                        call_src = ast.get_source_segment(forward_src, call_node.func)
                        if call_src and 'gdn_in_proj' in call_src:
                            print('FAIL: forward still calls gdn_in_proj custom op')
                            sys.exit(0)
                print('OK')
                sys.exit(0)

print('FAIL: could not find GDNAttention.forward method')
" 2>&1)
echo "  $F2P2_RESULT"
if echo "$F2P2_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  +0.15"
fi
echo ""

# [pr_diff] (0.15): gdn_in_proj must NOT be registered as a custom op at module level
echo "--- F2P: gdn_in_proj custom op not registered ---"
F2P3_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

# Check module-level calls to direct_register_custom_op with op_name='gdn_in_proj'
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        # Check if this is direct_register_custom_op(op_name='gdn_in_proj', ...)
        for kw in call.keywords:
            if kw.arg == 'op_name' and isinstance(kw.value, ast.Constant):
                if kw.value.value == 'gdn_in_proj':
                    print('FAIL: gdn_in_proj still registered as custom op')
                    sys.exit(0)
        # Also check positional args
        if call.args and isinstance(call.args[0], ast.Constant):
            if call.args[0].value == 'gdn_in_proj':
                print('FAIL: gdn_in_proj still registered as custom op')
                sys.exit(0)

print('OK')
" 2>&1)
echo "  $F2P3_RESULT"
if echo "$F2P3_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  +0.15"
fi
echo ""

########################################
# PASS-TO-PASS: Regression checks
########################################

# [pr_diff] (0.10): qwen3_next forward still performs input projection via linear layers
echo "--- P2P: qwen3_next forward calls in_proj_qkvz and in_proj_ba ---"
P2P1_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                forward_src = ast.get_source_segment(source, item)
                if forward_src is None:
                    lines = source.splitlines()
                    forward_src = '\n'.join(lines[item.lineno-1:item.end_lineno])
                # Check that forward calls self.in_proj_qkvz and self.in_proj_ba
                has_qkvz = False
                has_ba = False
                forward_tree = ast.parse(forward_src)
                for call_node in ast.walk(forward_tree):
                    if isinstance(call_node, ast.Call) and isinstance(call_node.func, ast.Attribute):
                        if call_node.func.attr == 'in_proj_qkvz':
                            has_qkvz = True
                        if call_node.func.attr == 'in_proj_ba':
                            has_ba = True
                if has_qkvz and has_ba:
                    print('OK')
                else:
                    missing = []
                    if not has_qkvz: missing.append('in_proj_qkvz')
                    if not has_ba: missing.append('in_proj_ba')
                    print(f'FAIL: forward missing direct calls to: {\", \".join(missing)}')
                sys.exit(0)

print('FAIL: could not find GDNAttention.forward')
" 2>&1)
echo "  $P2P1_RESULT"
if echo "$P2P1_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.10): qwen3_5 forward else-branch calls in_proj_qkvz and in_proj_ba
echo "--- P2P: qwen3_5 forward calls in_proj_qkvz and in_proj_ba ---"
P2P2_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_5') as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'forward':
                forward_src = ast.get_source_segment(source, item)
                if forward_src is None:
                    lines = source.splitlines()
                    forward_src = '\n'.join(lines[item.lineno-1:item.end_lineno])
                has_qkvz = False
                has_ba = False
                forward_tree = ast.parse(forward_src)
                for call_node in ast.walk(forward_tree):
                    if isinstance(call_node, ast.Call) and isinstance(call_node.func, ast.Attribute):
                        if call_node.func.attr == 'in_proj_qkvz':
                            has_qkvz = True
                        if call_node.func.attr == 'in_proj_ba':
                            has_ba = True
                if has_qkvz and has_ba:
                    print('OK')
                else:
                    missing = []
                    if not has_qkvz: missing.append('in_proj_qkvz')
                    if not has_ba: missing.append('in_proj_ba')
                    print(f'FAIL: forward missing direct calls to: {\", \".join(missing)}')
                sys.exit(0)

print('FAIL: could not find GDNAttention.forward')
" 2>&1)
echo "  $P2P2_RESULT"
if echo "$P2P2_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

# [pr_diff] (0.10): gdn_attention_core custom op still registered (not over-deleted)
echo "--- P2P: gdn_attention_core custom op preserved ---"
P2P3_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

found = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        for kw in call.keywords:
            if kw.arg == 'op_name' and isinstance(kw.value, ast.Constant):
                if kw.value.value == 'gdn_attention_core':
                    found = True
        if call.args and isinstance(call.args[0], ast.Constant):
            if call.args[0].value == 'gdn_attention_core':
                found = True

if found:
    print('OK')
else:
    print('FAIL: gdn_attention_core custom op registration missing (over-deletion)')
" 2>&1)
echo "  $P2P3_RESULT"
if echo "$P2P3_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
echo ""

########################################
# STRUCTURAL: Anti-stub / completeness
########################################

# [pr_diff] (0.05): qwen3_next __init__ must NOT set up aux_stream or cuda Events for dual-stream
echo "--- STRUCTURAL: __init__ does not create aux_stream/events ---"
STRUCT1_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                init_src = ast.get_source_segment(source, item)
                if init_src is None:
                    lines = source.splitlines()
                    init_src = '\n'.join(lines[item.lineno-1:item.end_lineno])
                init_tree = ast.parse(init_src)
                issues = []
                for assign_node in ast.walk(init_tree):
                    if isinstance(assign_node, ast.Assign):
                        for t in assign_node.targets:
                            if isinstance(t, ast.Attribute) and t.attr in ('aux_stream', 'events'):
                                issues.append(t.attr)
                if issues:
                    print(f'FAIL: __init__ still sets up: {\", \".join(issues)}')
                else:
                    print('OK')
                sys.exit(0)

print('FAIL: could not find GDNAttention.__init__')
" 2>&1)
echo "  $STRUCT1_RESULT"
if echo "$STRUCT1_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

# [pr_diff] (0.05): _forward_in_proj helper removed (dead code)
echo "--- STRUCTURAL: _forward_in_proj removed ---"
STRUCT2_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and 'GDNAttention' in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '_forward_in_proj':
                print('FAIL: _forward_in_proj helper still exists (dead code)')
                sys.exit(0)
        print('OK')
        sys.exit(0)

print('FAIL: could not find GDNAttention class')
" 2>&1)
echo "  $STRUCT2_RESULT"
if echo "$STRUCT2_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

# [pr_diff] (0.05): gdn_in_proj and gdn_in_proj_fake functions removed
echo "--- STRUCTURAL: gdn_in_proj functions removed ---"
STRUCT3_RESULT=$(python3 -c "
import ast, sys

with open('$QWEN3_NEXT') as f:
    source = f.read()
tree = ast.parse(source)

dead_funcs = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ('gdn_in_proj', 'gdn_in_proj_fake'):
        dead_funcs.append(node.name)

if dead_funcs:
    print(f'FAIL: dead functions still present: {\", \".join(dead_funcs)}')
else:
    print('OK')
" 2>&1)
echo "  $STRUCT3_RESULT"
if echo "$STRUCT3_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
echo "Score: $SCORE"

FINAL=$(python3 -c "print(f'{float($SCORE):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.55), 4),
    'regression': round(min(max(score - 0.55, 0), 0.30), 4),
    'structural': round(min(max(score - 0.85, 0), 0.15), 4),
}))
" > /logs/verifier/reward.json
