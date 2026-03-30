#!/usr/bin/env bash
#
# Verification for sglang-benchmark-random-len-fix
#
# Tests that sample_random_requests clamps input_lens to >= 1 after
# subtracting special tokens, preventing empty prompts.
#
# Weights:
#   Behavioral (fail-to-pass):  Test 1 (0.35) = 0.35
#   Pass-to-pass (regression):  Test 2 (0.25) = 0.25
#   Structural (supplementary): Test 3 (0.20) = 0.20
#   Anti-stub:                  Test 4 (0.10) = 0.10
#   Config-derived:             Test 5 (0.10) = 0.10
#   Total: 1.00
#
set +e

TARGET="/workspace/sglang/python/sglang/benchmark/datasets/random.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

###############################################################################
# GATE: Python syntax validity
###############################################################################

echo "=== GATE: Python syntax check ==="
python3 -c "
import ast, sys
with open('$TARGET', 'r') as f:
    source = f.read()
try:
    ast.parse(source)
    print('PASS: syntax OK')
except SyntaxError as e:
    print(f'FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error, scoring 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

###############################################################################
# Test 1 (0.35): Behavioral fail-to-pass — edge-case inputs produce >= 1
#   input_lens[i] - num_special_tokens == 0 or < 0 must still yield >= 1
###############################################################################

echo ""
echo "=== Test 1/4 [0.35]: Behavioral fail-to-pass — edge-case inputs ==="
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/benchmark/datasets/random.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find sample_random_requests
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "sample_random_requests":
        func_node = node
        break

if func_node is None:
    print("FAIL: sample_random_requests function not found")
    sys.exit(1)

# Extract input_lens[i] assignment expressions
adjustment_lines = []
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Subscript) and
                isinstance(target.value, ast.Name) and
                target.value.id == "input_lens"):
                seg = ast.get_source_segment(source, node)
                if seg:
                    adjustment_lines.append(seg)
    elif isinstance(node, ast.AugAssign):
        if (isinstance(node.target, ast.Subscript) and
            isinstance(node.target.value, ast.Name) and
            node.target.value.id == "input_lens"):
            seg = ast.get_source_segment(source, node)
            if seg:
                adjustment_lines.append(seg)

if not adjustment_lines:
    print("FAIL: could not extract adjustment expression for input_lens")
    sys.exit(1)

loop_body = "\n    ".join(adjustment_lines)

# Test cases: (input_len_value, num_special_tokens, description)
test_cases = [
    (3, 3, "input_len equals special tokens (would be 0)"),
    (1, 5, "input_len less than special tokens (would be negative)"),
    (2, 2, "input_len equals special tokens again"),
    (0, 1, "input_len is 0 already"),
    (5, 3, "normal case, should be 2"),
    (1, 1, "boundary: 1 - 1 = 0"),
    (10, 0, "no special tokens"),
]

all_passed = True
for input_val, num_special, desc in test_cases:
    input_lens = [input_val]
    num_special_tokens = num_special
    i = 0

    try:
        exec(loop_body)
    except Exception:
        pass

    if input_lens[0] < 1:
        print(f"  FAIL: {desc} -> input_lens={input_lens[0]} (expected >= 1)")
        all_passed = False
    else:
        print(f"  PASS: {desc} -> input_lens={input_lens[0]}")

if all_passed:
    print("PASS: all edge-case inputs produce input_lens >= 1")
else:
    print("FAIL: some inputs produced input_lens < 1")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.35)"); fi

###############################################################################
# Test 2 (0.25): Pass-to-pass regression — normal inputs still work
###############################################################################

echo ""
echo "=== Test 2/4 [0.25]: Pass-to-pass regression — normal inputs ==="
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/benchmark/datasets/random.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "sample_random_requests":
        func_node = node
        break

if func_node is None:
    print("FAIL: function not found")
    sys.exit(1)

adjustment_lines = []
for node in ast.walk(func_node):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if (isinstance(target, ast.Subscript) and
                isinstance(target.value, ast.Name) and
                target.value.id == "input_lens"):
                seg = ast.get_source_segment(source, node)
                if seg:
                    adjustment_lines.append(seg)
    elif isinstance(node, ast.AugAssign):
        if (isinstance(node.target, ast.Subscript) and
            isinstance(node.target.value, ast.Name) and
            node.target.value.id == "input_lens"):
            seg = ast.get_source_segment(source, node)
            if seg:
                adjustment_lines.append(seg)

if not adjustment_lines:
    print("FAIL: could not extract adjustment expression")
    sys.exit(1)

loop_body = "\n    ".join(adjustment_lines)

test_cases = [
    (100, 3, 97),
    (50, 5, 45),
    (256, 10, 246),
    (1024, 1, 1023),
]

all_ok = True
for input_val, num_special, expected_min in test_cases:
    input_lens = [input_val]
    num_special_tokens = num_special
    i = 0
    try:
        exec(loop_body)
    except Exception as e:
        print(f"FAIL: exec error: {e}")
        sys.exit(1)

    result = input_lens[0]
    if result < 1:
        print(f"  FAIL: input={input_val}, special={num_special} -> {result}")
        all_ok = False
    else:
        print(f"  PASS: input={input_val}, special={num_special} -> {result}")

if all_ok:
    print("PASS: normal inputs produce valid positive lengths")
else:
    print("FAIL")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi

###############################################################################
# Test 3 (0.20): Structural — buggy max(0,...) pattern removed
###############################################################################

echo ""
echo "=== Test 3/5 [0.20]: Structural — buggy max(0,...) pattern removed ==="
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/sglang/python/sglang/benchmark/datasets/random.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "sample_random_requests":
        func_node = node
        break

if func_node is None:
    print("FAIL: sample_random_requests function not found")
    sys.exit(1)

# Check for the buggy max(0, ...) pattern
has_max_0_with_input_lens = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == "max":
            if (len(node.args) >= 2 and
                isinstance(node.args[0], ast.Constant) and
                node.args[0].value == 0):
                segment = ast.get_source_segment(source, node)
                if segment and "input_lens" in segment and "num_special_tokens" in segment:
                    has_max_0_with_input_lens = True

if has_max_0_with_input_lens:
    print("FAIL: original buggy max(0, input_lens[i] - num_special_tokens) still present")
    sys.exit(1)

print("PASS: function exists and buggy max(0,...) pattern removed")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 4 (0.20): Anti-stub — file retains full implementation
###############################################################################

echo ""
echo "=== Test 4/5 [0.10]: Anti-stub check ==="
python3 << 'PYEOF'
import sys

TARGET = "/workspace/sglang/python/sglang/benchmark/datasets/random.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("def sample_random_requests" in source, "function definition present"),
    ("input_lens" in source, "input_lens variable used"),
    ("output_lens" in source, "output_lens variable used"),
    ("tokenizer" in source, "tokenizer referenced"),
    ("num_special_tokens" in source or "special" in source, "special tokens handling"),
    (len(source.splitlines()) > 30, "file has substantial content (>30 lines)"),
    (len(source) > 500, "file has substantial size (>500 chars)"),
    (source.count("def ") >= 1, "at least one function defined"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

###############################################################################
# Test 5 (0.10): Config-derived — "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ a93065679b6395c07fd03249e2e99ccca293ac15
# Any new test files the agent creates must include the standard main guard.
###############################################################################

echo ""
echo "=== Test 5/5 [0.10]: Config-derived — new test files have main guard ==="
cd /workspace/sglang 2>/dev/null
NEW_TEST_FILES=$(git diff --name-only --diff-filter=A HEAD 2>/dev/null | grep -E '^test/.*\.py$' || true)
if [ -z "$NEW_TEST_FILES" ]; then
    echo "PASS (no new test files added)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    ALL_OK=1
    for tf in $NEW_TEST_FILES; do
        if ! grep -q 'if __name__.*==.*"__main__"' "/workspace/sglang/$tf" 2>/dev/null; then
            echo "FAIL: $tf missing if __name__ == '__main__' guard"
            ALL_OK=0
        fi
    done
    if [ "$ALL_OK" -eq 1 ]; then
        echo "PASS"
        SCORE=$(python3 -c "print($SCORE + 0.10)")
    fi
fi

###############################################################################
# Final score
###############################################################################

echo ""
echo "=== Final Score: $SCORE ==="
REWARD=$(python3 -c "print(min(1.0, round($SCORE, 4)))")
echo "$REWARD" > "$REWARD_FILE"
echo "Reward: $REWARD"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
