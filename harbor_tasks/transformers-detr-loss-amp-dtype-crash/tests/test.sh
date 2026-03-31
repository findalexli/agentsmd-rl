#!/usr/bin/env bash
set -euo pipefail

SCORE=0.0
TOTAL=0.0
DETAILS=""

add() {
    local weight=$1 name=$2 pass=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        DETAILS="${DETAILS}PASS ($weight) $name\n"
    else
        DETAILS="${DETAILS}FAIL ($weight) $name\n"
    fi
}

REPO=/repo
LW_FILE="$REPO/src/transformers/loss/loss_lw_detr.py"
RT_FILE="$REPO/src/transformers/loss/loss_rt_detr.py"

# ── GATE: syntax check ──────────────────────────────────────────────
# [pr_diff] (0.00): Both modified files must parse
python3 -c "
import ast, sys
for f in ['$LW_FILE', '$RT_FILE']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'SYNTAX ERROR in {f}: {e}', file=sys.stderr)
        sys.exit(1)
" || { echo "GATE FAILED: syntax error"; echo "0.0" > /logs/verifier/reward.txt; exit 0; }

# ── BEHAVIORAL: fail-to-pass tests (0.65 total) ─────────────────────

# [pr_diff] (0.35): LwDetrImageLoss.loss_labels works with float16 under autocast
PASS=0
python3 -c "
import torch
import torch.nn as nn
import sys
sys.path.insert(0, '$REPO/src')

from transformers.loss.loss_lw_detr import LwDetrImageLoss, LwDetrHungarianMatcher

# Create small test inputs in float16
B, Q, C = 1, 4, 3
logits = torch.randn(B, Q, C, dtype=torch.float16)
pred_boxes = torch.rand(B, Q, 4, dtype=torch.float16)
# Ensure valid box format (x_center, y_center, w, h) with w,h > 0
pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)

targets = [{
    'class_labels': torch.tensor([0, 1]),
    'boxes': torch.tensor([[0.3, 0.3, 0.2, 0.2], [0.6, 0.6, 0.3, 0.3]], dtype=torch.float16),
}]

# Pre-computed indices (bypass matcher/scipy)
indices = [(torch.tensor([0, 1]), torch.tensor([0, 1]))]

# Simulate the dtype promotion that happens under CUDA autocast:
# Monkey-patch pow to return float32 (simulates autocast behavior)
_orig_pow = torch.Tensor.pow
_orig_rpow = torch.Tensor.__pow__

def _promoted_pow(self, exponent):
    result = _orig_pow(self.float(), exponent)
    return result  # Returns float32 even if input was float16

def _promoted_rpow(self, exponent):
    result = _orig_rpow(self.float(), exponent)
    return result

torch.Tensor.pow = _promoted_pow
torch.Tensor.__pow__ = _promoted_rpow

try:
    matcher = type('M', (), {'__call__': lambda s,o,t,g: indices})()
    loss_fn = LwDetrImageLoss(
        matcher=matcher, num_classes=C, focal_alpha=0.25,
        losses=['labels'], group_detr=1,
    )
    loss_fn.eval()

    outputs = {'logits': logits, 'pred_boxes': pred_boxes}
    losses = loss_fn.loss_labels(outputs, targets, indices, num_boxes=2.0)

    assert 'loss_ce' in losses, 'Missing loss_ce key'
    loss_val = losses['loss_ce']
    assert not torch.isnan(loss_val), 'loss_ce is NaN'
    assert not torch.isinf(loss_val), 'loss_ce is Inf'
    print('LwDetr float16 autocast test PASSED')
except Exception as e:
    print(f'LwDetr float16 autocast test FAILED: {e}', file=sys.stderr)
    sys.exit(1)
finally:
    torch.Tensor.pow = _orig_pow
    torch.Tensor.__pow__ = _orig_rpow
" 2>&1 && PASS=1 || true
add 0.35 "LwDetrImageLoss.loss_labels survives dtype promotion from pow" "$PASS"

# [pr_diff] (0.30): RTDetrLoss.loss_labels_vfl works with float16 under autocast
PASS=0
python3 -c "
import torch
import torch.nn as nn
import torch.nn.functional as F
import sys
sys.path.insert(0, '$REPO/src')

from transformers.loss.loss_rt_detr import RTDetrLoss

B, Q, C = 1, 4, 3

logits = torch.randn(B, Q, C, dtype=torch.float16)
pred_boxes = torch.rand(B, Q, 4, dtype=torch.float16)
pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)

targets = [{
    'class_labels': torch.tensor([0, 1]),
    'boxes': torch.tensor([[0.3, 0.3, 0.2, 0.2], [0.6, 0.6, 0.3, 0.3]], dtype=torch.float16),
}]
indices = [(torch.tensor([0, 1]), torch.tensor([0, 1]))]
idx = (torch.tensor([0, 0]), torch.tensor([0, 1]))

# Simulate pow promoting to float32 (as CUDA autocast does)
_orig_pow = torch.Tensor.pow
_orig_rpow = torch.Tensor.__pow__

def _promoted_pow(self, exponent):
    return _orig_pow(self.float(), exponent)

def _promoted_rpow(self, exponent):
    return _orig_rpow(self.float(), exponent)

torch.Tensor.pow = _promoted_pow
torch.Tensor.__pow__ = _promoted_rpow

try:
    # Build a minimal RTDetrLoss with required attributes
    class FakeConfig:
        matcher_class_cost = 2.0
        matcher_bbox_cost = 5.0
        matcher_giou_cost = 2.0
        use_focal_loss = True
        matcher_alpha = 0.25
        matcher_gamma = 2.0
        num_labels = C
        weight_loss_vfl = 1.0
        weight_loss_bbox = 5.0
        weight_loss_giou = 2.0
        eos_coefficient = 0.1
        focal_loss_alpha = 0.75
        focal_loss_gamma = 2.0

    loss_module = RTDetrLoss(FakeConfig())

    outputs = {'logits': logits, 'pred_boxes': pred_boxes}
    losses = loss_module.loss_labels_vfl(outputs, targets, indices, num_boxes=2.0)

    assert 'loss_vfl' in losses, 'Missing loss_vfl key'
    loss_val = losses['loss_vfl']
    assert not torch.isnan(loss_val), 'loss_vfl is NaN'
    assert not torch.isinf(loss_val), 'loss_vfl is Inf'
    print('RTDetr float16 autocast test PASSED')
except Exception as e:
    print(f'RTDetr float16 autocast test FAILED: {e}', file=sys.stderr)
    sys.exit(1)
finally:
    torch.Tensor.pow = _orig_pow
    torch.Tensor.__pow__ = _orig_rpow
" 2>&1 && PASS=1 || true
add 0.30 "RTDetrLoss.loss_labels_vfl survives dtype promotion from pow" "$PASS"

# ── PASS-TO-PASS: float32 still works (0.15 total) ──────────────────

# [pr_diff] (0.08): LwDetrImageLoss.loss_labels with float32 inputs
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, '$REPO/src')
from transformers.loss.loss_lw_detr import LwDetrImageLoss

B, Q, C = 1, 4, 3
logits = torch.randn(B, Q, C)
pred_boxes = torch.rand(B, Q, 4)
pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)
targets = [{'class_labels': torch.tensor([0, 1]),
            'boxes': torch.tensor([[0.3, 0.3, 0.2, 0.2], [0.6, 0.6, 0.3, 0.3]])}]
indices = [(torch.tensor([0, 1]), torch.tensor([0, 1]))]
matcher = type('M', (), {'__call__': lambda s,o,t,g: indices})()
loss_fn = LwDetrImageLoss(matcher=matcher, num_classes=C, focal_alpha=0.25, losses=['labels'], group_detr=1)
outputs = {'logits': logits, 'pred_boxes': pred_boxes}
losses = loss_fn.loss_labels(outputs, targets, indices, 2.0)
assert 'loss_ce' in losses and not torch.isnan(losses['loss_ce'])
print('LwDetr float32 P2P PASSED')
" 2>&1 && PASS=1 || true
add 0.08 "LwDetrImageLoss.loss_labels float32 regression" "$PASS"

# [pr_diff] (0.07): RTDetrLoss.loss_labels_vfl with float32 inputs
PASS=0
python3 -c "
import torch, sys
sys.path.insert(0, '$REPO/src')
from transformers.loss.loss_rt_detr import RTDetrLoss

B, Q, C = 1, 4, 3
logits = torch.randn(B, Q, C)
pred_boxes = torch.rand(B, Q, 4)
pred_boxes[..., 2:] = pred_boxes[..., 2:].abs().clamp(min=0.05)
targets = [{'class_labels': torch.tensor([0, 1]),
            'boxes': torch.tensor([[0.3, 0.3, 0.2, 0.2], [0.6, 0.6, 0.3, 0.3]])}]
indices = [(torch.tensor([0, 1]), torch.tensor([0, 1]))]

class FakeConfig:
    matcher_class_cost = 2.0; matcher_bbox_cost = 5.0; matcher_giou_cost = 2.0
    use_focal_loss = True; matcher_alpha = 0.25; matcher_gamma = 2.0
    num_labels = C; weight_loss_vfl = 1.0; weight_loss_bbox = 5.0; weight_loss_giou = 2.0
    eos_coefficient = 0.1; focal_loss_alpha = 0.75; focal_loss_gamma = 2.0

loss_module = RTDetrLoss(FakeConfig())
outputs = {'logits': logits, 'pred_boxes': pred_boxes}
losses = loss_module.loss_labels_vfl(outputs, targets, indices, 2.0)
assert 'loss_vfl' in losses and not torch.isnan(losses['loss_vfl'])
print('RTDetr float32 P2P PASSED')
" 2>&1 && PASS=1 || true
add 0.07 "RTDetrLoss.loss_labels_vfl float32 regression" "$PASS"

# ── CONFIG-DERIVED: ruff format check (0.10) ────────────────────────

# [agent_config] (0.10): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2
PASS=0
pip install ruff -q 2>/dev/null
if ruff check "$LW_FILE" "$RT_FILE" --select=E,W --quiet 2>&1; then
    PASS=1
fi
add 0.10 "ruff lint passes on modified files" "$PASS"

# ── ANTI-STUB: files are not empty stubs (0.10) ─────────────────────

# [pr_diff] (0.05): loss_lw_detr.py has substantial loss_labels implementation
PASS=0
python3 -c "
import ast, sys
tree = ast.parse(open('$LW_FILE').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'loss_labels':
        # Must have meaningful body (not just pass/return 0)
        body_lines = node.end_lineno - node.lineno
        assert body_lines > 10, f'loss_labels too short: {body_lines} lines'
        print(f'loss_labels has {body_lines} lines — OK')
        sys.exit(0)
print('loss_labels not found', file=sys.stderr)
sys.exit(1)
" 2>&1 && PASS=1 || true
add 0.05 "loss_lw_detr.py loss_labels is not a stub" "$PASS"

# [pr_diff] (0.05): loss_rt_detr.py has substantial loss_labels_vfl implementation
PASS=0
python3 -c "
import ast, sys
tree = ast.parse(open('$RT_FILE').read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'loss_labels_vfl':
        body_lines = node.end_lineno - node.lineno
        assert body_lines > 10, f'loss_labels_vfl too short: {body_lines} lines'
        print(f'loss_labels_vfl has {body_lines} lines — OK')
        sys.exit(0)
print('loss_labels_vfl not found', file=sys.stderr)
sys.exit(1)
" 2>&1 && PASS=1 || true
add 0.05 "loss_rt_detr.py loss_labels_vfl is not a stub" "$PASS"

# ── RESULTS ──────────────────────────────────────────────────────────
echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Total: $SCORE / $TOTAL"

# Write reward
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = $SCORE
data = {
    'reward': score,
    'behavioral': min(0.65, score),
    'regression': 0.0,
    'config': 0.0,
    'style_rubric': 0.0,
}
# Recompute components from details
remaining = score
if remaining >= 0.35:
    data['behavioral'] = 0.35
    remaining -= 0.35
else:
    data['behavioral'] = remaining
    remaining = 0.0
if remaining >= 0.30:
    data['behavioral'] += 0.30
    remaining -= 0.30
elif remaining > 0:
    data['behavioral'] += remaining
    remaining = 0.0
if remaining >= 0.08:
    data['regression'] = 0.08
    remaining -= 0.08
if remaining >= 0.07:
    data['regression'] += 0.07
    remaining -= 0.07
if remaining >= 0.10:
    data['config'] = 0.10
    remaining -= 0.10
print(json.dumps(data))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
