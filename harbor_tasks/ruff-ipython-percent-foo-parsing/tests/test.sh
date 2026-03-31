#!/usr/bin/env bash
# Verifier for ruff-ipython-percent-foo-parsing
# Bug: %foo? parsed incorrectly in IPython assignment context
# Fixed by: IpyEscapeLexContext enum distinguishing Assignment vs LogicalLineStart
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== ruff-ipython-percent-foo-parsing verifier ==="

LEXER_FILE="/workspace/ruff/crates/ruff_python_parser/src/lexer.rs"
TESTS_FILE="/workspace/ruff/crates/ruff_python_parser/src/parser/tests.rs"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_INT_TEST=0.35      # [pr_diff] Integration test for %foo? assignment
W_BEHAV_SNAPSHOT=0.25      # [pr_diff] Snapshot test matches expected output
W_P2P_ALL_TESTS=0.15       # [pr_diff] No regressions in lexer tests
W_STRUCTURAL_ENUM=0.15     # [pr_diff] IpyEscapeLexContext enum exists
W_ANTISTUB=0.10            # [agent_config] AGENTS.md:78 - avoid stub implementations

cd /workspace/ruff

# -- GATE: files exist --
echo "GATE: Checking target files"
if [ ! -f "$LEXER_FILE" ] || [ ! -f "$TESTS_FILE" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# -- GATE: code compiles --
echo ""
echo "GATE: Checking compilation"
cargo check -p ruff_python_parser 2>&1 | tail -20
if [ $? -ne 0 ]; then
    echo "GATE FAIL: code does not compile"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: compiles"

SCORE=0.0
BEHAV_PASSED=false

# -- TEST 1 (BEHAVIORAL): ipython_escape_commands integration test --
# [pr_diff] (0.35): Tests bar = %foo? and baz = !pwd? parse correctly
echo ""
echo "TEST 1: behavioral -- ipython_escape_commands integration (weight=$W_BEHAV_INT_TEST)"
cargo test -p ruff_python_parser --lib parser::tests::ipython_escape_commands -- --nocapture 2>&1 | tail -20
if [ $? -eq 0 ]; then
    echo "PASS: integration test passes"
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_INT_TEST)")
    BEHAV_PASSED=true
else
    echo "FAIL: integration test failed"
fi

# -- TEST 2 (BEHAVIORAL): Snapshot test for assignment --
# [pr_diff] (0.25): Lexer snapshot matches expected tokenization
echo ""
echo "TEST 2: behavioral -- ipython_escape_command_assignment snapshot (weight=$W_BEHAV_SNAPSHOT)"
cargo test -p ruff_python_parser --lib lexer::tests::ipython_escape_command_assignment -- --nocapture 2>&1 | tail -20
if [ $? -eq 0 ]; then
    echo "PASS: assignment snapshot test passes"
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_SNAPSHOT)")
    BEHAV_PASSED=true
else
    echo "FAIL: assignment snapshot test failed"
fi

# -- TEST 3 (P2P): All lexer tests pass (regression check) --
# [agent_config] (0.15): AGENTS.md:78 - check existing tests still pass
echo ""
echo "TEST 3: pass-to-pass -- lexer test suite (weight=$W_P2P_ALL_TESTS)"
if [ "$BEHAV_PASSED" = true ]; then
    cargo test -p ruff_python_parser --lib lexer::tests 2>&1 | tail -20
    if [ $? -eq 0 ]; then
        echo "PASS: all lexer tests pass"
        SCORE=$(python3 -c "print($SCORE + $W_P2P_ALL_TESTS)")
    else
        echo "FAIL: some lexer tests failed (regression)"
    fi
else
    echo "SKIPPED: Need at least one behavioral test to pass first"
fi

# -- TEST 4 (STRUCTURAL): IpyEscapeLexContext implementation --
# [pr_diff] (0.15): IpyEscapeLexContext with Assignment and LogicalLineStart variants
echo ""
echo "TEST 4: structural -- IpyEscapeLexContext enum (weight=$W_STRUCTURAL_ENUM)"
if [ "$BEHAV_PASSED" = true ]; then
    python3 << 'PYEOF'
import sys
with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    src = f.read()

has_enum = "enum IpyEscapeLexContext" in src
has_assignment = "IpyEscapeLexContext::Assignment" in src
has_line_start = "IpyEscapeLexContext::LogicalLineStart" in src
has_allows_help = "allows_help_end" in src

score = 0
if has_enum: score += 0.25
if has_assignment: score += 0.25
if has_line_start: score += 0.25
if has_allows_help: score += 0.25

if score >= 0.75:
    print(f"PASS: IpyEscapeLexContext fully implemented (score={score})")
    sys.exit(0)
elif score >= 0.5:
    print(f"PARTIAL: partial implementation (score={score})")
    sys.exit(2)
else:
    print(f"FAIL: missing implementation elements (score={score})")
    sys.exit(1)
PYEOF
    T4_EXIT=$?
    if [ $T4_EXIT -eq 0 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_ENUM)")
    elif [ $T4_EXIT -eq 2 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_ENUM * 0.5)")
    fi
else
    echo "SKIPPED: Behavioral tests must pass first"
fi

# -- TEST 5: Anti-stub --
# [agent_config] (0.10): AGENTS.md:78 - substantial implementation
echo ""
echo "TEST 5: anti-stub -- lexer implementation substance (weight=$W_ANTISTUB)"
if [ "$BEHAV_PASSED" = true ]; then
    python3 << 'PYEOF'
import sys
with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    src = f.read()

# Count non-empty code lines
lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith('//')]
code_lines = len(lines)

# Check for required lexer implementation elements
required = [
    "lex_ipython_escape_command",
    "IpyEscapeKind",
    "question_count",
    "TokenKind::IpyEscapeCommand",
]
missing = [r for r in required if r not in src]

if code_lines < 300 or missing:
    print(f"FAIL: stub detected ({code_lines} lines, missing: {missing})")
    sys.exit(1)
else:
    print(f"PASS: {code_lines} code lines, all required symbols present")
    sys.exit(0)
PYEOF
    if [ $? -eq 0 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
    fi
else
    echo "SKIPPED: Behavioral tests must pass first"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Final Reward: $REWARD"
echo ""
echo "Breakdown:"
BEHAV_VAL=$(python3 -c "b = min($SCORE, $W_BEHAV_INT_TEST + $W_BEHAV_SNAPSHOT); print(f'{b:.2f}')")
STRUCT_VAL=$(python3 -c "s = max(0, $SCORE - $W_BEHAV_INT_TEST - $W_BEHAV_SNAPSHOT); print(f'{s:.2f}')")
echo "  - Behavioral (F2P): $BEHAV_VAL target: >=0.60"
echo "  - Structural+P2P: $STRUCT_VAL target: <=0.40"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
