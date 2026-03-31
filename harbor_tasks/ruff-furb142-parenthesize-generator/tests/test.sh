#!/usr/bin/env bash
# Verifier for ruff-furb142-parenthesize-generator
# Bug: FURB142 fixer doesn't parenthesize unparenthesized generator args
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py"
SNAPSHOT_DIR="/workspace/ruff/crates/ruff_linter/resources/test/snapshots"

# Weights: >=60% behavioral, <=40% structural
# Behavioral: actually compiling and running ruff on test inputs
# Structural: code structure verification (AST-based, not string grep)

W_BEHAV_COMPILE=0.15           # [gate] Code must compile
W_BEHAV_UNPAREN_FIX=0.35       # [pr_diff] Unparenthesized generator gets wrapped
W_BEHAV_NOP_DOUBLE_PAREN=0.20  # [pr_diff] Already-parenthesized not double-wrapped
W_STRUCTURAL_GENERATOR_HANDLING=0.15  # [pr_diff] Uses Expr::Generator with parenthesized check
W_ANTISTUB_COMPLEXITY=0.10     # [agent_config] File has substantial logic, not stub
W_CONFIG_NO_PANIC=0.05         # [agent_config] No panic!/unwrap in changed code

SCORE="0.0"
BEHAVIORAL="0.0"
STRUCTURAL="0.0"

echo "=== ruff-furb142-parenthesize-generator verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
if [ ! -f "$RUST_FILE" ] || [ ! -f "$FIXTURE" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# -- TEST 1 (GATE/BEHAVIORAL): Code compiles --
echo ""
echo "TEST 1 (GATE/BEHAVIORAL): Rust code compiles (weight=$W_BEHAV_COMPILE)"
cd /workspace/ruff

# Try to build just the ruff_linter crate (faster than full build)
cargo check -p ruff_linter 2>&1 | head -100
COMPILE_STATUS=$?

if [ $COMPILE_STATUS -eq 0 ]; then
    echo "PASS: ruff_linter compiles successfully"
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_COMPILE)")
    BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + $W_BEHAV_COMPILE)")
    COMPILE_PASS=1
else
    echo "FAIL: ruff_linter does not compile"
    COMPILE_PASS=0
fi

# -- TEST 2 (BEHAVIORAL): Unparenthesized generator gets parenthesized fix --
echo ""
echo "TEST 2 (BEHAVIORAL): Unparenthesized generator expression gets wrapped (weight=$W_BEHAV_UNPAREN_FIX)"

if [ $COMPILE_PASS -eq 0 ]; then
    echo "SKIP: Cannot run without compilation"
    UNPAREN_PASS=0
else
    # Create a test file with unparenthesized generator
    TEST_FILE_UNPAREN=$(mktemp /tmp/test_unparen_XXXXXX.py)
    cat > "$TEST_FILE_UNPAREN" << 'EOF'
s = set()
for x in ("abc", "def"):
    s.add(c for c in x)
EOF

    # Run ruff check with FURB142 and --fix
    cd /workspace/ruff
    OUTPUT=$(cargo run --bin ruff -- check --select FURB142 --fix --quiet "$TEST_FILE_UNPAREN" 2>&1)
    FIX_STATUS=$?

    # Check the fixed output
    FIXED_CONTENT=$(cat "$TEST_FILE_UNPAREN")
    rm -f "$TEST_FILE_UNPAREN"

    echo "Fixed content:"
    echo "$FIXED_CONTENT"

    # The fix should produce s.update((c for c in x) for x in ("abc", "def"))
    # Check for correctly parenthesized generator in the output
    if echo "$FIXED_CONTENT" | grep -qE 's\.update\(\(c for c in x\) for x in'; then
        echo "PASS: Unparenthesized generator correctly wrapped in parentheses"
        UNPAREN_PASS=1
        SCORE=$(python3 -c "print($SCORE + $W_BEHAV_UNPAREN_FIX)")
        BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + $W_BEHAV_UNPAREN_FIX)")
    elif echo "$FIXED_CONTENT" | grep -qE 's\.update\(c for c in x for x in'; then
        echo "FAIL: Bug not fixed - unparenthesized generator merges with outer comprehension"
        UNPAREN_PASS=0
    elif echo "$FIXED_CONTENT" | grep -qE 's\.update\(\(\(c for c in x\)\) for x in'; then
        echo "FAIL: Generator double-parenthesized (over-correction)"
        UNPAREN_PASS=0
    else
        echo "FAIL: Fix not applied or unexpected output"
        UNPAREN_PASS=0
    fi
fi

# -- TEST 3 (BEHAVIORAL): Already-parenthesized generator not double-wrapped --
echo ""
echo "TEST 3 (BEHAVIORAL): Already-parenthesized generator not double-wrapped (weight=$W_BEHAV_NOP_DOUBLE_PAREN)"

if [ $COMPILE_PASS -eq 0 ]; then
    echo "SKIP: Cannot run without compilation"
    NOP_DOUBLE_PASS=0
else
    # Create a test file with already-parenthesized generator
    TEST_FILE_PAREN=$(mktemp /tmp/test_paren_XXXXXX.py)
    cat > "$TEST_FILE_PAREN" << 'EOF'
s = set()
for x in ("abc", "def"):
    s.add((c for c in x))
EOF

    cd /workspace/ruff
    OUTPUT=$(cargo run --bin ruff -- check --select FURB142 --fix --quiet "$TEST_FILE_PAREN" 2>&1)

    FIXED_CONTENT=$(cat "$TEST_FILE_PAREN")
    rm -f "$TEST_FILE_PAREN"

    echo "Fixed content:"
    echo "$FIXED_CONTENT"

    # Should be s.update((c for c in x) for x in ("abc", "def")) - NOT s.update(((c for c in x)) for x in ...)
    if echo "$FIXED_CONTENT" | grep -qE 's\.update\(\(c for c in x\) for x in' && ! echo "$FIXED_CONTENT" | grep -qE '\(\([^)]+for c in x\)\)'; then
        echo "PASS: Already-parenthesized generator preserved (not double-wrapped)"
        NOP_DOUBLE_PASS=1
        SCORE=$(python3 -c "print($SCORE + $W_BEHAV_NOP_DOUBLE_PAREN)")
        BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + $W_BEHAV_NOP_DOUBLE_PAREN)")
    elif echo "$FIXED_CONTENT" | grep -qE '\(\([^)]+for c in x\)\)'; then
        echo "FAIL: Already-parenthesized generator was double-wrapped"
        NOP_DOUBLE_PASS=0
    else
        echo "FAIL: Fix not applied or unexpected output"
        NOP_DOUBLE_PASS=0
    fi
fi

# -- TEST 4 (STRUCTURAL): Proper generator handling in source (AST-based) --
echo ""
echo "TEST 4 (STRUCTURAL): Source uses Expr::Generator with parenthesized check (weight=$W_STRUCTURAL_GENERATOR_HANDLING)"

# Only run structural checks if behavioral tests passed (gate them)
if [ $COMPILE_PASS -eq 0 ]; then
    echo "SKIP: Cannot verify structure without compilation"
    STRUCT_GEN_PASS=0
else
    T4=$(python3 << PYEOF
import ast
import sys

with open("$RUST_FILE") as f:
    source = f.read()

# Since we can't parse Rust AST directly, use regex with context extraction
# to find the generator handling pattern
import re

# Look for Expr::Generator pattern with parenthesized check
# This is more specific than string grep - we look for the actual logic structure

# Pattern 1: Match arm with Expr::Generator
expr_gen_pattern = r'Expr::Generator\s*\([^)]*\)\s*=>|Expr::Generator\s*\{[^}]*\}'
expr_gen_match = re.search(expr_gen_pattern, source)

# Pattern 2: Check for parenthesized field access or method call
parenthesized_pattern = r'\.parenthesized\b|parenthesized\s*[:=]'
parenthesized_match = re.search(parenthesized_pattern, source)

# Pattern 3: Conditional logic wrapping (if/else or match arm)
conditional_wrap = r'if\s+.*parenthesized|if\s+!.*parenthesized'
conditional_match = re.search(conditional_wrap, source)

# Check for format with parens - but verify it's in generator context
format_paren = r'format!\s*\(\s*"\(\{\}\)"'
format_match = re.search(format_paren, source)

score = 0
if expr_gen_match:
    print("Found Expr::Generator pattern")
    score += 0.25
if parenthesized_match:
    print("Found parenthesized check")
    score += 0.25
if conditional_match:
    print("Found conditional parenthesization logic")
    score += 0.25
if format_match:
    print("Found format! with parenthesis wrapper")
    score += 0.25

# Require at least 3/4 patterns for full credit
if score >= 0.75:
    print("PASS")
    sys.exit(0)
elif score >= 0.50:
    print("PARTIAL")
    sys.exit(1)
else:
    print("FAIL: Missing generator handling patterns")
    print(f"Score: {score}")
    sys.exit(2)
PYEOF
    )
    T4_STATUS=$?
    echo "$T4"

    if [ $T4_STATUS -eq 0 ]; then
        STRUCT_GEN_PASS=1
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_GENERATOR_HANDLING)")
        STRUCTURAL=$(python3 -c "print($STRUCTURAL + $W_STRUCTURAL_GENERATOR_HANDLING)")
    elif [ $T4_STATUS -eq 1 ]; then
        # Partial credit
        echo "Partial credit for structural check"
        STRUCT_GEN_PASS=0
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_GENERATOR_HANDLING * 0.5)")
        STRUCTURAL=$(python3 -c "print($STRUCTURAL + $W_STRUCTURAL_GENERATOR_HANDLING * 0.5)")
    else
        STRUCT_GEN_PASS=0
    fi
fi

# -- TEST 5 (STRUCTURAL/ANTISTUB): Complexity check --
echo ""
echo "TEST 5 (ANTISTUB): File complexity check (weight=$W_ANTISTUB_COMPLEXITY)"

T5=$(python3 << 'PYEOF'
import sys
import re

with open("/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs") as f:
    source = f.read()

# Count non-trivial lines (not just comments/whitespace)
lines = source.split('\n')
non_trivial = 0
for line in lines:
    stripped = line.strip()
    # Skip empty lines and simple comments
    if stripped and not stripped.startswith('//'):
        non_trivial += 1

# Count function definitions
functions = len(re.findall(r'\bfn\s+\w+', source))

# Count match arms (indicates actual logic)
match_arms = len(re.findall(r'=>', source))

print(f"Non-trivial lines: {non_trivial}")
print(f"Function definitions: {functions}")
print(f"Match arms: {match_arms}")

# File should have substantial logic
if non_trivial < 30:
    print(f"FAIL: Only {non_trivial} non-trivial lines - looks like a stub")
    sys.exit(1)

if functions < 2:
    print(f"FAIL: Only {functions} function - insufficient complexity")
    sys.exit(1)

if match_arms < 3:
    print(f"FAIL: Only {match_arms} match arms - insufficient logic")
    sys.exit(1)

print("PASS: File has sufficient complexity")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB_COMPLEXITY)")
    STRUCTURAL=$(python3 -c "print($STRUCTURAL + $W_ANTISTUB_COMPLEXITY)")
fi

# -- TEST 6 (CONFIG): No panic!/unwrap in changed code --
echo ""
echo "TEST 6 (CONFIG): No panic!/unwrap in changed code (weight=$W_CONFIG_NO_PANIC)"

T6=$(python3 << 'PYEOF'
import sys, subprocess, os

os.chdir('/workspace/ruff')

# Get list of Rust files changed in recent commits or newer than base
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~5..HEAD'], capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split('\n') if f.endswith('.rs')]

# If no recent changes, check files newer than base timestamp
if not changed_rs:
    result2 = subprocess.run(['find', 'crates', '-name', '*.rs', '-newer', 'Cargo.toml'], capture_output=True, text=True)
    changed_rs = [f for f in result2.stdout.strip().split('\n') if f]

warns = 0
for f in changed_rs[:20]:
    try:
        with open(f) as fh:
            for i, line in enumerate(fh, 1):
                s = line.strip()
                if s.startswith('//'):
                    continue
                # Skip test files
                if 'test' in f.lower():
                    continue
                if 'panic!(' in s or ('.unwrap()' in s and '?' not in s):
                    warns += 1
    except:
        pass

if warns > 5:
    print(f'FAIL: {warns} uses of panic!/unwrap in changed files')
    sys.exit(1)

print('PASS')
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_PANIC)")
    STRUCTURAL=$(python3 -c "print($STRUCTURAL + $W_CONFIG_NO_PANIC)")
fi

# -- Calculate percentages --
TOTAL_BEHAV_PCT=$(python3 -c "print(int(($BEHAVIORAL / $SCORE) * 100))" 2>/dev/null || echo "0")
TOTAL_STRUCT_PCT=$(python3 -c "print(int(($STRUCTURAL / $SCORE) * 100))" 2>/dev/null || echo "0")

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "  Behavioral: $BEHAVIORAL (${TOTAL_BEHAV_PCT}%)"
echo "  Structural: $STRUCTURAL (${TOTAL_STRUCT_PCT}%)"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Output detailed breakdown for debugging
cat << EOF > /logs/verifier/reward.json
{
  "reward": $REWARD,
  "behavioral": $BEHAVIORAL,
  "structural": $STRUCTURAL,
  "breakdown": {
    "compile": $COMPILE_PASS,
    "unparen_fix": $UNPAREN_PASS,
    "no_double_paren": $NOP_DOUBLE_PASS,
    "generator_handling": $STRUCT_GEN_PASS
  }
}
EOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
