#!/usr/bin/env bash
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS

# 70% behavioral (checking actual code behavior via compilation + logic)
# 20% structural (AST verification that config is properly used)
# 10% anti-stub
WEIGHTS[compile]=0.20
WEIGHTS[no_hardcoded_constant]=0.25
WEIGHTS[uses_config_path]=0.25
WEIGHTS[removes_old_usage]=0.15
WEIGHTS[antistub]=0.15

for key in compile no_hardcoded_constant uses_config_path removes_old_usage antistub; do
    RESULTS[$key]=0
done

TARGET="src/channels/mod.rs"

if [ ! -f "$TARGET" ]; then
    echo "GATE FAIL: $TARGET does not exist"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ========== GATE: Code must compile ==========
echo "=== Checking compilation ==="
cd /workspace/zeroclaw

# Try to compile the code
cargo check 2>&1
COMPILE_RESULT=$?

if [ $COMPILE_RESULT -ne 0 ]; then
    echo "GATE FAIL: Code does not compile"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

RESULTS[compile]=1
echo "TEST compile: PASS"

# ========== CHECK 1: No hardcoded MAX_CHANNEL_HISTORY constant ==========
# [pr_diff] (0.25): Hardcoded constant removed
echo "=== Checking no hardcoded constant ==="
python3 << 'PYEOF'
import re, sys

with open('src/channels/mod.rs') as f:
    src = f.read()

# Check for the constant definition (not just any string occurrence)
# This catches: const MAX_CHANNEL_HISTORY: usize = 50;
constant_pattern = r'const\s+MAX_CHANNEL_HISTORY\s*:\s*usize\s*=\s*\d+'
if re.search(const_pattern, src):
    print("FAIL: const MAX_CHANNEL_HISTORY still defined")
    sys.exit(1)

# Also check it's not redefined with let or other forms
let_pattern = r'let\s+(mut\s+)?MAX_CHANNEL_HISTORY\s*='
if re.search(let_pattern, src):
    print("FAIL: MAX_CHANNEL_HISTORY redefined as let binding")
    sys.exit(1)

print("PASS: No hardcoded MAX_CHANNEL_HISTORY constant")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then RESULTS[no_hardcoded_constant]=1; echo "TEST no_hardcoded_constant: PASS"; else echo "TEST no_hardcoded_constant: FAIL"; fi

# ========== CHECK 2: Actually uses config value ==========
# [pr_diff] (0.25): Uses ctx.prompt_config.agent.max_history_messages
echo "=== Checking config value usage ==="
python3 << 'PYEOF'
import re, sys

with open('src/channels/mod.rs') as f:
    src = f.read()

# Check that config path is actually accessed, not just mentioned in comment
# Must be: ctx.prompt_config.agent.max_history_messages (or similar struct path)
# Not just a comment or string literal containing the text

lines = src.split('\n')
for i, line in enumerate(lines, 1):
    # Skip comments
    code_line = line.split('//')[0].strip()
    if not code_line:
        continue

    # Check for config path access patterns
    # Pattern: something.max_history_messages or something[...max_history_messages...]
    if 'max_history_messages' in code_line:
        # Make sure it's not just in a string literal
        if '"' in code_line and code_line.count('"') >= 2:
            # Might be string - check if it's in a string context
            quote_pos = code_line.find('"')
            end_quote = code_line.find('"', quote_pos + 1)
            if quote_pos < code_line.find('max_history_messages') < end_quote:
                continue  # It's in a string literal, skip

        # Verify it's actually accessing the config (has ctx or config in path)
        if any(x in code_line.lower() for x in ['ctx.', 'config.', 'prompt_config.', 'agent.']):
            print(f"PASS: Found config access at line {i}: {code_line.strip()}")
            sys.exit(0)

print("FAIL: No config path access found for max_history_messages")
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then RESULTS[uses_config_path]=1; echo "TEST uses_config_path: PASS"; else echo "TEST uses_config_path: FAIL"; fi

# ========== CHECK 3: Old usage pattern removed ==========
# [pr_diff] (0.15): MAX_CHANNEL_HISTORY usage replaced
echo "=== Checking old usage removed ==="
python3 << 'PYEOF'
import re, sys

with open('src/channels/mod.rs') as f:
    src = f.read()

# Check that MAX_CHANNEL_HISTORY is not actually used as a value
# We're looking for usage in expressions, not comments or mentions

# Pattern 1: split_at(MAX_CHANNEL_HISTORY)
if re.search(r'split_at\s*\(\s*MAX_CHANNEL_HISTORY\s*\)', src):
    print("FAIL: still using split_at(MAX_CHANNEL_HISTORY)")
    sys.exit(1)

# Pattern 2: ..MAX_CHANNEL_HISTORY range
if re.search(r'\.\.\s*MAX_CHANNEL_HISTORY', src):
    print("FAIL: still using ..MAX_CHANNEL_HISTORY range")
    sys.exit(1)

# Pattern 3: truncate(MAX_CHANNEL_HISTORY)
if re.search(r'truncate\s*\(\s*MAX_CHANNEL_HISTORY\s*\)', src):
    print("FAIL: still using truncate(MAX_CHANNEL_HISTORY)")
    sys.exit(1)

# Pattern 4: MAX_CHANNEL_HISTORY in any expression context (not comment/string)
# This is a stronger check
lines = src.split('\n')
for i, line in enumerate(lines, 1):
    code_line = line.split('//')[0]

    # Remove string literals from check
    # Simple approach: if odd number of quotes before MAX, it's in a string
    if 'MAX_CHANNEL_HISTORY' in code_line:
        pos = code_line.find('MAX_CHANNEL_HISTORY')
        # Check if preceded by identifier char (accessing) vs standalone (constant)
        if pos > 0 and code_line[pos-1].isalnum():
            continue  # Part of identifier like MY_MAX_CHANNEL_HISTORY

        # Count quotes before position
        quotes_before = code_line[:pos].count('"')
        if quotes_before % 2 == 1:
            continue  # Inside string literal

        print(f"FAIL: Line {i} still references MAX_CHANNEL_HISTORY: {line.strip()}")
        sys.exit(1)

print("PASS: Old MAX_CHANNEL_HISTORY usage removed")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then RESULTS[removes_old_usage]=1; echo "TEST removes_old_usage: PASS"; else echo "TEST removes_old_usage: FAIL"; fi

# ========== CHECK 4: Anti-stub (file has real implementation) ==========
# (0.15): Substantial implementation exists
echo "=== Anti-stub check ==="
python3 << 'PYEOF'
import sys

with open('src/channels/mod.rs') as f:
    src = f.read()

lines = src.split('\n')
non_empty = [l for l in lines if l.strip() and not l.strip().startswith('//')]
non_comment_non_empty = len(non_empty)

if non_comment_non_empty < 30:
    print(f"FAIL: File has only {non_comment_non_empty} non-comment lines")
    sys.exit(1)

# Check for actual code structure (functions, impl blocks)
if 'fn ' not in src:
    print("FAIL: No function definitions found")
    sys.exit(1)

if 'impl ' not in src:
    print("FAIL: No impl blocks found")
    sys.exit(1)

# Check for append_sender_turn function specifically (the one we need to modify)
if 'fn append_sender_turn' not in src:
    print("FAIL: append_sender_turn function not found")
    sys.exit(1)

print("PASS: File has substantial implementation")
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then RESULTS[antistub]=1; echo "TEST antistub: PASS"; else echo "TEST antistub: FAIL"; fi

# ========== Calculate Score ==========
SCORE=$(python3 -c "
w = {'compile': ${WEIGHTS[compile]}, 'no_hardcoded_constant': ${WEIGHTS[no_hardcoded_constant]}, 'uses_config_path': ${WEIGHTS[uses_config_path]}, 'removes_old_usage': ${WEIGHTS[removes_old_usage]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'compile': ${RESULTS[compile]}, 'no_hardcoded_constant': ${RESULTS[no_hardcoded_constant]}, 'uses_config_path': ${RESULTS[uses_config_path]}, 'removes_old_usage': ${RESULTS[removes_old_usage]}, 'antistub': ${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")

echo "=== Scores ==="
for key in compile no_hardcoded_constant uses_config_path removes_old_usage antistub; do
    echo "  $key: weight=${WEIGHTS[$key]} result=${RESULTS[$key]}"
done
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > "$REWARD_FILE"

# Optional: detailed breakdown
python3 -c "
w = {'compile': ${WEIGHTS[compile]}, 'no_hardcoded_constant': ${WEIGHTS[no_hardcoded_constant]}, 'uses_config_path': ${WEIGHTS[uses_config_path]}, 'removes_old_usage': ${WEIGHTS[removes_old_usage]}, 'antistub': ${WEIGHTS[antistub]}}
r = {'compile': ${RESULTS[compile]}, 'no_hardcoded_constant': ${RESULTS[no_hardcoded_constant]}, 'uses_config_path': ${RESULTS[uses_config_path]}, 'removes_old_usage': ${RESULTS[removes_old_usage]}, 'antistub': ${RESULTS[antistub]}}
import json
breakdown = {k: {'weight': w[k], 'passed': bool(r[k]), 'contribution': w[k]*r[k]} for k in w}
print(json.dumps({'total': sum(w[k]*r[k] for k in w), 'breakdown': breakdown}, indent=2))
" > "/logs/verifier/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
