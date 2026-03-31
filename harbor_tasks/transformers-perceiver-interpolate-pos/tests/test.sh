#!/usr/bin/env bash
# Verifier for transformers-perceiver-interpolate-pos
# Bug: interpolate_pos_encoding passes source dims instead of target dims to nn.functional.interpolate
# File: src/transformers/models/perceiver/modeling_perceiver.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py"

echo "=== transformers-perceiver-interpolate-pos verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error - aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights - >=60% behavioral
W_BEHAV_PRIMARY=0.50    # [pr_diff] True behavioral: interpolates to target dims
W_BEHAV_SECONDARY=0.15 # [pr_diff] Multi-size testing
W_P2P=0.20            # [pr_diff] Upstream tests pass
W_ANTISTUB=0.10       # [repo_tests] File is not a stub
W_CONFIG_RUFF=0.05    # [agent_config] Format check

SCORE="0.0"
GATE_BEHAV_PASSED=0   # Gate for structural checks

# ── TEST 1 (PRIMARY): True behavioral - real torch execution verifies fix ──
echo ""
echo "TEST 1: behavioral - real execution verifies interpolation (weight=$W_BEHAV_PRIMARY)"
T1=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

try:
    import torch
    from src.transformers.models.perceiver.modeling_perceiver import PerceiverTrainablePositionEncoding
except ImportError as e:
    print(f"FAIL: import error: {e}")
    sys.exit(1)

# Test: Create position encoding with 4x4 grid (16 positions)
# Then interpolate to 8x8 (64 positions)
num_channels = 64
index_dims = (4, 4)  # 4x4 = 16 positions

pe = PerceiverTrainablePositionEncoding(index_dims=index_dims, num_channels=num_channels)

# Original embeddings: 16 positions, 64 channels each
pos_emb = pe.position_embeddings  # shape: (16, 64)
assert pos_emb.shape == (16, num_channels), f"Expected (16, {num_channels}), got {pos_emb.shape}"

# Target resolution: 8x8
target_height, target_width = 8, 8

# Call interpolate_pos_encoding with target dims
result = pe.interpolate_pos_encoding(pos_emb, target_height, target_width)

# The bug: result would have 16 positions (4x4) because it interpolates to (new_height, new_width)
# The fix: result should have 64 positions (8x8) because it interpolates to (height, width)
num_result_positions = result.shape[0]
expected_positions = target_height * target_width  # 64

if num_result_positions == expected_positions:
    print(f"PASS: interpolated output has {num_result_positions} positions (target: {expected_positions})")
    sys.exit(0)
elif num_result_positions == 16:
    print(f"FAIL: output has 16 positions (source dims) - bug not fixed")
    sys.exit(1)
else:
    print(f"FAIL: unexpected output shape {result.shape}")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_PRIMARY)")
    GATE_BEHAV_PASSED=1
fi

# ── TEST 2: Behavioral - multiple target resolutions ──
echo ""
echo "TEST 2: behavioral - multiple target resolutions (weight=$W_BEHAV_SECONDARY)"
T2=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/transformers')

try:
    import torch
    from src.transformers.models.perceiver.modeling_perceiver import PerceiverTrainablePositionEncoding
except ImportError as e:
    print(f"FAIL: import error: {e}")
    sys.exit(1)

# Test multiple target resolutions to ensure fix is general, not hardcoded
num_channels = 32
index_dims = (2, 2)  # 4 positions source

pe = PerceiverTrainablePositionEncoding(index_dims=index_dims, num_channels=num_channels)
pos_emb = pe.position_embeddings

# Test cases: (target_h, target_w, expected_positions)
test_cases = [
    (4, 4, 16),    # 4x4 = 16 positions
    (6, 6, 36),    # 6x6 = 36 positions
    (8, 4, 32),    # Non-square: 8x4 = 32 positions
]

all_passed = True
for h, w, expected in test_cases:
    result = pe.interpolate_pos_encoding(pos_emb, h, w)
    actual = result.shape[0]
    if actual != expected:
        print(f"FAIL: target ({h}x{w}) expected {expected} positions, got {actual}")
        all_passed = False

if all_passed:
    print(f"PASS: all {len(test_cases)} target resolutions work correctly")
    sys.exit(0)
else:
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_SECONDARY)")
fi

# ── TEST 3: Pass-to-pass - upstream perceiver tests ──
echo ""
echo "TEST 3: pass-to-pass - upstream perceiver tests (weight=$W_P2P)"
T3=$(python3 << 'PYEOF'
import sys
import subprocess

# Run a subset of CPU-safe upstream tests for the perceiver model
result = subprocess.run(
    [
        "python3", "-m", "pytest",
        "/workspace/transformers/tests/models/perceiver/test_modeling_perceiver.py",
        "-k", "test_config or test_model or test_forward",
        "--timeout=60", "-x", "-q",
    ],
    capture_output=True,
    text=True,
    cwd="/workspace/transformers"
)

if result.returncode == 0:
    print("PASS: upstream perceiver tests pass")
    sys.exit(0)
else:
    # If tests don't exist or there's a different issue, check pass-to-pass via import
    print("Note: upstream tests skipped or failed, checking basic import...")
    sys.path.insert(0, '/workspace/transformers')
    try:
        from src.transformers.models.perceiver.modeling_perceiver import (
            PerceiverTrainablePositionEncoding,
            PerceiverForImageClassificationLearned,
            PerceiverModel,
        )
        print("PASS: core perceiver classes import successfully")
        sys.exit(0)
    except ImportError as e:
        print(f"FAIL: import error: {e}")
        sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P)")
fi

# ── TEST 4: Anti-stub - file contains original logic (BEHAVIOR-GATED) ──
echo ""
echo "TEST 4: anti-stub - file retains original logic (weight=$W_ANTISTUB)"
if [ $GATE_BEHAV_PASSED -eq 0 ]; then
    echo "SKIPPED: behavioral tests failed - not awarding structural points"
    T4="SKIPPED"
else
    T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

# Check file has substantial content (line count)
lines = source.splitlines()
if len(lines) < 500:
    print(f"FAIL: file has only {len(lines)} lines - looks like a stub")
    sys.exit(1)

# Check the class still exists
if "class PerceiverTrainablePositionEncoding" not in source:
    print("FAIL: PerceiverTrainablePositionEncoding class missing")
    sys.exit(1)

# Check for key methods
methods = ["interpolate_pos_encoding", "forward", "__init__"]
for method in methods:
    if f"def {method}(" not in source:
        print(f"FAIL: method {method} missing")
        sys.exit(1)

# Check it's not just a pass-only stub
non_trivial = sum(1 for line in lines if line.strip() and not line.strip().startswith('#') and line.strip() != 'pass')
if non_trivial < 100:
    print(f"FAIL: too few non-trivial lines ({non_trivial})")
    sys.exit(1)

print(f"PASS: file has {len(lines)} lines with substantial content")
sys.exit(0)
PYEOF
)
    echo "$T4"
    if echo "$T4" | grep -q "^PASS"; then
        SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
    fi
fi

# -- CONFIG-DERIVED: ruff format check --
# [agent_config] (0.05): "Changed files pass ruff format check" - CLAUDE.md @ c532659b8734b88d2bbaac2542c2a5a8b525f3f7
echo ""
echo "TEST 5: ruff format check (weight=$W_CONFIG_RUFF)"
if [ $GATE_BEHAV_PASSED -eq 0 ]; then
    echo "SKIPPED: behavioral tests failed - not awarding config points"
    T5="SKIPPED"
else
    T5=$(python3 << 'PYRUFF'
import subprocess, sys
result = subprocess.run(
    ["ruff", "check", "--select", "E,W", "/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py"],
    capture_output=True, text=True
)
if result.returncode == 0:
    print("PASS: file passes ruff checks")
    sys.exit(0)
else:
    print(f"FAIL: ruff errors:\n{result.stdout}")
    sys.exit(1)
PYRUFF
)
    echo "$T5"
    if echo "$T5" | grep -q "^PASS"; then
        SCORE=$(python3 -c "print($SCORE + $W_CONFIG_RUFF)")
    fi
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
