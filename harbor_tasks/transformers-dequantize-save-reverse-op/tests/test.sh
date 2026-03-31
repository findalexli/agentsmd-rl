#!/usr/bin/env bash
set -uo pipefail

TOTAL="0.00"
add() { TOTAL=$(python3 -c "print(f'{float(\"$TOTAL\") + float(\"$1\"):.2f}')"); }

###############################################################################
# GATE: Syntax check on all four changed files
###############################################################################
# [pr_diff] (gate): All modified files must parse without syntax errors
GATE_PASS=true
for f in \
    src/transformers/core_model_loading.py \
    src/transformers/integrations/finegrained_fp8.py \
    src/transformers/integrations/metal_quantization.py \
    src/transformers/integrations/mxfp4.py; do
    if ! python3 -c "import ast; ast.parse(open('/repo/$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=false
    fi
done

if [ "$GATE_PASS" = false ]; then
    echo "0.00" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS: All files parse cleanly"

###############################################################################
# Fail-to-pass 1: Fp8Dequantize.reverse_op doesn't raise NotImplementedError
###############################################################################
# [pr_diff] (0.20): Fp8Dequantize must implement reverse_op without error
if python3 -c "
import sys
sys.path.insert(0, '/repo/src')
from transformers.integrations.finegrained_fp8 import Fp8Dequantize
from transformers.core_model_loading import ConversionOps

# Create instance with a mock quantizer
class MockQuantizer:
    class quantization_config:
        weight_block_size = None
obj = Fp8Dequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), 'reverse_op must return a ConversionOps instance'
# Verify passthrough behavior
test_data = {'layer.weight': 'test_tensor'}
result = rev.convert(test_data)
assert result is test_data, 'reverse_op.convert must pass through input unchanged'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.20): Fp8Dequantize.reverse_op works"
    add 0.20
else
    echo "FAIL (0.20): Fp8Dequantize.reverse_op raises or missing"
fi

###############################################################################
# Fail-to-pass 2: MetalDequantize.reverse_op doesn't raise NotImplementedError
###############################################################################
# [pr_diff] (0.20): MetalDequantize must implement reverse_op without error
if python3 -c "
import sys
sys.path.insert(0, '/repo/src')
from transformers.integrations.metal_quantization import MetalDequantize
from transformers.core_model_loading import ConversionOps

class MockQuantizer:
    class quantization_config:
        bits = 4
        group_size = 32
obj = MetalDequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), 'reverse_op must return a ConversionOps instance'
test_data = {'layer.weight': 'test_tensor'}
result = rev.convert(test_data)
assert result is test_data, 'reverse_op.convert must pass through input unchanged'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.20): MetalDequantize.reverse_op works"
    add 0.20
else
    echo "FAIL (0.20): MetalDequantize.reverse_op raises or missing"
fi

###############################################################################
# Fail-to-pass 3: Mxfp4Dequantize.reverse_op doesn't raise NotImplementedError
###############################################################################
# [pr_diff] (0.20): Mxfp4Dequantize must implement reverse_op without error
if python3 -c "
import sys
sys.path.insert(0, '/repo/src')
from transformers.integrations.mxfp4 import Mxfp4Dequantize
from transformers.core_model_loading import ConversionOps

class MockQuantizer:
    class quantization_config:
        pass
obj = Mxfp4Dequantize(MockQuantizer())
rev = obj.reverse_op
assert isinstance(rev, ConversionOps), 'reverse_op must return a ConversionOps instance'
test_data = {'layer.weight': 'test_tensor'}
result = rev.convert(test_data)
assert result is test_data, 'reverse_op.convert must pass through input unchanged'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.20): Mxfp4Dequantize.reverse_op works"
    add 0.20
else
    echo "FAIL (0.20): Mxfp4Dequantize.reverse_op raises or missing"
fi

###############################################################################
# Fail-to-pass 4: reverse_op.convert preserves dict keys and values exactly
###############################################################################
# [pr_diff] (0.10): reverse_op must be a true identity — preserve all keys/values
if python3 -c "
import sys, torch
sys.path.insert(0, '/repo/src')
from transformers.integrations.finegrained_fp8 import Fp8Dequantize

class MockQuantizer:
    class quantization_config:
        weight_block_size = None

obj = Fp8Dequantize(MockQuantizer())
rev = obj.reverse_op

# Test with realistic tensor dict
t = torch.randn(4, 4)
data = {'model.layer.0.weight': t, 'model.layer.0.bias': torch.zeros(4)}
result = rev.convert(data)
assert set(result.keys()) == set(data.keys()), 'Keys must be preserved'
assert torch.equal(result['model.layer.0.weight'], t), 'Tensor values must be identical'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): reverse_op identity preserves tensor data"
    add 0.10
else
    echo "FAIL (0.10): reverse_op does not preserve tensor data"
fi

###############################################################################
# Pass-to-pass: ConversionOps subclasses with existing reverse_op still work
###############################################################################
# [pr_diff] (0.10): Existing Chunk/Cat reverse_op must not be broken
if python3 -c "
import sys
sys.path.insert(0, '/repo/src')
from transformers.core_model_loading import Chunk, Cat

# Chunk's reverse is Cat and vice versa
chunk = Chunk(dim=0)
rev = chunk.reverse_op
assert isinstance(rev, Cat), f'Chunk.reverse_op should be Cat, got {type(rev)}'

cat = Cat(dim=0)
rev2 = cat.reverse_op
assert isinstance(rev2, Chunk), f'Cat.reverse_op should be Chunk, got {type(rev2)}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): Existing Chunk/Cat reverse_op unchanged"
    add 0.10
else
    echo "FAIL (0.10): Existing Chunk/Cat reverse_op broken"
fi

###############################################################################
# Anti-stub: reverse_op property must not just return None
###############################################################################
# [pr_diff] (0.05): reverse_op must return actual ConversionOps, not None
if python3 -c "
import sys
sys.path.insert(0, '/repo/src')
from transformers.integrations.finegrained_fp8 import Fp8Dequantize
from transformers.integrations.metal_quantization import MetalDequantize
from transformers.integrations.mxfp4 import Mxfp4Dequantize

class MQ:
    class quantization_config:
        weight_block_size = None
        bits = 4
        group_size = 32

for cls in [Fp8Dequantize, MetalDequantize, Mxfp4Dequantize]:
    obj = cls(MQ())
    rev = obj.reverse_op
    assert rev is not None, f'{cls.__name__}.reverse_op returned None'
    assert hasattr(rev, 'convert'), f'{cls.__name__}.reverse_op has no convert method'
    assert callable(rev.convert), f'{cls.__name__}.reverse_op.convert not callable'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): reverse_op returns real objects, not None"
    add 0.05
else
    echo "FAIL (0.05): reverse_op returned None or lacks convert()"
fi

###############################################################################
# Config-derived: ruff check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 12b6b57
if command -v ruff &>/dev/null; then
    if ruff check \
        /repo/src/transformers/core_model_loading.py \
        /repo/src/transformers/integrations/finegrained_fp8.py \
        /repo/src/transformers/integrations/metal_quantization.py \
        /repo/src/transformers/integrations/mxfp4.py \
        --quiet 2>/dev/null; then
        echo "PASS (0.05): ruff check passes"
        add 0.05
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    echo "SKIP (0.05): ruff not installed, awarding points"
    add 0.05
fi

###############################################################################
# Config-derived: no Copied-from blocks edited
###############################################################################
# [agent_config] (0.05): "Do not edit a # Copied from block" — CLAUDE.md:66 @ 12b6b57
if python3 -c "
import subprocess, re
diff = subprocess.run(['git', 'diff', 'HEAD'], cwd='/repo', capture_output=True, text=True).stdout
if not diff:
    diff = subprocess.run(['git', 'diff', '--cached'], cwd='/repo', capture_output=True, text=True).stdout
if not diff:
    diff = subprocess.run(['git', 'diff', 'HEAD~1'], cwd='/repo', capture_output=True, text=True).stdout

# Check that no hunk modifies a '# Copied from' block
in_hunk = False
for line in diff.splitlines():
    if line.startswith('@@'):
        in_hunk = True
    elif line.startswith('diff --git'):
        in_hunk = False
    elif in_hunk and (line.startswith('+') or line.startswith('-')):
        content = line[1:]
        if '# Copied from' in content:
            print('FAIL: diff modifies a Copied-from block')
            exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): No Copied-from blocks modified"
    add 0.05
else
    echo "FAIL (0.05): A Copied-from block was modified"
fi

###############################################################################
# Structural: no modular files edited
###############################################################################
# [agent_config] (0.05): "When a modular file is present, generated files should not be edited" — CLAUDE.md:67 @ 12b6b57
if python3 -c "
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], cwd='/repo', capture_output=True, text=True)
files = result.stdout.strip()
if not files:
    result = subprocess.run(['git', 'diff', '--name-only', '--cached'], cwd='/repo', capture_output=True, text=True)
    files = result.stdout.strip()
if not files:
    result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'], cwd='/repo', capture_output=True, text=True)
    files = result.stdout.strip()

import os
for f in files.splitlines():
    if not f.strip():
        continue
    dirname = os.path.dirname(f)
    basename = os.path.basename(f)
    # Check if there's a modular_ file in the same directory that generates this file
    if basename.startswith('modeling_'):
        modular = os.path.join('/repo', dirname, 'modular_' + basename.replace('modeling_', ''))
        if os.path.exists(modular):
            print(f'FAIL: {f} has a modular source and should not be edited directly')
            exit(1)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): No auto-generated modular files edited"
    add 0.05
else
    echo "FAIL (0.05): An auto-generated modeling file was edited directly"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
