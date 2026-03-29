#!/usr/bin/env bash
set +e

TARGET="/workspace/sglang/python/sglang/benchmark/datasets/random.py"
REWARD_FILE="/logs/verifier/reward.txt"
PASS=0
TOTAL=0

# ---------- GATE: Python syntax validity ----------
TOTAL=$((TOTAL + 1))
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'SYNTAX ERROR: {e}')
    sys.exit(1)
"
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
    echo "GATE PASS: syntax valid"
else
    echo "GATE FAIL: syntax error -- scoring 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- TEST 1: max(1, ...) instead of max(0, ...) in input_lens adjustment ----------
TOTAL=$((TOTAL + 1))
python3 -c "
import ast, sys

with open('$TARGET') as f:
    source = f.read()

tree = ast.parse(source)

found_max1 = False
found_max0 = False

for node in ast.walk(tree):
    # Look for Call nodes where func is 'max'
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == 'max':
            if len(node.args) >= 1:
                first_arg = node.args[0]
                if isinstance(first_arg, ast.Constant):
                    if first_arg.value == 1:
                        found_max1 = True
                    elif first_arg.value == 0:
                        found_max0 = True

if found_max1 and not found_max0:
    print('TEST 1 PASS: max(1, ...) found, no max(0, ...) in input_lens logic')
    sys.exit(0)
else:
    # Fallback: text-based check for the specific pattern
    if 'max(1,' in source and 'max(0, input_lens' not in source and 'max(0,input_lens' not in source:
        print('TEST 1 PASS (text fallback): max(1, ...) present')
        sys.exit(0)
    print(f'TEST 1 FAIL: found_max1={found_max1}, found_max0={found_max0}')
    sys.exit(1)
"
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
else
    echo "TEST 1 FAIL"
fi

# ---------- TEST 2: Behavioral -- the input_lens clamping logic produces no zeros ----------
TOTAL=$((TOTAL + 1))
python3 -c "
import ast, sys, textwrap

# Extract the relevant loop from sample_random_requests and test it directly.
# The function imports sglang internals we can't load, so we exec just the
# input_lens clamping loop with mocked values.

with open('/workspace/sglang/python/sglang/benchmark/datasets/random.py') as f:
    source = f.read()

# Simulate what happens: input_lens = [3, 3, 3, ...] (50 entries)
# num_special_tokens = 3 (from a tokenizer with 3 special tokens)
# After: input_lens[i] = max(?, input_lens[i] - num_special_tokens)
# With max(0,...): input_lens = [0, 0, 0, ...] -- BUG
# With max(1,...): input_lens = [1, 1, 1, ...] -- FIXED

# Extract the clamping expression from the source
import re
# Look for the pattern: max(N, input_lens[i] - num_special_tokens)
match = re.search(r'input_lens\[i\]\s*=\s*max\((\d+),\s*input_lens\[i\]\s*-\s*num_special_tokens\)', source)
if not match:
    print('TEST 2 FAIL: clamping pattern not found in source')
    sys.exit(1)

clamp_val = int(match.group(1))

# Simulate with input_len=3, num_special_tokens=3
input_lens = [3] * 50
num_special_tokens = 3
for i in range(len(input_lens)):
    input_lens[i] = max(clamp_val, input_lens[i] - num_special_tokens)

zeros = sum(1 for x in input_lens if x == 0)
if zeros > 0:
    print(f'TEST 2 FAIL: {zeros} zero-length inputs produced (clamp_val={clamp_val})')
    sys.exit(1)

print(f'TEST 2 PASS: no zero-length inputs (min={min(input_lens)}, clamp_val={clamp_val})')
sys.exit(0)
"
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
else
    echo "TEST 2 FAIL"
fi

# ---------- TEST 3: Anti-stub -- file still has full function logic ----------
TOTAL=$((TOTAL + 1))
python3 -c "
import sys

with open('$TARGET') as f:
    source = f.read()

# Check that the function still contains key logic elements
checks = [
    ('def sample_random_requests' in source, 'function definition'),
    ('input_lens' in source, 'input_lens variable'),
    ('output_lens' in source, 'output_lens variable'),
    ('num_special_tokens' in source or 'special' in source, 'special tokens handling'),
    ('tokenizer' in source, 'tokenizer usage'),
    (len(source) > 500, 'file length > 500 chars'),
]

failures = []
for ok, desc in checks:
    if not ok:
        failures.append(desc)

if failures:
    print(f'TEST 3 FAIL: missing: {failures}')
    sys.exit(1)
else:
    print('TEST 3 PASS: full function logic intact')
    sys.exit(0)
"
if [ $? -eq 0 ]; then
    PASS=$((PASS + 1))
else
    echo "TEST 3 FAIL"
fi

# ---------- Final score ----------
if [ "$TOTAL" -gt 0 ]; then
    SCORE=$(python3 -c "print(min(1.0, $PASS / $TOTAL))")
else
    SCORE="0.0"
fi
echo "Score: $PASS / $TOTAL = $SCORE"
echo "$SCORE" > "$REWARD_FILE"
