#!/usr/bin/env bash
# Verifier for ruff-ruf050-parenthesize
# Bug: RUF050 fix produces invalid Python for multiline expressions
# File: crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/ruff/RUF050.py"

echo "=== ruff-ruf050-parenthesize verifier ==="

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
W_BEHAV_MULTILINE_CASE=0.20
W_BEHAV_LINEBREAK_DETECT=0.25
W_BEHAV_PARENS_PRESERVE=0.20
W_STRUCTURAL_HELPER_FN=0.15
W_STRUCTURAL_TOKEN_SCAN=0.10
W_ANTISTUB=0.05
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Fixture has multiline expression test case --
echo ""
echo "TEST 1: behavioral -- fixture has multiline expression test case (weight=$W_BEHAV_MULTILINE_CASE)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/ruff/RUF050.py") as f:
    source = f.read()

# The fix adds test cases for multiline expressions in if conditions
# e.g.: if (\n    id(0)\n    + 0\n):\n    pass
has_multiline_id = "id(0)" in source and "+ 0" in source
has_multiline_comment = "ultiline" in source.lower()

if has_multiline_id:
    print("PASS: fixture has multiline expression test case (id(0) + 0)")
    sys.exit(0)
elif has_multiline_comment:
    print("PASS: fixture has multiline-related test case")
    sys.exit(0)
else:
    print("FAIL: no multiline expression test case found in fixture")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MULTILINE_CASE)")
fi

# -- TEST 2 (BEHAVIORAL): Rust source detects top-level line breaks --
echo ""
echo "TEST 2: behavioral -- detects top-level line breaks in expressions (weight=$W_BEHAV_LINEBREAK_DETECT)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs") as f:
    source = f.read()

# The fix must detect line breaks at top level (not inside parens/brackets)
# Look for: Newline or NonLogicalNewline token handling with nesting tracking
has_newline_check = "Newline" in source or "NonLogicalNewline" in source
has_nesting = "nesting" in source
has_line_break_fn = "line_break" in source.lower() or "has_top_level" in source

if has_newline_check and has_nesting:
    print("PASS: detects newlines with nesting tracking")
    sys.exit(0)
elif has_line_break_fn:
    print("PASS: has line break detection function")
    sys.exit(0)
else:
    print("FAIL: no top-level line break detection found")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_LINEBREAK_DETECT)")
fi

# -- TEST 3 (BEHAVIORAL): Preserves or adds parentheses for multiline --
echo ""
echo "TEST 3: behavioral -- preserves/adds parentheses for multiline expressions (weight=$W_BEHAV_PARENS_PRESERVE)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs") as f:
    source = f.read()

# The fix should use parenthesized_range to preserve existing parens
# or wrap with format!("({condition_text})") for multiline expressions
has_parenthesized_range = "parenthesized_range" in source
has_paren_wrap = '("({' in source or "format!(\"({" in source

if has_parenthesized_range and has_paren_wrap:
    print("PASS: uses parenthesized_range and wraps multiline expressions")
    sys.exit(0)
elif has_parenthesized_range:
    print("PASS: uses parenthesized_range to preserve existing parens")
    sys.exit(0)
elif has_paren_wrap:
    print("PASS: wraps multiline expressions in parentheses")
    sys.exit(0)
else:
    print("FAIL: no parenthesization logic for multiline expressions")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_PARENS_PRESERVE)")
fi

# -- TEST 4 (STRUCTURAL): Helper function extracted --
echo ""
echo "TEST 4: structural -- helper function for condition formatting (weight=$W_STRUCTURAL_HELPER_FN)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs") as f:
    source = f.read()

# The fix extracts the replacement logic into a helper function
has_helper = "condition_as_expression_statement" in source or "condition_as_expr" in source

if has_helper:
    print("PASS: helper function for condition expression formatting exists")
    sys.exit(0)
else:
    # Check if the logic is inline but handles multiline
    has_multiline_handling = ("line_break" in source.lower() or "has_top_level" in source) and "parenthes" in source.lower()
    if has_multiline_handling:
        print("PASS: multiline parenthesization logic present (inline)")
        sys.exit(0)
    else:
        print("FAIL: no helper function or multiline handling found")
        sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_HELPER_FN)")
fi

# -- TEST 5 (STRUCTURAL): Token scanning with bracket nesting --
echo ""
echo "TEST 5: structural -- token scanning tracks bracket nesting (weight=$W_STRUCTURAL_TOKEN_SCAN)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs") as f:
    source = f.read()

# The fix scans tokens and tracks nesting depth
has_lpar = "Lpar" in source
has_rpar = "Rpar" in source
has_lsqb = "Lsqb" in source or "Lbrace" in source

if has_lpar and has_rpar and has_lsqb:
    print("PASS: token scanning tracks bracket/paren nesting")
    sys.exit(0)
elif has_lpar and has_rpar:
    print("PASS: token scanning tracks paren nesting (partial)")
    sys.exit(0)
else:
    print("FAIL: no bracket nesting tracking in token scan")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_TOKEN_SCAN)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- files retain core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs") as f:
    source = f.read()

required = ["unnecessary_if", "checker", "StmtIf", "has_side_effects",
            "Edit", "Fix"]
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
# Source: AGENTS.md line 79 @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
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
