#!/usr/bin/env bash
set +e

REWARD=0

cd /repo

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0): Python syntax valid on all changed files
python3 -c "
import py_compile, sys
for f in [
    'src/transformers/integrations/moe.py',
    'src/transformers/conversion_mapping.py',
    'src/transformers/core_model_loading.py',
]:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'GATE FAIL: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

###############################################################################
# Helper to detect grouped_mm availability (reused across checks)
###############################################################################
HAS_GMM=$(python3 -c "
import torch
if hasattr(torch.nn.functional, 'grouped_mm') or hasattr(torch, '_grouped_mm'):
    print('yes')
else:
    print('no')
" 2>/dev/null)

###############################################################################
# Fail-to-pass: misaligned weight tensor returns False
###############################################################################
# [pr_diff] (0.20): misaligned weight tensor on CPU triggers fallback
if [ "$HAS_GMM" = "yes" ]; then
    python3 -c "
import torch, sys
from transformers.integrations.moe import _can_use_grouped_mm

# Create a misaligned weight tensor (offset by 2 bytes from bfloat16 element)
buf = torch.zeros(200, dtype=torch.bfloat16)
misaligned_weight = buf[1:129].reshape(16, 8)
assert misaligned_weight.data_ptr() % 16 != 0, 'Test setup error: weight should be misaligned'

aligned_input = torch.randn(1, 8, dtype=torch.bfloat16)
offs = torch.tensor([1], dtype=torch.int32)

result = _can_use_grouped_mm(aligned_input, misaligned_weight, offs)
assert result == False, f'Expected False for misaligned weight on CPU, got {result}'
print('OK: misaligned weight detected')
" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS (0.20): misaligned weight triggers fallback"
        REWARD=$(python3 -c "print(round($REWARD + 0.20, 4))")
    else
        echo "FAIL (0.20): misaligned weight not detected"
    fi
else
    echo "SKIP (0.20): grouped_mm not available"
fi

###############################################################################
# Fail-to-pass: misaligned input tensor returns False
###############################################################################
# [pr_diff] (0.15): misaligned input tensor on CPU triggers fallback
if [ "$HAS_GMM" = "yes" ]; then
    python3 -c "
import torch, sys
from transformers.integrations.moe import _can_use_grouped_mm

# Create a misaligned input tensor
buf = torch.zeros(200, dtype=torch.bfloat16)
misaligned_input = buf[1:17].reshape(2, 8)
assert misaligned_input.data_ptr() % 16 != 0, 'Test setup error: input should be misaligned'

aligned_weight = torch.randn(16, 8, dtype=torch.bfloat16)
offs = torch.tensor([2], dtype=torch.int32)

result = _can_use_grouped_mm(misaligned_input, aligned_weight, offs)
assert result == False, f'Expected False for misaligned input on CPU, got {result}'
print('OK: misaligned input detected')
" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS (0.15): misaligned input triggers fallback"
        REWARD=$(python3 -c "print(round($REWARD + 0.15, 4))")
    else
        echo "FAIL (0.15): misaligned input not detected"
    fi
else
    echo "SKIP (0.15): grouped_mm not available"
fi

###############################################################################
# Pass-to-pass: aligned tensors on CPU must still return True
###############################################################################
# [pr_diff] (0.20): aligned CPU tensors still allow grouped_mm
if [ "$HAS_GMM" = "yes" ]; then
    python3 -c "
import torch, sys
from transformers.integrations.moe import _can_use_grouped_mm

aligned_input = torch.randn(2, 8, dtype=torch.bfloat16)
aligned_weight = torch.randn(16, 8, dtype=torch.bfloat16)
offs = torch.tensor([2], dtype=torch.int32)

assert aligned_input.data_ptr() % 16 == 0, 'Test setup error: input should be aligned'
assert aligned_weight.data_ptr() % 16 == 0, 'Test setup error: weight should be aligned'

result = _can_use_grouped_mm(aligned_input, aligned_weight, offs)
assert result == True, f'Expected True for aligned CPU tensors, got {result}'
print('OK: aligned tensors still use grouped_mm')
" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS (0.20): aligned tensors still use grouped_mm"
        REWARD=$(python3 -c "print(round($REWARD + 0.20, 4))")
    else
        echo "FAIL (0.20): aligned tensors incorrectly rejected"
    fi
else
    echo "SKIP (0.20): grouped_mm not available"
fi

###############################################################################
# Fail-to-pass: Differentiation — function has conditional logic, not constant
###############################################################################
# [pr_diff] (0.15): function distinguishes aligned from misaligned tensors
if [ "$HAS_GMM" = "yes" ]; then
    python3 -c "
import torch, sys
from transformers.integrations.moe import _can_use_grouped_mm

# Test 1: aligned tensors should return True
aligned_input = torch.randn(2, 8, dtype=torch.bfloat16)
aligned_weight = torch.randn(16, 8, dtype=torch.bfloat16)
offs = torch.tensor([2], dtype=torch.int32)
assert aligned_input.data_ptr() % 16 == 0
assert aligned_weight.data_ptr() % 16 == 0
result_aligned = _can_use_grouped_mm(aligned_input, aligned_weight, offs)

# Test 2: misaligned tensors should return False
buf = torch.zeros(200, dtype=torch.bfloat16)
misaligned_w = buf[1:129].reshape(16, 8)
assert misaligned_w.data_ptr() % 16 != 0
result_misaligned = _can_use_grouped_mm(aligned_input, misaligned_w, offs)

# The function must differentiate: True for aligned, False for misaligned
assert result_aligned == True and result_misaligned == False, \
    f'Function must differentiate aligned/misaligned: got aligned={result_aligned}, misaligned={result_misaligned}'
print('OK: function differentiates aligned from misaligned')
" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS (0.15): function differentiates aligned from misaligned"
        REWARD=$(python3 -c "print(round($REWARD + 0.15, 4))")
    else
        echo "FAIL (0.15): function does not differentiate aligned from misaligned"
    fi
else
    echo "SKIP (0.15): grouped_mm not available"
fi

###############################################################################
# Fail-to-pass: Force16BytesAlignment removed from conversion_mapping
###############################################################################
# [pr_diff] (0.10): conversion_mapping no longer uses the fragile alignment op
python3 -c "
from transformers.conversion_mapping import _build_checkpoint_conversion_mapping
mappings = _build_checkpoint_conversion_mapping()

from transformers.core_model_loading import WeightConverter
for model_name, converters in mappings.items():
    if isinstance(converters, list):
        for conv in converters:
            if isinstance(conv, WeightConverter) and conv.operations:
                for op in conv.operations:
                    cls_name = type(op).__name__
                    assert cls_name != 'Force16BytesAlignment', \
                        f'Force16BytesAlignment still used in {model_name}'
print('OK: no Force16BytesAlignment in conversion mappings')
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS (0.10): Force16BytesAlignment removed from conversion mappings"
    REWARD=$(python3 -c "print(round($REWARD + 0.10, 4))")
else
    echo "FAIL (0.10): Force16BytesAlignment still in conversion mappings"
fi

###############################################################################
# Pass-to-pass: conversion_mapping builds without error
###############################################################################
# [pr_diff] (0.10): weight conversion mapping loads cleanly
python3 -c "
from transformers.conversion_mapping import _build_checkpoint_conversion_mapping
mappings = _build_checkpoint_conversion_mapping()
assert len(mappings) > 0, 'Empty mappings'
assert 'mixtral' in mappings, 'mixtral missing from mappings'
assert 'qwen3_moe' in mappings, 'qwen3_moe missing from mappings'
print(f'OK: {len(mappings)} model mappings loaded')
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS (0.10): conversion mapping builds cleanly"
    REWARD=$(python3 -c "print(round($REWARD + 0.10, 4))")
else
    echo "FAIL (0.10): conversion mapping build error"
fi

###############################################################################
# Config-derived: ruff check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ b3d7942
if command -v ruff &>/dev/null; then
    ruff check src/transformers/integrations/moe.py src/transformers/conversion_mapping.py src/transformers/core_model_loading.py --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "PASS (0.05): ruff check passes"
        REWARD=$(python3 -c "print(round($REWARD + 0.05, 4))")
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    echo "SKIP (0.05): ruff not installed, awarding points"
    REWARD=$(python3 -c "print(round($REWARD + 0.05, 4))")
fi

###############################################################################
# Anti-stub: _can_use_grouped_mm has substantive logic
###############################################################################
# [pr_diff] (0.05): function has real alignment check logic, not a trivial stub
python3 -c "
import ast, sys
with open('src/transformers/integrations/moe.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_can_use_grouped_mm':
        # Filter out docstrings
        body = [n for n in node.body
                if not (isinstance(n, ast.Expr) and isinstance(getattr(n, 'value', None), (ast.Constant, ast.Str)))]
        # A proper fix needs: compile check + alignment checks + return(s)
        # Minimum 4 meaningful statements to not be a trivial stub
        assert len(body) >= 4, f'Function body too short ({len(body)} stmts), likely a stub'
        print(f'OK: _can_use_grouped_mm has {len(body)} statements')
        sys.exit(0)
print('Function _can_use_grouped_mm not found', file=sys.stderr)
sys.exit(1)
" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "PASS (0.05): _can_use_grouped_mm has real implementation"
    REWARD=$(python3 -c "print(round($REWARD + 0.05, 4))")
else
    echo "FAIL (0.05): _can_use_grouped_mm is missing or a stub"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
