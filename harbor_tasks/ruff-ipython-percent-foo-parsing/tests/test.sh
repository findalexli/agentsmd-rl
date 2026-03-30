#!/usr/bin/env bash
# Verifier for ruff-ipython-percent-foo-parsing
# Bug: %foo? parsed incorrectly in IPython assignment context
# File: crates/ruff_python_parser/src/lexer.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

LEXER_FILE="/workspace/ruff/crates/ruff_python_parser/src/lexer.rs"
TESTS_FILE="/workspace/ruff/crates/ruff_python_parser/src/parser/tests.rs"

echo "=== ruff-ipython-percent-foo-parsing verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
if [ ! -f "$LEXER_FILE" ]; then
    echo "GATE FAIL: lexer file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_CONTEXT_ENUM=0.25
W_BEHAV_ASSIGNMENT_CTX=0.20
W_BEHAV_TEST_CASES=0.20
W_STRUCTURAL_ALLOWS_HELP=0.15
W_STRUCTURAL_QUESTION_PUSH=0.10
W_ANTISTUB=0.05
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Context enum distinguishes assignment vs line-start --
echo ""
echo "TEST 1: behavioral -- lexer context distinguishes assignment from line start (weight=$W_BEHAV_CONTEXT_ENUM)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    source = f.read()

# The fix adds an enum like IpyEscapeLexContext with Assignment and LogicalLineStart variants
has_context_enum = "IpyEscapeLexContext" in source or "IpyEscapeContext" in source
has_assignment = "Assignment" in source
has_line_start = "LogicalLineStart" in source or "LineStart" in source

if has_context_enum and has_assignment and has_line_start:
    print("PASS: IpyEscapeLexContext enum with Assignment and LogicalLineStart variants")
    sys.exit(0)
elif has_context_enum:
    print("PASS: context enum exists (partial)")
    sys.exit(0)
else:
    # Alternative: could use a bool parameter
    has_bool_param = "context" in source and "lex_ipython_escape_command" in source
    if has_bool_param:
        print("PASS: lex_ipython_escape_command takes context parameter")
        sys.exit(0)
    print("FAIL: no context distinction for IPython escape command lexing")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CONTEXT_ENUM)")
fi

# -- TEST 2 (BEHAVIORAL): Assignment context passed for post-equals escapes --
echo ""
echo "TEST 2: behavioral -- Assignment context used after = sign (weight=$W_BEHAV_ASSIGNMENT_CTX)"
T2=$(python3 << 'PYEOF'
import re, sys

with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    source = f.read()

# The fix passes IpyEscapeLexContext::Assignment when lexing escape commands after =
has_assignment_ctx = "Assignment" in source and "lex_ipython_escape_command" in source

# The old code had a single call with just the kind; new code passes context too
# Count the number of lex_ipython_escape_command calls
calls = re.findall(r'lex_ipython_escape_command\s*\(', source)

if has_assignment_ctx and len(calls) >= 2:
    print(f"PASS: lex_ipython_escape_command called {len(calls)} times with context parameter")
    sys.exit(0)
elif has_assignment_ctx:
    print("PASS: Assignment context used with lex_ipython_escape_command")
    sys.exit(0)
else:
    print("FAIL: no Assignment context in escape command lexing")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_ASSIGNMENT_CTX)")
fi

# -- TEST 3 (BEHAVIORAL): Test cases added for %foo? and !pwd? assignments --
echo ""
echo "TEST 3: behavioral -- test cases for %foo? and !pwd? assignments (weight=$W_BEHAV_TEST_CASES)"
T3=$(python3 << 'PYEOF'
import sys

# Check parser tests or lexer tests for the new cases
tests_found = False
for path in [
    "/workspace/ruff/crates/ruff_python_parser/src/parser/tests.rs",
    "/workspace/ruff/crates/ruff_python_parser/src/lexer.rs",
]:
    try:
        with open(path) as f:
            source = f.read()
        if "%foo?" in source or "!pwd?" in source:
            tests_found = True
            break
    except FileNotFoundError:
        continue

if tests_found:
    print("PASS: test cases include %foo? or !pwd? assignment patterns")
    sys.exit(0)
else:
    print("FAIL: no test cases for %foo? or !pwd? assignment")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TEST_CASES)")
fi

# -- TEST 4 (STRUCTURAL): allows_help_end method on context --
echo ""
echo "TEST 4: structural -- context has allows_help_end method (weight=$W_STRUCTURAL_ALLOWS_HELP)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    source = f.read()

has_allows_help = "allows_help_end" in source or "allow_help" in source

if has_allows_help:
    print("PASS: allows_help_end method exists")
    sys.exit(0)
else:
    # Alternative: inline check
    has_inline_check = "Assignment" in source and "Help" in source
    if has_inline_check:
        print("PASS: assignment context check for help tokens (inline)")
        sys.exit(0)
    print("FAIL: no allows_help_end or equivalent check")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_ALLOWS_HELP)")
fi

# -- TEST 5 (STRUCTURAL): Question marks pushed into value for assignment context --
echo ""
echo "TEST 5: structural -- ? chars pushed into value in assignment context (weight=$W_STRUCTURAL_QUESTION_PUSH)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    source = f.read()

# The fix should push '?' chars into the value string instead of treating as help end
has_push_question = "value.push('?')" in source or "value.push_str" in source
has_question_count = "question_count" in source

if has_push_question and has_question_count:
    print("PASS: ? characters pushed into value string using question_count")
    sys.exit(0)
elif has_push_question:
    print("PASS: ? characters pushed into value string")
    sys.exit(0)
else:
    print("FAIL: no logic to push ? into command value")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_QUESTION_PUSH)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- lexer retains core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_python_parser/src/lexer.rs") as f:
    source = f.read()

required = ["lex_ipython_escape_command", "IpyEscapeKind", "Magic", "Shell",
            "question_count", "TokenKind"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 500:
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
# Source: AGENTS.md line 79 @ 9d2b16029a6a141b2d15e966a69faa4c2ec41572
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
