#!/usr/bin/env bash
set +e
set -uo pipefail

REPO="/workspace/sglang"
SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" desc="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}\nPASS ($weight): $desc"
    else
        DETAILS="${DETAILS}\nFAIL ($weight): $desc"
    fi
}

# ============================================================
# GATE: Syntax check — abort on failure
# ============================================================
# [pr_diff] (0): Both changed files must parse without syntax errors
python3 -c "
import ast, sys
for f in ['python/sglang/srt/lora/utils.py', 'python/sglang/srt/lora/lora_manager.py']:
    try:
        ast.parse(open('$REPO/' + f).read())
    except SyntaxError as e:
        print(f'Syntax error in {f}: {e}', file=sys.stderr)
        sys.exit(1)
" 2>&1
if [ $? -ne 0 ]; then
    echo "GATE FAILED: Syntax error in modified files"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi

# ============================================================
# FAIL-TO-PASS: Behavioral tests (0.70 total)
# ============================================================

# [pr_diff] (0.25): auto_detect_lora_target_modules returns correct modules for a dense model
# Builds a mock model with known module types and verifies detected set
DETECT_DENSE=$(python3 -c "
import torch
import torch.nn as nn
from unittest.mock import patch

class MockLinearBase(nn.Module):
    pass

class MockFusedMoE(nn.Module):
    pass

class MockParallelLMHead(nn.Module):
    pass

# Dense transformer mock: attention + MLP + embed + lm_head
model = nn.Module()
inner = nn.Module()
layer = nn.Module()

attn = nn.Module()
attn.qkv_proj = MockLinearBase()
attn.o_proj = MockLinearBase()
layer.self_attn = attn

mlp = nn.Module()
mlp.gate_up_proj = MockLinearBase()
mlp.down_proj = MockLinearBase()
layer.mlp = mlp

inner.layers = nn.ModuleList([layer])
inner.embed_tokens = nn.Embedding(10, 8)  # NOT LinearBase
model.model = inner
model.lm_head = MockParallelLMHead()

with patch('sglang.srt.layers.linear.LinearBase', MockLinearBase), \
     patch('sglang.srt.layers.moe.fused_moe_triton.layer.FusedMoE', MockFusedMoE), \
     patch('sglang.srt.layers.vocab_parallel_embedding.ParallelLMHead', MockParallelLMHead):
    from sglang.srt.lora.utils import auto_detect_lora_target_modules
    detected = auto_detect_lora_target_modules(model)

expected = {'qkv_proj', 'o_proj', 'gate_up_proj', 'down_proj', 'lm_head'}
if detected == expected:
    print('PASS')
else:
    print(f'FAIL: detected={sorted(detected)}, expected={sorted(expected)}')
" 2>&1)
if echo "$DETECT_DENSE" | grep -q "^PASS$"; then
    add_result 0.25 1 "auto_detect returns correct modules for dense model"
else
    echo "detect_dense detail: $DETECT_DENSE"
    add_result 0.25 0 "auto_detect returns correct modules for dense model"
fi

# [pr_diff] (0.15): auto_detect returns only matching modules when model has single known module
# A hardcoded stub cannot pass both this AND the dense model test above
DETECT_SINGLE=$(python3 -c "
import torch
import torch.nn as nn
from unittest.mock import patch

class MockLinearBase(nn.Module):
    pass

class MockFusedMoE(nn.Module):
    pass

class MockParallelLMHead(nn.Module):
    pass

# Model with only a single known linear module
model = nn.Module()
inner = nn.Module()
layer = nn.Module()
attn = nn.Module()
attn.o_proj = MockLinearBase()
layer.self_attn = attn
inner.layers = nn.ModuleList([layer])
model.model = inner

with patch('sglang.srt.layers.linear.LinearBase', MockLinearBase), \
     patch('sglang.srt.layers.moe.fused_moe_triton.layer.FusedMoE', MockFusedMoE), \
     patch('sglang.srt.layers.vocab_parallel_embedding.ParallelLMHead', MockParallelLMHead):
    from sglang.srt.lora.utils import auto_detect_lora_target_modules
    detected = auto_detect_lora_target_modules(model)

if detected == {'o_proj'}:
    print('PASS')
else:
    print(f'FAIL: detected={sorted(detected)}, expected=[\"o_proj\"]')
" 2>&1)
if echo "$DETECT_SINGLE" | grep -q "^PASS$"; then
    add_result 0.15 1 "auto_detect returns only matching modules for single-module model"
else
    echo "detect_single detail: $DETECT_SINGLE"
    add_result 0.15 0 "auto_detect returns only matching modules for single-module model"
fi

# [pr_diff] (0.10): auto_detect filters out unknown module names (only returns known LoRA targets)
DETECT_FILTER=$(python3 -c "
import torch
import torch.nn as nn
from unittest.mock import patch

class MockLinearBase(nn.Module):
    pass

class MockFusedMoE(nn.Module):
    pass

class MockParallelLMHead(nn.Module):
    pass

# Model with ONLY unknown-named linear modules
model = nn.Module()
layer = nn.Module()
layer.weird_custom_proj = MockLinearBase()
layer.another_unknown = MockLinearBase()
model.layers = nn.ModuleList([layer])

with patch('sglang.srt.layers.linear.LinearBase', MockLinearBase), \
     patch('sglang.srt.layers.moe.fused_moe_triton.layer.FusedMoE', MockFusedMoE), \
     patch('sglang.srt.layers.vocab_parallel_embedding.ParallelLMHead', MockParallelLMHead):
    from sglang.srt.lora.utils import auto_detect_lora_target_modules
    detected = auto_detect_lora_target_modules(model)

# Should return empty — no known module names match
if detected == set():
    print('PASS')
elif 'weird_custom_proj' in detected or 'another_unknown' in detected:
    print(f'FAIL: unknown modules not filtered: {sorted(detected)}')
else:
    print(f'FAIL: unexpected result: {sorted(detected)}')
" 2>&1)
if echo "$DETECT_FILTER" | grep -q "^PASS$"; then
    add_result 0.10 1 "auto_detect returns empty set when model has no known modules"
else
    echo "detect_filter detail: $DETECT_FILTER"
    add_result 0.10 0 "auto_detect returns empty set when model has no known modules"
fi

# [pr_diff] (0.10): auto_detect includes lm_head when model has ParallelLMHead
DETECT_LMHEAD=$(python3 -c "
import torch
import torch.nn as nn
from unittest.mock import patch

class MockLinearBase(nn.Module):
    pass

class MockFusedMoE(nn.Module):
    pass

class MockParallelLMHead(nn.Module):
    pass

# Model with only lm_head (ParallelLMHead type)
model = nn.Module()
inner = nn.Module()
inner.layers = nn.ModuleList([])
model.model = inner
model.lm_head = MockParallelLMHead()

with patch('sglang.srt.layers.linear.LinearBase', MockLinearBase), \
     patch('sglang.srt.layers.moe.fused_moe_triton.layer.FusedMoE', MockFusedMoE), \
     patch('sglang.srt.layers.vocab_parallel_embedding.ParallelLMHead', MockParallelLMHead):
    from sglang.srt.lora.utils import auto_detect_lora_target_modules
    detected = auto_detect_lora_target_modules(model)

if 'lm_head' in detected:
    print('PASS')
else:
    print(f'FAIL: lm_head not detected: {sorted(detected)}')
" 2>&1)
if echo "$DETECT_LMHEAD" | grep -q "^PASS$"; then
    add_result 0.10 1 "auto_detect includes lm_head for ParallelLMHead module"
else
    echo "detect_lmhead detail: $DETECT_LMHEAD"
    add_result 0.10 0 "auto_detect includes lm_head for ParallelLMHead module"
fi

# [pr_diff] (0.10): init_lora_shapes no longer raises ValueError for 'all-linear' target_modules
# WHY AST: init_lora_shapes is a method on LoRAManager requiring full model/adapter state.
# We check AST nodes (not string search) to verify the ValueError raise is removed.
SHAPES_RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/python/sglang/srt/lora/lora_manager.py').read()
tree = ast.parse(source)

# Find init_lora_shapes function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'init_lora_shapes':
        func_node = node
        break

if func_node is None:
    print('FAIL: init_lora_shapes not found')
    sys.exit(0)

# Walk the function body looking for Raise(ValueError(...)) nodes
# whose message mentions 'cannot be resolved automatically'
has_old_raise = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Raise) and node.exc is not None:
        # Check if it's ValueError(...)
        exc = node.exc
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == 'ValueError':
            for arg in exc.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if 'cannot be resolved automatically' in arg.value:
                        has_old_raise = True
                # Also check f-strings (JoinedStr)
                if isinstance(arg, ast.JoinedStr):
                    for val in arg.values:
                        if isinstance(val, ast.Constant) and isinstance(val.value, str):
                            if 'cannot be resolved automatically' in val.value:
                                has_old_raise = True

if has_old_raise:
    print('FAIL: still raises ValueError for all-linear')
else:
    print('PASS')
" 2>&1)
if echo "$SHAPES_RESULT" | grep -q "^PASS$"; then
    add_result 0.10 1 "init_lora_shapes no longer raises ValueError for all-linear"
else
    echo "shapes detail: $SHAPES_RESULT"
    add_result 0.10 0 "init_lora_shapes no longer raises ValueError for all-linear"
fi

# ============================================================
# PASS-TO-PASS: Existing functionality must not break (0.10)
# ============================================================

# [pr_diff] (0.05): get_normalized_target_modules still works for list inputs
P2P_NORM=$(python3 -c "
from sglang.srt.lora.utils import get_normalized_target_modules
result = get_normalized_target_modules(['q_proj', 'v_proj', 'gate_proj', 'down_proj'])
expected = {'qkv_proj', 'gate_up_proj', 'down_proj'}
if result == expected:
    print('PASS')
else:
    print(f'FAIL: {result} != {expected}')
" 2>&1)
if echo "$P2P_NORM" | grep -q "^PASS$"; then
    add_result 0.05 1 "get_normalized_target_modules normalizes list inputs correctly"
else
    echo "p2p_norm detail: $P2P_NORM"
    add_result 0.05 0 "get_normalized_target_modules normalizes list inputs correctly"
fi

# [pr_diff] (0.05): get_normalized_target_modules returns sentinel for 'all-linear' string
P2P_SENTINEL=$(python3 -c "
from sglang.srt.lora.utils import get_normalized_target_modules
result = get_normalized_target_modules('all-linear')
if result == {'all'}:
    print('PASS')
else:
    print(f'FAIL: {result}')
" 2>&1)
if echo "$P2P_SENTINEL" | grep -q "^PASS$"; then
    add_result 0.05 1 "get_normalized_target_modules returns sentinel for 'all-linear'"
else
    echo "p2p_sentinel detail: $P2P_SENTINEL"
    add_result 0.05 0 "get_normalized_target_modules returns sentinel for 'all-linear'"
fi

# ============================================================
# STRUCTURAL: Anti-stub / validation (0.15)
# ============================================================

# [pr_diff] (0.10): init_lora_modules handles get_layer_id returning None
# WHY AST: init_lora_modules requires a fully initialized LoRAManager with loaded
# base model and adapters. We use AST node inspection (not string search) to verify
# a None guard exists for layer_id.
LAYER_ID_RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/python/sglang/srt/lora/lora_manager.py').read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'init_lora_modules':
        func_node = node
        break

if func_node is None:
    print('FAIL: init_lora_modules not found')
    sys.exit(0)

# Look for any comparison involving None that guards layer_id usage.
# Valid patterns:
#   if layer_id is None: ...
#   if layer_id is not None: ...
#   if layer_id == None: ...
#   if layer_id != None: ...
# We check for Compare nodes with a None comparator and an operand named 'layer_id'
has_none_guard = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Compare):
        # Check left operand
        left_is_layer_id = isinstance(node.left, ast.Name) and node.left.id == 'layer_id'
        # Check comparators for None
        has_none_comp = any(
            isinstance(c, ast.Constant) and c.value is None
            for c in node.comparators
        )
        if left_is_layer_id and has_none_comp:
            has_none_guard = True
            break
        # Also check if None is on the left and layer_id in comparators
        left_is_none = isinstance(node.left, ast.Constant) and node.left.value is None
        comp_is_layer_id = any(
            isinstance(c, ast.Name) and c.id == 'layer_id'
            for c in node.comparators
        )
        if left_is_none and comp_is_layer_id:
            has_none_guard = True
            break
    # Also handle try/except that catches TypeError or IndexError around layer_id
    if isinstance(node, ast.Try):
        for handler in node.handlers:
            if handler.type is not None:
                if isinstance(handler.type, ast.Name) and handler.type.id in ('TypeError', 'IndexError'):
                    # Check if the try body uses layer_id
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name) and child.id == 'layer_id':
                            has_none_guard = True
                            break
                elif isinstance(handler.type, ast.Tuple):
                    for elt in handler.type.elts:
                        if isinstance(elt, ast.Name) and elt.id in ('TypeError', 'IndexError'):
                            for child in ast.walk(node):
                                if isinstance(child, ast.Name) and child.id == 'layer_id':
                                    has_none_guard = True
                                    break

if has_none_guard:
    print('PASS')
else:
    print('FAIL: no None guard for layer_id in init_lora_modules')
" 2>&1)
if echo "$LAYER_ID_RESULT" | grep -q "^PASS$"; then
    add_result 0.10 1 "init_lora_modules guards against get_layer_id returning None"
else
    echo "layer_id detail: $LAYER_ID_RESULT"
    add_result 0.10 0 "init_lora_modules guards against get_layer_id returning None"
fi

# [pr_diff] (0.05): auto_detect function has non-trivial body (anti-stub)
ANTISTUB_RESULT=$(python3 -c "
import ast, sys

source = open('$REPO/python/sglang/srt/lora/utils.py').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'auto_detect_lora_target_modules':
        # Count meaningful statements (not docstrings, not pass, not comments)
        meaningful = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign,
                                  ast.For, ast.If, ast.Return, ast.With)):
                meaningful += 1
        if meaningful >= 4:
            print('PASS')
        else:
            print(f'FAIL: only {meaningful} meaningful statements (stub?)')
        break
else:
    print('FAIL: auto_detect_lora_target_modules not found')
" 2>&1)
if echo "$ANTISTUB_RESULT" | grep -q "^PASS$"; then
    add_result 0.05 1 "auto_detect_lora_target_modules has non-trivial implementation"
else
    echo "antistub detail: $ANTISTUB_RESULT"
    add_result 0.05 0 "auto_detect_lora_target_modules has non-trivial implementation"
fi

# ============================================================
# CONFIG-DERIVED (0.05)
# ============================================================

# [agent_config] (0.05): "Always use CustomTestCase" — .claude/skills/write-sglang-test/SKILL.md:12-16 @ 9b29131
# Verify the new function is properly importable from the utils module
CONFIG_RESULT=$(python3 -c "
import importlib
mod = importlib.import_module('sglang.srt.lora.utils')
if hasattr(mod, 'auto_detect_lora_target_modules') and callable(mod.auto_detect_lora_target_modules):
    print('PASS')
else:
    print('FAIL: auto_detect_lora_target_modules not properly exported')
" 2>&1)
if echo "$CONFIG_RESULT" | grep -q "^PASS$"; then
    add_result 0.05 1 "auto_detect_lora_target_modules is properly exported from utils"
else
    echo "config detail: $CONFIG_RESULT"
    add_result 0.05 0 "auto_detect_lora_target_modules is properly exported from utils"
fi

# ============================================================
# SUMMARY
# ============================================================

echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo ""
echo "Score: $SCORE / $TOTAL"

# Normalize to 1.0
FINAL=$(python3 -c "print(round($SCORE, 4))")
echo ""
echo "Final reward: $FINAL"
echo "$FINAL" > /logs/verifier/reward.txt

python3 -c "
import json
score = $SCORE
data = {
    'reward': round(score, 4),
    'behavioral': round(min(score, 0.70), 4),
    'regression': round(min(max(score - 0.70, 0), 0.10), 4),
    'structural': round(min(max(score - 0.80, 0), 0.15), 4),
    'config': round(min(max(score - 0.95, 0), 0.05), 4),
    'style_rubric': 0.0
}
print(json.dumps(data))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
