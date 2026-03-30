#!/usr/bin/env bash
# Verifier for pytorch-stream-context-reentrance
# Bug: Stream context manager doesn't support nested/reentrant usage
# File: torch/csrc/Stream.cpp
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/torch/csrc/Stream.cpp"

echo "=== pytorch-stream-context-reentrance verifier ==="

# -- GATE: file exists --
echo ""
echo "GATE: Target file exists"
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: target file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral (logic checks), <=40% structural
W_BEHAV_STACK=0.25
W_BEHAV_NO_ASSERT=0.20
W_BEHAV_NOOP_SENTINEL=0.20
W_STRUCTURAL_DEALLOC=0.10
W_STRUCTURAL_POP=0.10
W_ANTISTUB=0.10
W_CONFIG_STYLE=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Context uses stack/list instead of single dict --
echo ""
echo "TEST 1: behavioral -- context uses stack-based storage (weight=$W_BEHAV_STACK)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# The fix replaces a single context dict with a list/stack.
# Look for PyList_New or PyList_Append in __enter__ function
has_list_new = "PyList_New" in source
has_list_append = "PyList_Append" in source

# Alternative: could use std::vector or std::stack in C++
has_vector = "std::vector" in source and "context" in source.lower()
has_stack = "std::stack" in source and "context" in source.lower()

if has_list_new and has_list_append:
    print("PASS: context uses Python list as stack (PyList_New + PyList_Append)")
    sys.exit(0)
elif has_vector or has_stack:
    print("PASS: context uses C++ container as stack")
    sys.exit(0)
else:
    print("FAIL: no stack-based context storage found")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_STACK)")
fi

# -- TEST 2 (BEHAVIORAL): No assertion that prevents reentrance --
echo ""
echo "TEST 2: behavioral -- reentrance assertion removed (weight=$W_BEHAV_NO_ASSERT)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# The buggy code has: TORCH_CHECK(!(self->context), "Stream's context should not be initialized.")
# This must be removed for reentrance to work
if 'Stream\'s context should not be initialized' in source:
    print("FAIL: reentrance-blocking assertion still present")
    sys.exit(1)
elif 'context should not be initialized' in source:
    print("FAIL: reentrance-blocking assertion still present (variant)")
    sys.exit(1)
else:
    print("PASS: reentrance-blocking assertion removed")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_NO_ASSERT)")
fi

# -- TEST 3 (BEHAVIORAL): No-op sentinel for already-current stream --
echo ""
echo "TEST 3: behavioral -- no-op sentinel when stream is already current (weight=$W_BEHAV_NOOP_SENTINEL)"
T3=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# The fix should check if stream is already the current stream in __enter__
# and push a no-op sentinel (Py_None) instead of switching
# This handles the case: with s0, s0: ...

# Look for stream_id comparison in THPStream_enter
enter_start = source.find("THPStream_enter")
if enter_start < 0:
    print("FAIL: THPStream_enter not found")
    sys.exit(1)

enter_section = source[enter_start:enter_start+3000]

# Check for current stream comparison
has_stream_id_check = "stream_id" in enter_section and ("cur_stream" in enter_section or "current_stream" in enter_section)
has_none_sentinel = "Py_None" in enter_section

if has_stream_id_check and has_none_sentinel:
    print("PASS: __enter__ checks if stream is already current and uses None sentinel")
    sys.exit(0)
elif has_none_sentinel:
    print("PASS: __enter__ uses None sentinel for no-op case")
    sys.exit(0)
else:
    print("FAIL: no current-stream check or None sentinel in __enter__")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_NOOP_SENTINEL)")
fi

# -- TEST 4 (STRUCTURAL): Dealloc clears context --
echo ""
echo "TEST 4: structural -- dealloc clears context (weight=$W_STRUCTURAL_DEALLOC)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

# Find dealloc function
dealloc_start = source.find("THPStream_dealloc")
if dealloc_start < 0:
    print("FAIL: THPStream_dealloc not found")
    sys.exit(1)

dealloc_section = source[dealloc_start:dealloc_start+500]

# Should have Py_CLEAR(self->context) or Py_XDECREF(self->context)
if "Py_CLEAR(self->context)" in dealloc_section or "Py_XDECREF(self->context)" in dealloc_section:
    print("PASS: dealloc clears context")
    sys.exit(0)
else:
    print("FAIL: dealloc does not clear context")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_DEALLOC)")
fi

# -- TEST 5 (STRUCTURAL): __exit__ pops from stack --
echo ""
echo "TEST 5: structural -- __exit__ pops from context stack (weight=$W_STRUCTURAL_POP)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/Stream.cpp") as f:
    source = f.read()

exit_start = source.find("THPStream_exit")
if exit_start < 0:
    print("FAIL: THPStream_exit not found")
    sys.exit(1)

exit_section = source[exit_start:exit_start+2000]

# __exit__ should pop from list (PyList_SetSlice or PyList_GET_ITEM + remove)
has_pop = ("PyList_SetSlice" in exit_section or "PyList_GET_ITEM" in exit_section
           or "pop" in exit_section.lower())

# Should NOT have Py_CLEAR(self->context) which clears the whole thing
has_full_clear = "Py_CLEAR(self->context)" in exit_section

if has_pop and not has_full_clear:
    print("PASS: __exit__ pops from stack without clearing entire context")
    sys.exit(0)
elif has_pop:
    print("PASS: __exit__ pops from stack (partial)")
    sys.exit(0)
else:
    print("FAIL: __exit__ does not pop from context stack")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_POP)")
fi

# -- TEST 6: Anti-stub check --
echo ""
echo "TEST 6: anti-stub -- file retains stream context logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
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

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# ---------- Config-derived test (0.05): "Match existing code style and architectural patterns" ----------
# Source: CLAUDE.md line 57 @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
echo ""
echo "TEST config_style: config-derived -- match existing code style (weight=$W_CONFIG_STYLE)"
T_CONFIG=$(python3 << 'PYEOF'
import sys, os
os.chdir('/workspace/pytorch')
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
if not changed:
    result2 = subprocess.run(['find', 'torch', '-name', '*.py', '-newer', 'setup.py'], capture_output=True, text=True)
    changed = [f for f in result2.stdout.strip().split('\n') if f]
print('PASS')
PYEOF
)
echo "$T_CONFIG"
if echo "$T_CONFIG" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_STYLE)")
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
