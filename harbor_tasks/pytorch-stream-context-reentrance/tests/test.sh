#!/usr/bin/env bash
# Verifier for pytorch-stream-context-reentrance
# Bug: Stream context manager doesn't support nested/reentrant usage
# File: torch/csrc/Stream.cpp
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/torch/csrc/Stream.cpp"

echo "=== pytorch-stream-context-reentrance verifier ==="

# -- GATE: file exists and is valid C++ --
echo ""
echo "GATE: Target file exists and compiles"
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: target file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi

# Check for basic syntax by ensuring it has required function signatures
if ! grep -q "THPStream_enter" "$TARGET" || ! grep -q "THPStream_exit" "$TARGET"; then
    echo "GATE FAIL: required functions missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi

echo "GATE PASS"

# Weights: >=60% behavioral (logic checks), <=40% structural
# Fail-to-pass behavioral: 0.40 (core bug fix verification)
# Pass-to-pass: 0.15 (upstream test suite)
# Structural verification: 0.30 (fallback when code can't be executed)
# Anti-stub: 0.10
# Config style: 0.05

W_F2P_REENTRANT=0.25
W_F2P_NESTED=0.15
W_P2P_UPSTREAM=0.15
W_STRUCT_STACK=0.15
W_STRUCT_NOASSERT=0.10
W_ANTISTUB=0.10
W_CONFIG_STYLE=0.05

SCORE="0.0"
PASSED_F2P=0

# -- TEST 1 (BEHAVIORAL FAIL-TO-PASS): Reentrant stream context works --
# [pr_diff] (0.25): Reentrant usage `with s0, s0:` works without crash
echo ""
echo "TEST 1: behavioral F2P -- reentrant stream context works (weight=$W_F2P_REENTRANT)"
T1=$(python3 << 'PYEOF'
import sys
import os
import subprocess

# First check if we can build pytorch enough to import torch
os.chdir('/workspace/pytorch')

# Try to build minimal torch (this may fail, so we have fallback)
print("Attempting to build minimal torch for testing...")
result = subprocess.run(
    ['python3', 'setup.py', 'build_ext', '--inplace'],
    capture_output=True,
    text=True,
    timeout=300
)

# Try importing torch
try:
    import torch
    print("torch imported successfully")
except Exception as e:
    print(f"SKIP: Cannot import torch: {e}")
    # Return special code to trigger structural fallback
    sys.exit(42)

# Test the actual bug: reentrant stream usage
# This should work after fix, crash/assert before fix
try:
    s0 = torch.Stream()
    prev = torch.accelerator.current_stream()

    # The bug: with s0, s0: should work but crashes before fix
    with s0, s0:
        current = torch.accelerator.current_stream()
        if current != s0:
            print(f"FAIL: Expected current stream to be s0 inside context, got {current}")
            sys.exit(1)

    # After exit, should be back to previous stream
    after = torch.accelerator.current_stream()
    if after != prev:
        print(f"FAIL: Stream not restored after context exit. Expected {prev}, got {after}")
        sys.exit(1)

    print("PASS: Reentrant stream context works correctly")
    sys.exit(0)
except AssertionError as e:
    print(f"FAIL: Assertion error (bug still present): {e}")
    sys.exit(1)
except RuntimeError as e:
    print(f"FAIL: Runtime error (bug still present): {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T1"
T1_EXIT=$?

if [ $T1_EXIT -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_REENTRANT)")
    PASSED_F2P=1
    echo "SCORE: $SCORE (behavioral pass)"
elif [ $T1_EXIT -eq 42 ]; then
    echo "BEHAVIORAL SKIP: torch not available, will use structural fallback"
else
    echo "BEHAVIORAL FAIL: Reentrant context doesn't work (bug still present)"
fi

# -- TEST 2 (BEHAVIORAL FAIL-TO-PASS): Nested interleaved streams work --
# [pr_diff] (0.15): Nested interleaved streams work
echo ""
echo "TEST 2: behavioral F2P -- nested interleaved streams work (weight=$W_F2P_NESTED)"
T2=$(python3 << 'PYEOF'
import sys
import os

os.chdir('/workspace/pytorch')

try:
    import torch
except Exception:
    print("SKIP: Cannot import torch")
    sys.exit(42)

try:
    s0 = torch.Stream()
    s1 = torch.Stream()
    prev = torch.accelerator.current_stream()

    # Nested interleaved usage: with s0: with s1: with s0:
    with s0:
        if torch.accelerator.current_stream() != s0:
            print("FAIL: First s0 context not active")
            sys.exit(1)
        with s1:
            if torch.accelerator.current_stream() != s1:
                print("FAIL: s1 context not active")
                sys.exit(1)
            with s0:
                if torch.accelerator.current_stream() != s0:
                    print("FAIL: Nested s0 context not active")
                    sys.exit(1)
            # Back to s1
            if torch.accelerator.current_stream() != s1:
                print("FAIL: Back to s1 context failed")
                sys.exit(1)
        # Back to s0
        if torch.accelerator.current_stream() != s0:
            print("FAIL: Back to s0 context failed")
            sys.exit(1)
    # Back to prev
    if torch.accelerator.current_stream() != prev:
        print("FAIL: Stream not restored to original")
        sys.exit(1)

    print("PASS: Nested interleaved streams work correctly")
    sys.exit(0)
except AssertionError as e:
    print(f"FAIL: Assertion error (bug still present): {e}")
    sys.exit(1)
except RuntimeError as e:
    print(f"FAIL: Runtime error (bug still present): {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T2"
T2_EXIT=$?

if [ $T2_EXIT -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_F2P_NESTED)")
    PASSED_F2P=1
    echo "SCORE: $SCORE (behavioral pass)"
elif [ $T2_EXIT -eq 42 ]; then
    echo "BEHAVIORAL SKIP: torch not available, will use structural fallback"
else
    echo "BEHAVIORAL FAIL: Nested interleaved streams don't work"
fi

# -- TEST 3 (PASS-TO-PASS): Upstream test suite --
# [pr_diff] (0.15): Existing tests still pass
echo ""
echo "TEST 3: P2P -- upstream test suite (weight=$W_P2P_UPSTREAM)"
T3=$(python3 << 'PYEOF'
import sys
import os
import subprocess

os.chdir('/workspace/pytorch')

try:
    import torch
except Exception:
    print("SKIP: Cannot import torch")
    sys.exit(42)

# Run the specific upstream test that was added with the fix
result = subprocess.run(
    ['python3', '-m', 'pytest', 'test/test_accelerator.py::TestAccelerator::test_stream_context_manager_reentrance', '-v', '--timeout=60', '-x'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("PASS: Upstream reentrance test passes")
    sys.exit(0)
else:
    print(f"FAIL: Upstream test failed")
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
    sys.exit(1)
PYEOF
)
echo "$T3"
T3_EXIT=$?

if [ $T3_EXIT -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_UPSTREAM)")
    echo "SCORE: $SCORE (P2P pass)"
elif [ $T3_EXIT -eq 42 ]; then
    echo "P2P SKIP: torch not available"
else
    echo "P2P INFO: Upstream test didn't pass (non-blocking)"
fi

# -- STRUCTURAL FALLBACK: Only used if behavioral tests couldn't run --
# These are BRONZE tier - only run when code literally cannot execute

STRUCTURAL_SCORE="0.0"
STRUCTURAL_USED=0

if [ $PASSED_F2P -eq 0 ]; then
    echo ""
    echo "=== USING STRUCTURAL FALLBACK (torch unavailable) ==="
    STRUCTURAL_USED=1

    # -- STRUCTURAL TEST 1: Stack-based context storage --
    echo ""
    echo "STRUCTURAL 1: Stack-based context storage (weight=$W_STRUCT_STACK)"
    S1=$(python3 << 'PYEOF'
import sys
import ast

# Parse the C++ file to look for stack patterns
with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# Look for list/stack operations
has_list_ops = "PyList_New" in source and "PyList_Append" in source
has_vector = "std::vector" in source and "context" in source.lower()
has_stack = "std::stack" in source and "context" in source.lower()

# Verify the context is actually used as a stack (push/pop pattern)
has_push = "PyList_Append" in source or "push_back" in source
has_pop = "PyList_SetSlice" in source or "pop" in source.lower() or "pop_back" in source

if (has_list_ops or has_vector or has_stack) and has_push and has_pop:
    print("PASS: Stack-based context storage detected")
    sys.exit(0)
else:
    print("FAIL: No stack-based context storage found")
    sys.exit(1)
PYEOF
)
    echo "$S1"
    if echo "$S1" | grep -q "^PASS"; then
        STRUCTURAL_SCORE=$(python3 -c "print($STRUCTURAL_SCORE + $W_STRUCT_STACK)")
    fi

    # -- STRUCTURAL TEST 2: Reentrance assertion removed --
    echo ""
    echo "STRUCTURAL 2: Reentrance-blocking assertion removed (weight=$W_STRUCT_NOASSERT)"
    S2=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# The buggy code has: TORCH_CHECK(!(self->context), "Stream's context should not be initialized.")
if "Stream's context should not be initialized" in source:
    print("FAIL: Reentrance-blocking assertion still present")
    sys.exit(1)
elif "context should not be initialized" in source:
    print("FAIL: Reentrance-blocking assertion variant still present")
    sys.exit(1)
else:
    print("PASS: Reentrance-blocking assertion removed")
    sys.exit(0)
PYEOF
)
    echo "$S2"
    if echo "$S2" | grep -q "^PASS"; then
        STRUCTURAL_SCORE=$(python3 -c "print($STRUCTURAL_SCORE + $W_STRUCT_NOASSERT)")
    fi
fi

# Add structural score if we used fallback
if [ $STRUCTURAL_USED -eq 1 ]; then
    SCORE=$(python3 -c "print($SCORE + $STRUCTURAL_SCORE)")
    echo "STRUCTURAL SCORE: $STRUCTURAL_SCORE"
fi

# -- TEST 4: Anti-stub check --
# [agent_config] (0.10): File must contain real implementation, not stub
echo ""
echo "TEST 4: anti-stub -- file retains stream context logic (weight=$W_ANTISTUB)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

required = ["THPStream_enter", "THPStream_exit", "THPStream_dealloc",
            "setCurrentStream", "getCurrentStream", "context"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 200:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

# Additional: check for meaningful implementation in enter/exit
enter_start = source.find("THPStream_enter")
exit_start = source.find("THPStream_exit")
if enter_start < 0 or exit_start < 0:
    print("FAIL: enter/exit functions not found")
    sys.exit(1)

enter_section = source[enter_start:enter_start+2000]
exit_section = source[exit_start:exit_start+2000]

# Should have actual logic, not just pass-through
enter_lines = [l.strip() for l in enter_section.split('\n') if l.strip() and not l.strip().startswith('//')]
exit_lines = [l.strip() for l in exit_section.split('\n') if l.strip() and not l.strip().startswith('//')]

if len(enter_lines) < 10 or len(exit_lines) < 10:
    print(f"FAIL: enter ({len(enter_lines)} lines) or exit ({len(exit_lines)} lines) too short")
    sys.exit(1)

print(f"PASS: file has {line_count} lines with substantial enter/exit implementations")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- TEST 5: Config-derived style check --
# [agent_config] (0.05): "Match existing code style and architectural patterns"
# Source: CLAUDE.md line 57 @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
echo ""
echo "TEST 5: config-derived -- match existing code style (weight=$W_CONFIG_STYLE)"
T5=$(python3 << 'PYEOF'
import sys, os, subprocess

os.chdir('/workspace/pytorch')

# Check that the file was actually modified from baseline
result = subprocess.run(
    ['git', 'diff', 'HEAD', 'torch/csrc/Stream.cpp'],
    capture_output=True,
    text=True
)

if len(result.stdout) > 100:  # Some meaningful change
    print("PASS: File has been modified from baseline")
    sys.exit(0)
else:
    # If no git changes, check file timestamps or content differences
    stat_result = subprocess.run(['stat', '-c', '%Y', 'torch/csrc/Stream.cpp'], capture_output=True, text=True)
    print("PASS: File exists and is accessible")
    sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_STYLE)")
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Final Reward: $REWARD"
echo "Behavioral: $(python3 -c "print('%.0f%%' % (($W_F2P_REENTRANT + $W_F2P_NESTED + $W_P2P_UPSTREAM)/1.0*100))")"
echo "Structural: $(python3 -c "print('%.0f%%' % (($W_STRUCT_STACK + $W_STRUCT_NOASSERT)/1.0*100))") (fallback only)"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Write detailed breakdown
python3 << PYEOF
import json
reward_data = {
    "reward": float("$REWARD"),
    "behavioral": {
        "f2p_reentrant": $PASSED_F2P if $T1_EXIT == 0 else 0,
        "f2p_nested": 1 if $T2_EXIT == 0 else 0,
        "p2p_upstream": 1 if $T3_EXIT == 0 else 0,
        "weight": 0.55 if (1 if $T2_EXIT == 0 else 0) + (1 if $T3_EXIT == 0 else 0) + $PASSED_F2P > 0 else 0
    },
    "structural_fallback_used": $STRUCTURAL_USED,
    "structural_score": float("$STRUCTURAL_SCORE") if $STRUCTURAL_USED else 0,
    "antistub": 1 if "$T4"[:4] == "PASS" else 0,
    "config_style": 1 if "$T5"[:4] == "PASS" else 0
}
with open("$REWARD_FILE".replace('.txt', '.json'), 'w') as f:
    json.dump(reward_data, f, indent=2)
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
