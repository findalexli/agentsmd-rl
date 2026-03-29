#!/usr/bin/env bash
#
# Verification for sglang-lscpu-topology-fix
#
# Tests that the agent fixed parse_lscpu_topology() to handle malformed
# lscpu output lines gracefully instead of crashing.
#
# Scoring: 5 tests, reward = PASS / TOTAL (capped at 1.0)
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

PASS=0
TOTAL=5

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
# Test 1: No bare map(int, ...) on unsplit line in parse_lscpu_topology
###############################################################################

echo ""
echo "=== Test 1/5: No bare map(int, line.split) pattern ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/common.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

# Find parse_lscpu_topology function
func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
        func = node
        break

if func is None:
    print("FAIL: parse_lscpu_topology function not found")
    sys.exit(1)

# Check that there's no pattern like: cpu, core, socket, node = map(int, ...)
# which is the buggy original code
source_lines = source.splitlines()
func_start = func.lineno - 1
func_end = func_start + 50  # scan a reasonable window
func_text = "\n".join(source_lines[func_start:func_end])

# The buggy pattern is a tuple unpack from map(int, line...split(...))
if "map(int," in func_text and "split" in func_text:
    # Check if it's still the bare pattern (no guard around it)
    # Look for the specific dangerous pattern: direct unpack of map(int, split)
    for node2 in ast.walk(func):
        if isinstance(node2, ast.Assign):
            if isinstance(node2.value, ast.Call):
                call = node2.value
                if isinstance(call.func, ast.Name) and call.func.id == "map":
                    # Check if targets is a tuple of 4 (cpu, core, socket, node)
                    for t in node2.targets:
                        if isinstance(t, ast.Tuple) and len(t.elts) == 4:
                            print("FAIL: still has bare 'cpu, core, socket, node = map(int, ...)' pattern")
                            sys.exit(1)

print("PASS: no bare map(int, split) unpack found")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Helper: extract parse_lscpu_topology function and exec it in isolation
# (avoids importing sglang which pulls in torch/triton)
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

# Build a namespace with the deps the function needs
ns = {"subprocess": subprocess, "logger": logger, "__builtins__": __builtins__}
exec(func_src, ns)
PARSE_FUNC = ns["parse_lscpu_topology"]
'

###############################################################################
# Test 2: Behavioral - malformed lines don't crash
###############################################################################

echo ""
echo "=== Test 2/5: Malformed lines don't crash ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,0,0,0
1,1,0,0
bad_line
2,2
3,3,1,1,extra_field
"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()
        if result is None:
            print("FAIL: function returned None")
            sys.exit(1)
        print(f"PASS: function returned {len(result)} entries without crashing")
        sys.exit(0)
except ValueError as e:
    print(f"FAIL: ValueError raised: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected exception: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Test 3: Behavioral - normal 4-field input works correctly
###############################################################################

echo ""
echo "=== Test 3/5: Normal input parsed correctly ==="
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

        entry = result[3]
        if entry[0] != 3 or entry[1] != 3 or entry[2] != 1 or entry[3] != 1:
            print(f"FAIL: last entry values wrong: {entry}")
            sys.exit(1)

        print(f"PASS: all 4 entries parsed correctly")
        sys.exit(0)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Test 4: Empty fields default to 0
###############################################################################

echo ""
echo "=== Test 4/5: Empty fields default to 0 ==="
python3 << PYEOF
${EXTRACT_FUNC}

import unittest.mock

mock_output = """# CPU,Core,Socket,Node
0,1,,0
1,,,
"""

try:
    with unittest.mock.patch("subprocess.check_output", return_value=mock_output):
        result = PARSE_FUNC()

        if result is None or len(result) == 0:
            print("FAIL: no entries returned for lines with empty fields")
            sys.exit(1)

        entry = result[0]
        if entry[0] != 0:
            print(f"FAIL: cpu should be 0, got {entry[0]}")
            sys.exit(1)
        if entry[1] != 1:
            print(f"FAIL: core should be 1, got {entry[1]}")
            sys.exit(1)
        if entry[2] != 0:
            print(f"FAIL: socket should default to 0, got {entry[2]}")
            sys.exit(1)
        if entry[3] != 0:
            print(f"FAIL: node should be 0, got {entry[3]}")
            sys.exit(1)

        print(f"PASS: empty fields defaulted to 0 correctly ({len(result)} entries)")
        sys.exit(0)
except ValueError as e:
    print(f"FAIL: ValueError on empty fields: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: {type(e).__name__}: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Test 5: Anti-stub - function still has real implementation
###############################################################################

echo ""
echo "=== Test 5/5: Anti-stub check ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/common.py", "r") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "parse_lscpu_topology":
        # Count meaningful statements (exclude docstrings)
        stmts = [s for s in ast.walk(node)
                  if isinstance(s, (ast.Assign, ast.AugAssign, ast.For, ast.If,
                                    ast.Return, ast.Call, ast.Expr, ast.Try))]
        if len(stmts) < 8:
            print(f"FAIL: function too short ({len(stmts)} AST nodes), likely stubbed")
            sys.exit(1)

        # Must contain subprocess call and return
        func_source = ast.get_source_segment(source, node) or ""
        if "subprocess" not in func_source and "check_output" not in func_source:
            print("FAIL: no subprocess call found - function likely stubbed")
            sys.exit(1)

        if "cpu_info" not in func_source:
            print("FAIL: no cpu_info list found - function likely stubbed")
            sys.exit(1)

        print(f"PASS: function has {len(stmts)} AST nodes, looks real")
        sys.exit(0)

print("FAIL: parse_lscpu_topology not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then PASS=$((PASS + 1)); fi

###############################################################################
# Final score
###############################################################################

echo ""
echo "=== Results: $PASS / $TOTAL ==="
REWARD=$(python3 -c "print(min(1.0, round($PASS / $TOTAL, 4)))")
echo "$REWARD" > "$REWARD_FILE"
echo "Reward: $REWARD"
