#!/usr/bin/env bash
#
# Verification for sglang-lscpu-topology-fix
#
# Tests that parse_lscpu_topology() handles malformed lscpu output
# (wrong field counts, empty fields, blank lines) without crashing.
#
# Weights:
#   Behavioral (fail-to-pass):  Test 1 (0.20) + Test 2 (0.20) + Test 3 (0.20) = 0.60
#   Pass-to-pass:               Test 4 (0.10)
#   Structural (supplementary): Test 5 (0.15)
#   Anti-stub:                  Test 6 (0.05)
#   Config-derived:             Test 7 (0.10)
#   Total: 1.00
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0
TARGET="/workspace/sglang/python/sglang/srt/utils/common.py"

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
# Helper: extract parse_lscpu_topology and make it callable without imports
###############################################################################

EXTRACT_FUNC='
import ast, textwrap, subprocess, logging, sys

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("test")

with open("/workspace/sglang/python/sglang/srt/utils/common.py") as f:
    source = f.read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
        func_node = node
        break

if func_node is None:
    print("FAIL: parse_lscpu_topology not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))

ns = {"subprocess": subprocess, "logger": logger, "__builtins__": __builtins__}
exec(func_src, ns)
PARSE_FUNC = ns["parse_lscpu_topology"]
'

###############################################################################
# Test 1 (0.20): Behavioral fail-to-pass — malformed lines don't crash
#   2-field lines, 5-field lines, blank lines, non-numeric data
#   Buggy code: ValueError. Fixed code: handles gracefully.
###############################################################################

echo ""
echo "=== Test 1/6 [0.20]: Malformed lines don't crash ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,0,0,0
1,1,0,0
bad_line_no_commas
2,2
3,3,1,1,extra_field

"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()
        if result is None:
            print("FAIL: function returned None")
            sys.exit(1)
        # Should have parsed at least the 2 valid lines (0,0,0,0 and 1,1,0,0)
        if len(result) < 1:
            print(f"FAIL: expected at least 1 entry from valid lines, got {len(result)}")
            sys.exit(1)
        print(f"PASS: handled malformed input gracefully, returned {len(result)} entries")
        sys.exit(0)
except ValueError as e:
    print(f"FAIL: ValueError raised on malformed input: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected exception: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 2 (0.20): Behavioral fail-to-pass — normal 4-field input parses correctly
#   Verifies cpu, core, socket, node values are correct integers.
###############################################################################

echo ""
echo "=== Test 2/6 [0.20]: Normal input parsed correctly ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,0,0,0
1,1,0,0
2,2,1,1
3,3,1,1
"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()

        if result is None:
            print("FAIL: function returned None")
            sys.exit(1)
        if len(result) != 4:
            print(f"FAIL: expected 4 entries, got {len(result)}")
            sys.exit(1)

        entry = result[0]
        if not (isinstance(entry, (list, tuple)) and len(entry) >= 4):
            print(f"FAIL: entry format wrong: {entry}")
            sys.exit(1)
        if entry[0] != 0 or entry[1] != 0 or entry[2] != 0 or entry[3] != 0:
            print(f"FAIL: first entry values wrong: {entry}")
            sys.exit(1)

        entry = result[2]
        if entry[0] != 2 or entry[1] != 2 or entry[2] != 1 or entry[3] != 1:
            print(f"FAIL: entry[2] values wrong: {entry}")
            sys.exit(1)

        entry = result[3]
        if entry[0] != 3 or entry[1] != 3 or entry[2] != 1 or entry[3] != 1:
            print(f"FAIL: last entry values wrong: {entry}")
            sys.exit(1)

        print("PASS: all 4 entries parsed correctly")
        sys.exit(0)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 3 (0.20): Behavioral fail-to-pass — empty fields handled gracefully
#   e.g. "0,1,,0" or "1,,,"
#   Buggy code: ValueError on int(''). Fixed code: any non-crash behavior is OK
#   (defaulting to 0, skipping the line, etc.)
###############################################################################

echo ""
echo "=== Test 3/6 [0.20]: Empty fields don't crash ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,1,,0
1,,,
2,2,1,1
"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()

        if result is None:
            print("FAIL: function returned None")
            sys.exit(1)

        # At minimum, the valid line "2,2,1,1" should parse
        if len(result) < 1:
            print(f"FAIL: expected at least 1 entry, got 0")
            sys.exit(1)

        # Verify the fully valid line (2,2,1,1) was parsed somewhere in the result
        found_valid = False
        for entry in result:
            if (isinstance(entry, (list, tuple)) and len(entry) >= 4
                    and entry[0] == 2 and entry[1] == 2 and entry[2] == 1 and entry[3] == 1):
                found_valid = True
                break
        if not found_valid:
            print(f"FAIL: valid line (2,2,1,1) not found in result: {result}")
            sys.exit(1)

        print(f"PASS: empty fields handled gracefully, {len(result)} entries returned")
        sys.exit(0)
except ValueError as e:
    print(f"FAIL: ValueError on empty fields: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 4 (0.10): Pass-to-pass — normal input still parses after fix
#   (slightly different input from Test 2 to ensure not over-fitting)
###############################################################################

echo ""
echo "=== Test 4/6 [0.10]: Pass-to-pass — different normal input ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,0,0,0
1,0,0,0
2,1,0,0
3,1,0,0
4,2,1,1
5,2,1,1
6,3,1,1
7,3,1,1
"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()

        if result is None or len(result) != 8:
            print(f"FAIL: expected 8 entries, got {result if result is None else len(result)}")
            sys.exit(1)

        # Spot check a few entries
        if result[0][0] != 0 or result[0][2] != 0:
            print(f"FAIL: entry 0 wrong: {result[0]}")
            sys.exit(1)
        if result[4][0] != 4 or result[4][1] != 2 or result[4][2] != 1 or result[4][3] != 1:
            print(f"FAIL: entry 4 wrong: {result[4]}")
            sys.exit(1)
        if result[7][0] != 7 or result[7][1] != 3:
            print(f"FAIL: entry 7 wrong: {result[7]}")
            sys.exit(1)

        print("PASS: 8-CPU topology parsed correctly")
        sys.exit(0)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

###############################################################################
# Test 5 (0.15): Structural — function has validation/error-handling logic
#   Light check: function exists and contains some form of error handling
#   (try/except, if-guard, continue, len check, etc.)
###############################################################################

echo ""
echo "=== Test 5/6 [0.15]: Structural — has validation logic ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/common.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
        func = node
        break

if func is None:
    print("FAIL: parse_lscpu_topology not found")
    sys.exit(1)

func_source = ast.get_source_segment(source, func) or ""

# Check for SOME form of validation/error-handling. Accept any of:
# try/except, len() check, if-guard with continue/pass, .strip(), isdigit, etc.
has_try = any(isinstance(n, ast.Try) for n in ast.walk(func))
has_continue = any(isinstance(n, ast.Continue) for n in ast.walk(func))
has_len_check = "len(" in func_source
has_if_guard = any(isinstance(n, ast.If) for n in ast.walk(func))
has_except_handler = any(isinstance(n, ast.ExceptHandler) for n in ast.walk(func))

indicators = sum([has_try, has_continue, has_len_check, has_if_guard, has_except_handler])

if indicators >= 2:
    print(f"PASS: found {indicators} validation indicators in function")
    sys.exit(0)
elif indicators == 1:
    print(f"PASS (marginal): found {indicators} validation indicator")
    sys.exit(0)
else:
    print("FAIL: no validation/error-handling logic detected")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.15)"); fi

###############################################################################
# Test 6 (0.15): Anti-stub — function still has real implementation
###############################################################################

echo ""
echo "=== Test 6/7 [0.05]: Anti-stub check ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/common.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
        # Count meaningful statements
        stmts = [s for s in ast.walk(node)
                  if isinstance(s, (ast.Assign, ast.AugAssign, ast.For, ast.If,
                                    ast.Return, ast.Call, ast.Expr, ast.Try))]
        if len(stmts) < 8:
            print(f"FAIL: function too short ({len(stmts)} AST nodes), likely stubbed")
            sys.exit(1)

        func_source = ast.get_source_segment(source, node) or ""
        if "subprocess" not in func_source and "check_output" not in func_source:
            print("FAIL: no subprocess call found — function likely stubbed")
            sys.exit(1)

        if "cpu_info" not in func_source:
            print("FAIL: no cpu_info list found — function likely stubbed")
            sys.exit(1)

        print(f"PASS: function has {len(stmts)} AST nodes, looks real")
        sys.exit(0)

print("FAIL: parse_lscpu_topology not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.05)"); fi

###############################################################################
# Test 7 (0.10): Config-derived — "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ 069c7e4188aca6ef69c0b81dfa05abba49685946
###############################################################################

echo ""
echo "=== Test 7/7 [0.10]: Config-derived — new test files have main guard ==="
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
