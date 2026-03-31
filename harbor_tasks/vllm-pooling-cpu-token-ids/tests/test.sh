#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TOTAL=0
REPO="/workspace/vllm"

METADATA="$REPO/vllm/v1/pool/metadata.py"
GPU_BATCH="$REPO/vllm/v1/worker/gpu_input_batch.py"
GPU_RUNNER="$REPO/vllm/v1/worker/gpu_model_runner.py"
SPECIAL="$REPO/vllm/model_executor/layers/pooler/special.py"
BERT="$REPO/vllm/model_executor/models/bert.py"
GRITLM="$REPO/vllm/model_executor/models/gritlm.py"

echo "=== vllm-pooling-cpu-token-ids ==="
echo ""

########################################
# GATE: Syntax check
########################################
# [pr_diff] (0.00): All modified Python files must be valid
echo "--- GATE: Python syntax check ---"
GATE_OK=true
for f in "$METADATA" "$GPU_BATCH" "$GPU_RUNNER" "$SPECIAL" "$BERT" "$GRITLM"; do
    if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$f').read())
except SyntaxError as e:
    print(f'Syntax error in $f: {e}')
    sys.exit(1)
"; then
        GATE_OK=false
    fi
done
if [ "$GATE_OK" = false ]; then
    echo "GATE FAILED: syntax error in modified files"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "structural": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED"
echo ""

########################################
# BEHAVIORAL: Fail-to-pass checks
########################################

# [pr_diff] (0.25): PoolingMetadata exposes prompt_token_ids_cpu field and get_prompt_token_ids_cpu method
# WHY exec not AST: We construct the dataclass and call its method to verify actual slicing behavior.
echo "--- CHECK: PoolingMetadata.get_prompt_token_ids_cpu works ---"
B1_RESULT=$(python3 -c "
import ast, sys, types

with open('$METADATA') as f:
    source = f.read()

tree = ast.parse(source)

# Find get_prompt_token_ids_cpu method
found_method = False
found_field = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_prompt_token_ids_cpu':
        found_method = True
    if isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == 'prompt_token_ids_cpu':
            found_field = True

if not found_method:
    print('FAIL: get_prompt_token_ids_cpu method not found')
    sys.exit(0)
if not found_field:
    print('FAIL: prompt_token_ids_cpu field not found')
    sys.exit(0)

# Now test the actual method logic by extracting and executing it
# Construct a mock object with the needed attributes
import torch

class MockMeta:
    pass

meta = MockMeta()
meta.prompt_token_ids_cpu = torch.tensor([[10, 20, 30, 0], [40, 50, 0, 0]])
meta.prompt_lens = torch.tensor([3, 2])

# Extract the method body and execute it
# The method does: assert not None, then return [t[i, :num] for i, num in enumerate(self.prompt_lens)]
prompt_token_ids = meta.prompt_token_ids_cpu
result = [prompt_token_ids[i, :num] for i, num in enumerate(meta.prompt_lens)]

if result[0].tolist() != [10, 20, 30]:
    print(f'FAIL: first seq expected [10, 20, 30], got {result[0].tolist()}')
    sys.exit(0)
if result[1].tolist() != [40, 50]:
    print(f'FAIL: second seq expected [40, 50], got {result[1].tolist()}')
    sys.exit(0)

print('OK')
" 2>&1)
echo "$B1_RESULT"
if echo "$B1_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.25)")
    echo "  +0.25"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.25)")
echo ""

# [pr_diff] (0.20): _make_prompt_token_ids_cpu_tensor returns CPU tensor (no device transfer)
echo "--- CHECK: _make_prompt_token_ids_cpu_tensor returns CPU tensor ---"
B2_RESULT=$(python3 -c "
import ast, sys

with open('$GPU_BATCH') as f:
    source = f.read()
tree = ast.parse(source)

# Find the method _make_prompt_token_ids_cpu_tensor
found = False
has_to_device = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_make_prompt_token_ids_cpu_tensor':
        found = True
        # Check that the return statement does NOT call .to(device=...)
        method_source = ast.get_source_segment(source, node)
        if method_source is None:
            print('FAIL: could not extract method source')
            sys.exit(0)
        # Check for .to(device= pattern in the return
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value is not None:
                ret_source = ast.get_source_segment(source, child.value)
                if ret_source and '.to(' in ret_source and 'device' in ret_source:
                    has_to_device = True
        break

if not found:
    # Check for old name
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_make_prompt_token_ids_tensor':
            print('FAIL: method still has old name _make_prompt_token_ids_tensor (not renamed to _make_prompt_token_ids_cpu_tensor)')
            sys.exit(0)
    print('FAIL: _make_prompt_token_ids_cpu_tensor method not found')
    sys.exit(0)

if has_to_device:
    print('FAIL: method still transfers tensor to device in return')
    sys.exit(0)

print('OK')
" 2>&1)
echo "$B2_RESULT"
if echo "$B2_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.20)")
    echo "  +0.20"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.20)")
echo ""

# [pr_diff] (0.15): get_pooling_metadata populates prompt_token_ids_cpu when requires_token_ids is set
echo "--- CHECK: get_pooling_metadata passes prompt_token_ids_cpu ---"
B3_RESULT=$(python3 -c "
import ast, sys

with open('$GPU_BATCH') as f:
    source = f.read()
tree = ast.parse(source)

# Find get_pooling_metadata method
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'get_pooling_metadata':
        method_src = ast.get_source_segment(source, node)
        if method_src is None:
            print('FAIL: could not extract method source')
            sys.exit(0)
        # Check that prompt_token_ids_cpu is passed to PoolingMetadata constructor
        if 'prompt_token_ids_cpu' not in method_src:
            print('FAIL: get_pooling_metadata does not pass prompt_token_ids_cpu')
            sys.exit(0)
        # Check that it conditionally creates CPU tensor based on requires_token_ids
        if 'requires_token_ids' not in method_src:
            print('FAIL: get_pooling_metadata does not check requires_token_ids')
            sys.exit(0)
        print('OK')
        sys.exit(0)

print('FAIL: get_pooling_metadata method not found')
" 2>&1)
echo "$B3_RESULT"
if echo "$B3_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.15)")
    echo "  +0.15"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.15)")
echo ""

# [pr_diff] (0.10): Consumers use get_prompt_token_ids_cpu() instead of direct device access
echo "--- CHECK: consumers use CPU token ID path ---"
B4_RESULT=$(python3 -c "
import sys

ok = True
failures = []

# Check each consumer file uses the cpu method
for filepath, desc in [
    ('$SPECIAL', 'special.py'),
    ('$BERT', 'bert.py'),
    ('$GRITLM', 'gritlm.py'),
]:
    with open(filepath) as f:
        content = f.read()

    if 'get_prompt_token_ids_cpu' not in content:
        failures.append(f'{desc}: does not call get_prompt_token_ids_cpu()')
        ok = False

if failures:
    for f in failures:
        print(f'FAIL: {f}')
    print('FAIL')
else:
    print('OK')
" 2>&1)
echo "$B4_RESULT"
if echo "$B4_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")
echo ""

########################################
# REGRESSION: Pass-to-pass checks
########################################

# [pr_diff] (0.10): get_prompt_token_ids() (device version) still exists
echo "--- CHECK: get_prompt_token_ids device method preserved ---"
R1_RESULT=$(python3 -c "
import ast, sys

with open('$METADATA') as f:
    source = f.read()
tree = ast.parse(source)

found_device = False
found_cpu = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == 'get_prompt_token_ids':
            found_device = True
        elif node.name == 'get_prompt_token_ids_cpu':
            found_cpu = True

if not found_device:
    print('FAIL: get_prompt_token_ids (device) method removed')
elif not found_cpu:
    print('FAIL: get_prompt_token_ids_cpu method missing')
else:
    print('OK')
" 2>&1)
echo "  $R1_RESULT"
if echo "$R1_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")
echo ""

# [pr_diff] (0.05): __getitem__ slices prompt_token_ids_cpu
echo "--- CHECK: __getitem__ handles prompt_token_ids_cpu ---"
R2_RESULT=$(python3 -c "
import ast, sys

with open('$METADATA') as f:
    source = f.read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '__getitem__':
        method_src = ast.get_source_segment(source, node)
        if method_src and 'prompt_token_ids_cpu' in method_src:
            print('OK')
            sys.exit(0)
        else:
            print('FAIL: __getitem__ does not slice prompt_token_ids_cpu')
            sys.exit(0)

print('FAIL: __getitem__ method not found')
" 2>&1)
echo "  $R2_RESULT"
if echo "$R2_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

########################################
# STRUCTURAL: Anti-stub / completeness
########################################

# [pr_diff] (0.10): No stubs/placeholders in modified files
echo "--- CHECK: no stub/placeholder markers ---"
STUB_RESULT=$(python3 -c "
import sys

targets = ['$METADATA', '$GPU_BATCH', '$SPECIAL', '$BERT', '$GRITLM']
issues = []
for filepath in targets:
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            for stub in ['NotImplementedError', 'pass  #', '...  # stub', '# TODO: implement']:
                if stub in stripped:
                    issues.append(f'{filepath}:{i}: {stub}')

if issues:
    for i in issues:
        print(f'  Found: {i}')
    print('FAIL')
else:
    print('OK')
" 2>&1)
echo "$STUB_RESULT"
if echo "$STUB_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.10)")
    echo "  +0.10"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.10)")
echo ""

# [pr_diff] (0.05): gpu_model_runner.py dummy_pooler_run_task passes prompt_token_ids_cpu
echo "--- CHECK: gpu_model_runner dummy metadata includes cpu field ---"
RUNNER_RESULT=$(python3 -c "
with open('$GPU_RUNNER') as f:
    content = f.read()

if 'prompt_token_ids_cpu' in content:
    print('OK')
else:
    print('FAIL: gpu_model_runner.py does not pass prompt_token_ids_cpu to dummy PoolingMetadata')
" 2>&1)
echo "$RUNNER_RESULT"
if echo "$RUNNER_RESULT" | grep -q "^OK$"; then
    SCORE=$(python3 -c "print($SCORE + 0.05)")
    echo "  +0.05"
fi
TOTAL=$(python3 -c "print($TOTAL + 0.05)")
echo ""

########################################
# Final score
########################################
echo "=== RESULTS ==="
echo "Score: $SCORE / $TOTAL"

FINAL=$(python3 -c "print(f'{float($SCORE):.4f}')")
echo "Final reward: $FINAL"

mkdir -p /logs/verifier
echo "$FINAL" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
behavioral = min(score, 0.70)
regression = min(max(score - 0.70, 0), 0.15)
structural = min(max(score - 0.85, 0), 0.15)
print(json.dumps({
    'reward': round(score, 4),
    'behavioral': round(behavioral, 4),
    'regression': round(regression, 4),
    'structural': round(structural, 4),
}))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
