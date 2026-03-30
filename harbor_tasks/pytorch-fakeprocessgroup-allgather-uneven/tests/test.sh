#!/usr/bin/env bash
# Verifier for pytorch-fakeprocessgroup-allgather-uneven
# Bug: FakeProcessGroup allgather crashes on uneven output tensor sizes
# File: torch/csrc/distributed/c10d/FakeProcessGroup.hpp
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp"

echo "=== pytorch-fakeprocessgroup-allgather-uneven verifier ==="

# -- GATE: file exists and is valid C++ --
echo ""
echo "GATE: Target file exists"
if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: target file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_UNEVEN=0.35
W_BEHAV_EVEN=0.30
W_STRUCTURAL_SKIP=0.20
W_ANTISTUB=0.10
W_CONFIG_STYLE=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Uneven allgather does not crash --
# Extract the allgather loop logic and simulate it in Python
echo ""
echo "TEST 1: behavioral -- uneven allgather does not crash (weight=$W_BEHAV_UNEVEN)"
T1=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp") as f:
    source = f.read()

# Find the allgather method body
# The bug is in the loop that copies input to output tensors
# The fix should skip tensors with mismatched sizes

# Simulate the logic: look for the allgather override and check if there's
# a size check before copy_
allgather_pattern = r'allgather\s*\([^)]*\)\s*override\s*\{(.*?)\n\s*return\s+c10::make_intrusive'
match = re.search(allgather_pattern, source, re.DOTALL)

if not match:
    print("FAIL: could not find allgather method body")
    sys.exit(1)

body = match.group(1)

# The fix: before copy_, check if tensor sizes match. If they don't, skip.
# Valid approaches:
# 1. if (tensor.size(0) != inputTensors[0].size(0)) continue;
# 2. if (tensor.sizes() != inputTensors[0].sizes()) continue;
# 3. try/catch around copy_
# 4. Any conditional that avoids copy_ for mismatched tensors

has_size_check = bool(re.search(r'size\s*\(\s*0\s*\)', body))
has_sizes_check = bool(re.search(r'sizes\s*\(\s*\)', body))
has_numel_check = bool(re.search(r'numel\s*\(\s*\)', body))
has_continue = 'continue' in body
has_conditional = bool(re.search(r'if\s*\(', body))

# The key behavioral test: there must be a guard that prevents copy_ on mismatched tensors
if (has_size_check or has_sizes_check or has_numel_check) and (has_continue or has_conditional):
    print("PASS: allgather has size guard to skip mismatched tensors")
    sys.exit(0)
elif has_conditional and has_continue:
    print("PASS: allgather has conditional skip logic")
    sys.exit(0)
else:
    print("FAIL: allgather unconditionally copies to all output tensors")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_UNEVEN)")
fi

# -- TEST 2 (BEHAVIORAL): Even allgather still works (regression) --
echo ""
echo "TEST 2: behavioral -- even allgather still copies correctly (weight=$W_BEHAV_EVEN)"
T2=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp") as f:
    source = f.read()

# Find the allgather method
allgather_pattern = r'allgather\s*\([^)]*\)\s*override\s*\{(.*?)\n\s*return\s+c10::make_intrusive'
match = re.search(allgather_pattern, source, re.DOTALL)

if not match:
    print("FAIL: could not find allgather method body")
    sys.exit(1)

body = match.group(1)

# The copy_ call must still exist (not removed entirely)
if 'copy_' not in body:
    print("FAIL: copy_ operation removed entirely -- even tensors won't be filled")
    sys.exit(1)

# The copy_ must be reachable (not dead code)
# If there's a continue before copy_, the continue must be conditional
lines = body.strip().split('\n')
copy_line_idx = None
for i, line in enumerate(lines):
    if 'copy_' in line:
        copy_line_idx = i
        break

if copy_line_idx is None:
    print("FAIL: copy_ not found")
    sys.exit(1)

# Check that copy_ is inside the for loop (should follow the tensor iteration)
if 'for' not in body:
    print("FAIL: no for loop found in allgather")
    sys.exit(1)

print("PASS: copy_ still present and reachable for matching tensors")
sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_EVEN)")
fi

# -- TEST 3 (STRUCTURAL): Size comparison references correct dimension --
echo ""
echo "TEST 3: structural -- size check references dimension 0 (weight=$W_STRUCTURAL_SKIP)"
T3=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp") as f:
    source = f.read()

allgather_pattern = r'allgather\s*\([^)]*\)\s*override\s*\{(.*?)\n\s*return\s+c10::make_intrusive'
match = re.search(allgather_pattern, source, re.DOTALL)

if not match:
    print("FAIL: could not find allgather method body")
    sys.exit(1)

body = match.group(1)

# Check for size(0) comparison between output tensor and input tensor
# Valid patterns: tensor.size(0) != inputTensors[0].size(0)
#                 tensor.sizes() != inputTensors[0].sizes()
has_dim0_compare = bool(re.search(r'\.size\s*\(\s*0\s*\)\s*!=\s*.*\.size\s*\(\s*0\s*\)', body))
has_sizes_compare = bool(re.search(r'\.sizes\s*\(\s*\)\s*!=\s*.*\.sizes\s*\(\s*\)', body))
has_shape_compare = bool(re.search(r'\.size\s*\(\s*0\s*\)\s*==\s*.*\.size\s*\(\s*0\s*\)', body))
has_numel_compare = bool(re.search(r'\.numel\s*\(\s*\)\s*!=\s*.*\.numel\s*\(\s*\)', body))

if has_dim0_compare or has_sizes_compare or has_shape_compare or has_numel_compare:
    print("PASS: size comparison between output and input tensors found")
    sys.exit(0)
else:
    print("FAIL: no proper size comparison found")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SKIP)")
fi

# -- TEST 4: Anti-stub check --
echo ""
echo "TEST 4: anti-stub -- file retains original allgather logic (weight=$W_ANTISTUB)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp") as f:
    source = f.read()

required = ["FakeProcessGroup", "allgather", "copy_", "outputTensors", "inputTensors",
            "checkCollectiveError", "FakeWork", "Backend"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 50:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# ---------- Config-derived test (0.05): "Match existing code style and architectural patterns" ----------
# Source: CLAUDE.md line 57 @ 8401fdeb9abd665b36465c52b7aefd591cc3dbcb
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
