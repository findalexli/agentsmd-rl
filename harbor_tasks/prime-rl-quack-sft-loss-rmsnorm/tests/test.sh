#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

pass() { SCORE=$(python3 -c "print($SCORE + $1)"); TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "  PASS ($1): $2"; }
fail() { TOTAL=$(python3 -c "print($TOTAL + $1)"); echo "  FAIL ($1): $2"; }

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): All modified Python files must parse
for f in src/prime_rl/configs/sft.py \
         src/prime_rl/trainer/model.py \
         src/prime_rl/trainer/models/layers/lm_head.py \
         src/prime_rl/trainer/models/layers/norms.py \
         src/prime_rl/trainer/sft/train.py; do
    if [ -f "$f" ] && ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAILED: $f has syntax errors"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward":0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done
echo "  Gate passed."

echo ""
echo "=== Behavioral: Quack fused CE output linear class ==="
# [pr_diff] (0.15): New quack fused CE class exists, has correct interface, labels=None returns logits
python3 -c "
import torch
from prime_rl.trainer.models.layers.lm_head import QuackFusedCrossEntropyOutputLinear, FUSED_CE_IGNORE_INDEX

# Class exists and is a torch.nn.Linear subclass
assert issubclass(QuackFusedCrossEntropyOutputLinear, torch.nn.Linear)

# Has correct IGNORE_INDEX
assert QuackFusedCrossEntropyOutputLinear.IGNORE_INDEX == -100
assert FUSED_CE_IGNORE_INDEX == -100

# labels=None path returns logits (CPU, no quack needed)
layer = QuackFusedCrossEntropyOutputLinear(in_features=16, out_features=32)
hidden = torch.randn(2, 4, 16)
out = layer(hidden, labels=None)
assert 'logits' in out, 'labels=None should return logits'
assert out['logits'].shape == (2, 4, 32), f'wrong shape: {out[\"logits\"].shape}'
print('OK')
" 2>&1 && pass 0.15 "QuackFusedCrossEntropyOutputLinear class and labels=None path" \
       || fail 0.15 "QuackFusedCrossEntropyOutputLinear class and labels=None path"

echo ""
echo "=== Behavioral: QuackFusedCE labels path attempts quack import ==="
# [pr_diff] (0.10): When labels are provided, the forward path invokes quack chunked_linear_cross_entropy
python3 -c "
import torch
from prime_rl.trainer.models.layers.lm_head import QuackFusedCrossEntropyOutputLinear

layer = QuackFusedCrossEntropyOutputLinear(in_features=16, out_features=32)
hidden = torch.randn(2, 4, 16)
labels = torch.randint(0, 32, (2, 4))

# With labels, the forward should try to call quack's chunked_linear_cross_entropy.
# Since quack-kernels is not installed, we expect an ImportError or ModuleNotFoundError
# (not an AttributeError, TypeError, or other bug-indicating error).
try:
    out = layer(hidden, labels=labels)
    # If it somehow succeeds (unlikely on CPU without quack), check it returns loss
    assert 'loss' in out, 'labels provided should return loss'
    print('OK')
except (ImportError, ModuleNotFoundError) as e:
    assert 'quack' in str(e).lower(), f'Import error should reference quack: {e}'
    print('OK - quack import attempted as expected')
except Exception as e:
    print(f'FAIL: unexpected error type {type(e).__name__}: {e}')
    import sys; sys.exit(1)
" 2>&1 && pass 0.10 "QuackFusedCE labels path uses quack backend" \
       || fail 0.10 "QuackFusedCE labels path uses quack backend"

echo ""
echo "=== Behavioral: FUSED_CE_IGNORE_INDEX constant ==="
# [pr_diff] (0.05): Module-level constant extracted and shared
python3 -c "
from prime_rl.trainer.models.layers.lm_head import (
    FUSED_CE_IGNORE_INDEX,
    FusedCrossEntropyOutputLinear,
)
assert FUSED_CE_IGNORE_INDEX == -100
assert FusedCrossEntropyOutputLinear.IGNORE_INDEX == FUSED_CE_IGNORE_INDEX
print('OK')
" 2>&1 && pass 0.05 "FUSED_CE_IGNORE_INDEX constant" \
       || fail 0.05 "FUSED_CE_IGNORE_INDEX constant"

echo ""
echo "=== Behavioral: inject_prime_lm_head dispatches quack ==="
# [pr_diff] (0.15): inject_prime_lm_head installs QuackFusedCrossEntropyOutputLinear when fused_cross_entropy="quack"
python3 -c "
import torch
import torch.nn as nn

from prime_rl.trainer.models.layers.lm_head import (
    inject_prime_lm_head,
    QuackFusedCrossEntropyOutputLinear,
    FusedCrossEntropyOutputLinear,
)

# Build a minimal model mock
class FakeConfig:
    final_logit_softcapping = None
    vocab_size = 32

class FakeBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed_tokens = nn.Embedding(32, 16)

class FakeModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.config = FakeConfig()
        self.model = FakeBackbone()
        self.lm_head = nn.Linear(16, 32, bias=False)

# Test quack dispatch
model_q = FakeModel()
inject_prime_lm_head(model_q, chunk_size=None, fused_cross_entropy='quack')
assert isinstance(model_q.lm_head, QuackFusedCrossEntropyOutputLinear), \
    f'Expected QuackFusedCrossEntropyOutputLinear, got {type(model_q.lm_head)}'

# Test liger dispatch (True or 'liger')
model_l = FakeModel()
inject_prime_lm_head(model_l, chunk_size=None, fused_cross_entropy=True)
assert isinstance(model_l.lm_head, FusedCrossEntropyOutputLinear), \
    f'Expected FusedCrossEntropyOutputLinear, got {type(model_l.lm_head)}'

print('OK')
" 2>&1 && pass 0.15 "inject_prime_lm_head dispatches quack vs liger" \
       || fail 0.15 "inject_prime_lm_head dispatches quack vs liger"

echo ""
echo "=== Behavioral: Gemma softcapping raises for quack ==="
# [pr_diff] (0.10): quack + Gemma softcapping raises ValueError
python3 -c "
import torch
import torch.nn as nn

from prime_rl.trainer.models.layers.lm_head import inject_prime_lm_head

class FakeConfig:
    final_logit_softcapping = 30.0  # Gemma-style
    vocab_size = 32

class FakeBackbone(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed_tokens = nn.Embedding(32, 16)

class FakeModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.config = FakeConfig()
        self.model = FakeBackbone()
        self.lm_head = nn.Linear(16, 32, bias=False)

model = FakeModel()
try:
    inject_prime_lm_head(model, chunk_size=None, fused_cross_entropy='quack')
    assert False, 'Should have raised ValueError'
except ValueError as e:
    assert 'softcapping' in str(e).lower() or 'gemma' in str(e).lower() or 'quack' in str(e).lower(), \
        f'Error message should mention softcapping/gemma/quack: {e}'
    print('OK')
" 2>&1 && pass 0.10 "Gemma softcapping raises ValueError for quack" \
       || fail 0.10 "Gemma softcapping raises ValueError for quack"

echo ""
echo "=== Behavioral: RMSNorm quack fallback on CPU ==="
# [pr_diff] (0.10): _get_quack_rmsnorm returns None on CPU, RMSNorm works on CPU tensors
python3 -c "
import torch
from prime_rl.trainer.models.layers.norms import _get_quack_rmsnorm, RMSNorm, RMSNormConfig

# On CPU (no CUDA), should return None
result = _get_quack_rmsnorm()
assert result is None, f'Expected None on CPU, got {result}'

# RMSNorm forward should still work on CPU using torch fallback
config = RMSNormConfig(hidden_size=16, eps=1e-5)
norm = RMSNorm(config)
x = torch.randn(2, 4, 16)
out = norm(x)
assert out.shape == (2, 4, 16), f'Wrong shape: {out.shape}'
# Output should be normalized (not all zeros, not NaN)
assert not torch.isnan(out).any(), 'Output has NaN'
assert out.abs().sum() > 0, 'Output is all zeros'
print('OK')
" 2>&1 && pass 0.10 "RMSNorm quack fallback and CPU forward" \
       || fail 0.10 "RMSNorm quack fallback and CPU forward"

echo ""
echo "=== Behavioral: _contiguous_grad identity in forward ==="
# [pr_diff] (0.05): _contiguous_grad is identity in forward, works for both requires_grad cases
python3 -c "
import torch
from prime_rl.trainer.models.layers.norms import _contiguous_grad

# With requires_grad=True
x = torch.randn(3, 4, requires_grad=True)
y = _contiguous_grad(x)
assert torch.equal(x, y), 'Should be identity in forward'

# With requires_grad=False (should skip autograd function)
x2 = torch.randn(3, 4, requires_grad=False)
y2 = _contiguous_grad(x2)
assert torch.equal(x2, y2), 'Should be identity for non-grad tensors'
assert y2 is x2, 'Should return same tensor when requires_grad=False'
print('OK')
" 2>&1 && pass 0.05 "_contiguous_grad identity in forward" \
       || fail 0.05 "_contiguous_grad identity in forward"

echo ""
echo "=== Behavioral: SFT config accepts quack_fused loss_impl ==="
# [pr_diff] (0.10): loss_impl field accepts "quack_fused" as a valid value
python3 -c "
import sys
sys.path.insert(0, '/repo/src')

# Try to instantiate the config with the new loss_impl value
# This tests the actual pydantic validation, not just AST string presence
from prime_rl.configs.sft import SFTConfig

# quack_fused should be accepted
try:
    cfg = SFTConfig(loss_impl='quack_fused')
    assert cfg.loss_impl == 'quack_fused', f'Expected quack_fused, got {cfg.loss_impl}'
    print('quack_fused accepted')
except Exception as e:
    # If SFTConfig needs more args, try a different approach
    import ast
    with open('src/prime_rl/configs/sft.py') as f:
        tree = ast.parse(f.read())
    # Find Literal annotation containing quack_fused as an actual type annotation value
    found_in_annotation = False
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and node.value is not None:
            # Check if this annotation contains a Subscript with Literal
            ann = node.annotation
            if isinstance(ann, ast.Subscript):
                # Walk the annotation subtree for 'quack_fused' constant
                for sub in ast.walk(ann):
                    if isinstance(sub, ast.Constant) and sub.value == 'quack_fused':
                        found_in_annotation = True
                        break
    if not found_in_annotation:
        # Also check for quack_fused as a class variable default
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == 'quack_fused':
                found_in_annotation = True
                break
    assert found_in_annotation, 'quack_fused not found as config option in sft.py'
    print('quack_fused found in config annotation')

print('OK')
" 2>&1 && pass 0.10 "SFT config accepts quack_fused" \
       || fail 0.10 "SFT config accepts quack_fused"

echo ""
echo "=== Behavioral: train.py wires quack_fused to fused_cross_entropy ==="
# [pr_diff] (0.05): train.py maps quack_fused config to fused_cross_entropy and imports shared constant
python3 -c "
import ast

with open('src/prime_rl/trainer/sft/train.py') as f:
    source = f.read()
    tree = ast.parse(source)

# 1. Check FUSED_CE_IGNORE_INDEX is referenced as a Name node (not just a string/comment)
names_used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
assert 'FUSED_CE_IGNORE_INDEX' in names_used, \
    'train.py should reference FUSED_CE_IGNORE_INDEX as a variable (not hardcoded -100)'

# 2. Check quack_fused appears as an AST string constant (in a comparison/match, not a comment)
quack_constants = [
    node for node in ast.walk(tree)
    if isinstance(node, ast.Constant) and node.value == 'quack_fused'
]
assert len(quack_constants) > 0, \
    'train.py should handle quack_fused as a string constant in dispatch logic'

print('OK')
" 2>&1 && pass 0.05 "train.py quack_fused wiring" \
       || fail 0.05 "train.py quack_fused wiring"

echo ""
echo "=== Pass-to-pass: Existing FusedOutputLinear CPU test ==="
# [repo_tests] (0.10): Existing fused lm_head CPU tests still pass
python3 -c "
import torch
from prime_rl.trainer.models.layers.lm_head import FusedOutputLinear, VanillaOutputLinear

# VanillaOutputLinear returns logits
torch.manual_seed(0)
h, v = 8, 37
lm = VanillaOutputLinear(in_features=h, out_features=v)
hidden = torch.randn(2, 4, h, dtype=torch.float32)
out = lm(hidden, labels=None, temperature=None)
assert out.get('logits') is not None, 'Vanilla should return logits'
assert out['logits'].shape == (2, 4, v)

# FusedOutputLinear still works (labels required)
lm2 = FusedOutputLinear(in_features=h, out_features=v, chunk_size=3)
try:
    lm2(hidden, labels=None, temperature=torch.ones(2, 4))
    assert False, 'Should have raised AssertionError'
except AssertionError:
    pass  # Expected

print('OK')
" 2>&1 && pass 0.10 "Existing FusedOutputLinear/VanillaOutputLinear still work" \
       || fail 0.10 "Existing FusedOutputLinear/VanillaOutputLinear still work"

echo ""
echo "=== Structural: pyproject.toml quack extra ==="
# [pr_diff] (0.05): pyproject.toml has quack optional extra with quack-kernels>=0.3.3
python3 -c "
import re

with open('pyproject.toml') as f:
    content = f.read()

# Check for quack-kernels dependency with a version constraint
match = re.search(r'quack-kernels\s*[>~=!]+\s*=?\s*([\d.]+)', content)
assert match, 'quack-kernels dependency with version constraint not found in pyproject.toml'
version = match.group(1)
parts = [int(x) for x in version.split('.')]
assert parts >= [0, 3, 3], f'quack-kernels version must be >= 0.3.3, got {version}'
print('OK')
" 2>&1 && pass 0.05 "pyproject.toml quack extra" \
       || fail 0.05 "pyproject.toml quack extra"

echo ""
echo "=== Summary ==="
echo "Score: $SCORE / 1.00"

mkdir -p /logs/verifier
echo "$SCORE" > /logs/verifier/reward.txt
python3 -c "
import json
score = float('$SCORE')
print(json.dumps({
    'reward': score,
    'behavioral': min(score, 0.85),
    'regression': min(max(score - 0.85, 0), 0.10),
    'structural': min(max(score - 0.95, 0), 0.05),
}))
" > /logs/verifier/reward.json 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
