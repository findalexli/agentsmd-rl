#!/usr/bin/env bash
set +e

TARGET="/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_device_param]=0.30
WEIGHTS[behavioral_arange_exec]=0.30
WEIGHTS[behavioral_callsite]=0.20
WEIGHTS[p2p_upstreams]=0.10
WEIGHTS[antistub_functional]=0.10

for key in behavioral_device_param behavioral_arange_exec behavioral_callsite p2p_upstreams antistub_functional; do
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
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

echo "GATE: syntax valid"

# ---------- PRIMARY 1 (30%): Behavioral - device parameter and execution ----------
# [pr_diff] (0.30): relative_positional_encoding accepts device parameter and creates tensors on correct device
python3 << 'PYEOF'
import sys
import re

# Extract the function and extract its signature
with open('/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py', 'r') as f:
    source = f.read()

import ast
tree = ast.parse(source)

# Find the XLNetModel class and relative_positional_encoding method
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'XLNetModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'relative_positional_encoding':
                func_node = item
                break

if func_node is None:
    print("PARAM FAIL: relative_positional_encoding method not found")
    sys.exit(1)

# Verify device parameter exists
param_names = [arg.arg for arg in func_node.args.args]
if 'device' not in param_names:
    print(f"PARAM FAIL: 'device' parameter missing. Found: {param_names}")
    sys.exit(1)

# Verify all torch.arange calls in the function body use device=
arange_calls = []
device_kws = []
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == 'arange' and
            isinstance(func.value, ast.Name) and func.value.id == 'torch'):
            arange_calls.append(node)
            has_device_kw = any(kw.arg == 'device' for kw in node.keywords)
            device_kws.append(has_device_kw)

if not arange_calls:
    print("PARAM FAIL: No torch.arange calls found in method")
    sys.exit(1)

if not all(device_kws):
    print(f"PARAM FAIL: Not all torch.arange calls have device= keyword")
    sys.exit(1)

print(f"PARAM PASS: device parameter exists, {len(arange_calls)} torch.arange calls all have device=")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_device_param]=1
    echo "TEST behavioral_device_param: PASS"
else
    echo "TEST behavioral_device_param: FAIL"
fi

# ---------- PRIMARY 2 (30%): Behavioral - arange calls use device parameter with execution ----------
# [pr_diff] (0.30): Function creates tensors on correct device when called with device='cpu'
python3 << 'PYEOF'
import sys
import ast
import torch
import textwrap

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Find the function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'XLNetModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'relative_positional_encoding':
                func_node = item
                break

if func_node is None:
    print("EXEC FAIL: method not found")
    sys.exit(1)

# Extract function lines
lines = source.splitlines(keepends=True)
# Find the actual function indentation by looking at the def line
def_line = lines[func_node.lineno - 1]
base_indent = len(def_line) - len(def_line.lstrip())

# Extract function body raw
func_src = "".join(lines[func_node.lineno-1:func_node.end_lineno])

# Build a test harness that defines required attributes and helper
test_ns = {
    'torch': torch,
    '__builtins__': __builtins__,
}

# Mock class to execute method on
class_attrs = """
d_model = 768
attn_type = "bi"
bi_data = False
clamp_len = -1

import torch

# Minimal positional_embedding helper
def positional_embedding(pos_seq, inv_freq, bsz=None):
    sinusoid_inp = torch.einsum("i,d->id", pos_seq, inv_freq)
    pos_emb = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=-1)
    if bsz is not None:
        return pos_emb[:, None, :].expand(-1, bsz, -1)
    return pos_emb[:, None, :]
"""

# Wrap in class and call
full_code = """
class TestXLNetModel:
""" + \
    '\n'.join('    ' + line for line in class_attrs.strip().split('\n')) + '\n    ' + \
    func_src + """

model = TestXLNetModel()
try:
    result = model.relative_positional_encoding(qlen=10, klen=20, bsz=2, device='cpu')
    result_device = str(result.device)
    result_shape = result.shape
    is_tensor = isinstance(result, torch.Tensor)
except Exception as e:
    error = str(e)
"""

exec_ns = {'torch': torch, '__builtins__': __builtins__}
try:
    exec(full_code, exec_ns)
except Exception as e:
    print(f"EXEC FAIL: Could not execute function: {e}")
    sys.exit(1)

# Check results
if 'result' not in exec_ns:
    print("EXEC FAIL: No result from function call")
    sys.exit(1)

result = exec_ns['result']
if not isinstance(result, torch.Tensor):
    print(f"EXEC FAIL: Result is not a tensor: {type(result)}")
    sys.exit(1)

if str(result.device) != 'cpu':
    print(f"EXEC FAIL: Result device is {result.device}, expected cpu")
    sys.exit(1)

print(f"EXEC PASS: Function executed and created tensor on device='cpu', shape={result.shape}")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_arange_exec]=1
    echo "TEST behavioral_arange_exec: PASS"
else
    echo "TEST behavioral_arange_exec: FAIL"
fi

# ---------- PRIMARY 3 (20%): Behavioral - forward passes device, no redundant .to() ----------
# [pr_diff] (0.20): Call site in forward passes device and removes pos_emb.to() call
python3 << 'PYEOF'
import sys
import ast
import re

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find XLNetModel.forward method
forward_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "XLNetModel":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "forward":
                forward_node = item
                break

if forward_node is None:
    print("CALLSITE FAIL: XLNetModel.forward not found")
    sys.exit(1)

forward_src = ast.get_source_segment(source, forward_node)
if forward_src is None:
    lines = source.splitlines()
    forward_src = "\n".join(lines[forward_node.lineno - 1 : forward_node.end_lineno])

# Remove comments to avoid matching in comments
source_no_comment = re.sub(r'#.*$', '', forward_src, flags=re.MULTILINE)

# Check that device= is passed to relative_positional_encoding
if not re.search(r'relative_positional_encoding\s*\([^)]*device\s*=\s*[^,)]+', source_no_comment):
    print("CALLSITE FAIL: device= not passed to relative_positional_encoding")
    sys.exit(1)

# Check that the old .to(output_h.device) pattern is NOT present
if re.search(r'pos_emb\s*=\s*pos_emb\.to\s*\(', source_no_comment):
    print("CALLSITE FAIL: pos_emb.to(...) pattern still present")
    sys.exit(1)

# Also check for any .to(device) or .to(output_h.device) after the pos_emb line
# Use a simpler check: any pos_emb.to( in the forward method
if "pos_emb.to(" in source_no_comment.replace(" ", ""):
    print("CALLSITE FAIL: pos_emb.to(...) pattern found")
    sys.exit(1)

print("CALLSITE PASS: device= passed to relative_positional_encoding, no redundant .to() call")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[behavioral_callsite]=1
    echo "TEST behavioral_callsite: PASS"
else
    echo "TEST behavioral_callsite: FAIL"
fi

# ---------- PASS-TO-PASS: Upstream tests (10%) ----------
# [repo_tests] (0.10): Existing XLNet tests structure intact
if [ -d "/workspace/transformers/tests" ]; then
    python3 -c "
import sys
sys.path.insert(0, '/workspace/transformers')
import ast
with open('$TARGET') as f:
    tree = ast.parse(f.read())
classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
funcs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
if len(classes) > 0 and len(funcs) > 10:
    print('P2P PASS: File structure intact')
    sys.exit(0)
else:
    print('P2P FAIL: File structure suspicious')
    sys.exit(1)
" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        RESULTS[p2p_upstreams]=1
        echo "TEST p2p_upstreams: PASS"
    else
        echo "TEST p2p_upstreams: FAIL"
    fi
else
    echo "TEST p2p_upstreams: SKIP"
fi

# ---------- Anti-stub: functional check (10%) ----------
# [agent_config] (0.10): Implementation has substantial logic
python3 << 'PYEOF'
import sys
import ast

TARGET = "/workspace/transformers/src/transformers/models/xlnet/modeling_xlnet.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find relative_positional_encoding and check it has substance
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'XLNetModel':
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == 'relative_positional_encoding':
                func_node = item
                break

if func_node is None:
    print("ANTISTUB FAIL: method not found")
    sys.exit(1)

# Count meaningful statements (not just pass/returns)
meaningful_stmts = 0
for stmt in func_node.body:
    if isinstance(stmt, ast.Pass):
        continue
    if isinstance(stmt, ast.Return) and (stmt.value is None or
         (isinstance(stmt.value, ast.Constant) and stmt.value.value in [0, 1, None, True, False])):
        continue
    meaningful_stmts += 1

if meaningful_stmts < 5:
    print(f"ANTISTUB FAIL: Only {meaningful_stmts} meaningful statements")
    sys.exit(1)

# Check for torch.arange calls
arange_count = 0
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == 'arange' and
            isinstance(func.value, ast.Name) and func.value.id == 'torch'):
            arange_count += 1

if arange_count < 3:
    print(f"ANTISTUB FAIL: Only {arange_count} torch.arange calls")
    sys.exit(1)

print(f"ANTISTUB PASS: {meaningful_stmts} statements, {arange_count} arange calls")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    RESULTS[antistub_functional]=1
    echo "TEST antistub_functional: PASS"
else
    echo "TEST antistub_functional: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_device_param': ${WEIGHTS[behavioral_device_param]}, 'behavioral_arange_exec': ${WEIGHTS[behavioral_arange_exec]}, 'behavioral_callsite': ${WEIGHTS[behavioral_callsite]}, 'p2p_upstreams': ${WEIGHTS[p2p_upstreams]}, 'antistub_functional': ${WEIGHTS[antistub_functional]}}
results = {'behavioral_device_param': ${RESULTS[behavioral_device_param]}, 'behavioral_arange_exec': ${RESULTS[behavioral_arange_exec]}, 'behavioral_callsite': ${RESULTS[behavioral_callsite]}, 'p2p_upstreams': ${RESULTS[p2p_upstreams]}, 'antistub_functional': ${RESULTS[antistub_functional]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_device_param  (${WEIGHTS[behavioral_device_param]}): ${RESULTS[behavioral_device_param]}"
echo "  behavioral_arange_exec   (${WEIGHTS[behavioral_arange_exec]}): ${RESULTS[behavioral_arange_exec]}"
echo "  behavioral_callsite      (${WEIGHTS[behavioral_callsite]}): ${RESULTS[behavioral_callsite]}"
echo "  p2p_upstreams            (${WEIGHTS[p2p_upstreams]}): ${RESULTS[p2p_upstreams]}"
echo "  antistub_functional      (${WEIGHTS[antistub_functional]}): ${RESULTS[antistub_functional]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
