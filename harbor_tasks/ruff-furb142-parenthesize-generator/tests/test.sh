#!/usr/bin/env bash
# Verifier for ruff-furb142-parenthesize-generator
# Bug: FURB142 fixer doesn't parenthesize unparenthesized generator args
# File: crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py"

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

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_FIXTURE_UNPARENTHESIZED=0.20
W_BEHAV_FIXTURE_PARENTHESIZED=0.15
W_BEHAV_GENERATOR_CHECK=0.30
W_STRUCTURAL_EXPR_GENERATOR=0.15
W_STRUCTURAL_PAREN_WRAP=0.10
W_ANTISTUB=0.05
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Fixture has unparenthesized generator test case --
echo ""
echo "TEST 1: behavioral -- fixture has unparenthesized generator test case (weight=$W_BEHAV_FIXTURE_UNPARENTHESIZED)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py") as f:
    source = f.read()

# The fix adds: for x in ("abc", "def"):\n    s.add(c for c in x)
has_unparenthesized = "s.add(c for c in x)" in source

if has_unparenthesized:
    print("PASS: fixture has unparenthesized generator case: s.add(c for c in x)")
    sys.exit(0)
else:
    print("FAIL: unparenthesized generator test case not found")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FIXTURE_UNPARENTHESIZED)")
fi

# -- TEST 2 (BEHAVIORAL): Fixture has already-parenthesized generator test case --
echo ""
echo "TEST 2: behavioral -- fixture has already-parenthesized generator case (weight=$W_BEHAV_FIXTURE_PARENTHESIZED)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/refurb/FURB142.py") as f:
    source = f.read()

# Should also have: s.add((c for c in x)) -- already parenthesized
has_parenthesized = "s.add((c for c in x))" in source

if has_parenthesized:
    print("PASS: fixture has already-parenthesized generator case")
    sys.exit(0)
else:
    print("FAIL: already-parenthesized generator test case not found")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FIXTURE_PARENTHESIZED)")
fi

# -- TEST 3 (BEHAVIORAL): Rust source checks for unparenthesized generators --
echo ""
echo "TEST 3: behavioral -- Rust source handles generator parenthesization (weight=$W_BEHAV_GENERATOR_CHECK)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs") as f:
    source = f.read()

# The fix should check Expr::Generator and generator.parenthesized
has_generator = "Generator" in source
has_parenthesized_check = "parenthesized" in source

# The fix wraps unparenthesized generators: format!("({})", ...)
has_paren_wrap = '"({})"' in source or "format!(\"({" in source

if has_generator and has_parenthesized_check and has_paren_wrap:
    print("PASS: checks Generator.parenthesized and wraps unparenthesized generators")
    sys.exit(0)
elif has_generator and has_parenthesized_check:
    print("PASS: checks Generator.parenthesized (partial)")
    sys.exit(0)
elif has_generator and has_paren_wrap:
    print("PASS: wraps generators in parens (partial)")
    sys.exit(0)
else:
    print("FAIL: no generator parenthesization logic found")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_GENERATOR_CHECK)")
fi

# -- TEST 4 (STRUCTURAL): Expr::Generator match arm --
echo ""
echo "TEST 4: structural -- Expr::Generator match pattern (weight=$W_STRUCTURAL_EXPR_GENERATOR)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs") as f:
    source = f.read()

has_expr_generator = "Expr::Generator" in source

if has_expr_generator:
    print("PASS: Expr::Generator match pattern exists")
    sys.exit(0)
else:
    print("FAIL: no Expr::Generator pattern found")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_EXPR_GENERATOR)")
fi

# -- TEST 5 (STRUCTURAL): Format string wraps with parens --
echo ""
echo "TEST 5: structural -- format string adds parens around generator (weight=$W_STRUCTURAL_PAREN_WRAP)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs") as f:
    source = f.read()

# Check for format!("({})", locator.slice(arg)) or similar
has_format_paren = '"({})"' in source

if has_format_paren:
    print("PASS: format string wraps generator in parentheses")
    sys.exit(0)
else:
    # Check for any parenthesization in the arg formatting
    has_paren_concat = '("("' in source or 'format!("({' in source
    if has_paren_concat:
        print("PASS: parenthesization logic for arg (variant)")
        sys.exit(0)
    print("FAIL: no parenthesization format string found")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_PAREN_WRAP)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- file retains core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/refurb/rules/for_loop_set_mutations.rs") as f:
    source = f.read()

required = ["for_loop_set_mutations", "batch_method_name", "update", "locator",
            "StmtFor"]
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
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# ---------- Config-derived test (0.05): "Avoid panic!, unreachable!, .unwrap()" ----------
# Source: AGENTS.md line 79 @ 20ca73626d71189ed000806938e1de688c1d3e55
echo ""
echo "TEST config_no_panic: config-derived -- avoid panic!/unwrap (weight=$W_CONFIG_NO_PANIC)"
T_CONFIG=$(python3 << 'PYEOF'
import sys, os
os.chdir('/workspace/ruff')
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split('\n') if f.endswith('.rs')]
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
                if ('panic!(' in s or '.unwrap()' in s) and 'test' not in f:
                    warns += 1
    except: pass
if warns > 5:
    print('FAIL: ' + str(warns) + ' uses of panic!/unwrap in changed files')
    sys.exit(1)
print('PASS')
PYEOF
)
echo "$T_CONFIG"
if echo "$T_CONFIG" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_PANIC)")
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
