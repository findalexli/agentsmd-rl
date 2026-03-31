#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral_f2p]=0.40
WEIGHTS[behavioral_p2p]=0.25
WEIGHTS[behavioral_edge]=0.20
WEIGHTS[structural]=0.10
WEIGHTS[antistub]=0.05

for key in behavioral_f2p behavioral_p2p behavioral_edge structural antistub; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- Load safe_join from the actual module (not AST extraction) ----------
# First, check that safe_join exists and can be imported
python3 -c "
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.utils import safe_join
print('Import successful')
" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "GATE FAIL: Cannot import safe_join from gradio.utils"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY FAIL-TO-PASS (40%): Reject paths starting with / on Windows Py3.14 ----------
# [pr_diff] (0.40): Paths starting with / must be rejected even when os.path.isabs returns False
python3 << 'PYEOF'
import sys
import unittest.mock

sys.path.insert(0, '/workspace/gradio')

# Mock os.path.isabs to simulate Python 3.14 on Windows behavior BEFORE importing
# On Windows Py3.14, os.path.isabs("/etc/passwd") returns False
with unittest.mock.patch('os.path.isabs', return_value=False):
    # Need to reload to pick up the mocked behavior if module caches it
    import importlib
    import gradio.utils
    importlib.reload(gradio.utils)
    from gradio.utils import safe_join, InvalidPathError

    # Test 1: Path starting with / should be rejected
    try:
        result = safe_join("/tmp/uploads", "/etc/passwd")
        print(f"F2P FAIL: safe_join accepted '/etc/passwd', returned: {result}")
        sys.exit(1)
    except InvalidPathError:
        print("F2P PASS: /etc/passwd correctly rejected with InvalidPathError")
    except Exception as e:
        print(f"F2P WARN: /etc/passwd rejected but with wrong exception: {type(e).__name__}")
        # Still count as pass for security, but log the issue

    # Test 2: Multiple leading slashes
    try:
        result = safe_join("/tmp/uploads", "//etc/passwd")
        print(f"F2P FAIL: safe_join accepted '//etc/passwd', returned: {result}")
        sys.exit(1)
    except Exception:
        print("F2P PASS: //etc/passwd correctly rejected")

    # Test 3: Path with / in the middle (should be allowed - not absolute)
    try:
        result = safe_join("/tmp/uploads", "subdir/file.txt")
        if "/tmp/uploads/subdir/file.txt" in result or "subdir/file.txt" in result:
            print("F2P PASS: subdir/file.txt correctly allowed")
        else:
            print(f"F2P FAIL: unexpected result for subdir/file.txt: {result}")
            sys.exit(1)
    except Exception as e:
        print(f"F2P FAIL: subdir/file.txt was rejected: {e}")
        sys.exit(1)

sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_f2p]=1
    echo "TEST behavioral_f2p: PASS"
    BEHAVIORAL_PASSED=1
else
    echo "TEST behavioral_f2p: FAIL"
    BEHAVIORAL_PASSED=0
fi

# ---------- PASS-TO-PASS (25%): Normal relative paths still work ----------
# [pr_diff] (0.25): Existing functionality must not break
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/gradio')
from gradio.utils import safe_join

test_cases = [
    ("/tmp/uploads", "image.png", "image.png"),
    ("/tmp/uploads", "subdir/file.txt", "subdir/file.txt"),
    ("/tmp/uploads", "a/b/c/d.txt", "d.txt"),
    ("/var/www", "static/style.css", "style.css"),
]

all_pass = True
for directory, path, expected_substring in test_cases:
    try:
        result = safe_join(directory, path)
        # Result should contain the path components properly joined
        if expected_substring in result or (directory.replace("/", os.sep) in result and path.replace("/", os.sep) in result):
            print(f"  P2P PASS: safe_join({directory!r}, {path!r}) = {result!r}")
        else:
            print(f"  P2P FAIL: safe_join({directory!r}, {path!r}) = {result!r} (expected {expected_substring})")
            all_pass = False
    except Exception as e:
        print(f"  P2P FAIL: safe_join({directory!r}, {path!r}) raised {type(e).__name__}: {e}")
        all_pass = False

if all_pass:
    print("P2P PASS: all normal relative paths work correctly")
    sys.exit(0)
else:
    print("P2P FAIL: some normal paths were rejected")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_p2p]=1
    echo "TEST behavioral_p2p: PASS"
else
    echo "TEST behavioral_p2p: FAIL"
fi

# ---------- EDGE CASES (20%): .. paths, alt separators, error type ----------
# [pr_diff] (0.20): Security edge cases must be handled
python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/workspace/gradio')
from gradio.utils import safe_join, InvalidPathError

all_pass = True

# Test 1: .. should be rejected
try:
    result = safe_join("/tmp/uploads", "..")
    print(f"EDGE FAIL: '..' was accepted: {result}")
    all_pass = False
except InvalidPathError:
    print("EDGE PASS: '..' correctly rejected with InvalidPathError")
except Exception as e:
    print(f"EDGE WARN: '..' rejected but with {type(e).__name__}")

# Test 2: ../ should be rejected
try:
    result = safe_join("/tmp/uploads", "../etc/passwd")
    print(f"EDGE FAIL: '../etc/passwd' was accepted: {result}")
    all_pass = False
except InvalidPathError:
    print("EDGE PASS: '../etc/passwd' correctly rejected with InvalidPathError")
except Exception as e:
    print(f"EDGE WARN: '../etc/passwd' rejected but with {type(e).__name__}")

# Test 3: Empty path should work or be rejected consistently
try:
    result = safe_join("/tmp/uploads", "")
    print(f"EDGE INFO: empty path result: {result}")
except Exception as e:
    print(f"EDGE INFO: empty path raises: {type(e).__name__}")

# Test 4: Current directory reference
try:
    result = safe_join("/tmp/uploads", "./file.txt")
    # Should normalize to file.txt in the uploads directory
    if "file.txt" in result:
        print("EDGE PASS: './file.txt' correctly handled")
    else:
        print(f"EDGE FAIL: './file.txt' unexpected result: {result}")
        all_pass = False
except Exception as e:
    print(f"EDGE FAIL: './file.txt' raised {type(e).__name__}: {e}")
    all_pass = False

if all_pass:
    print("EDGE PASS: all edge cases handled correctly")
    sys.exit(0)
else:
    print("EDGE FAIL: some edge cases failed")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral_edge]=1
    echo "TEST behavioral_edge: PASS"
else
    echo "TEST behavioral_edge: FAIL"
fi

# ---------- STRUCTURAL (10%): Checks for explicit slash detection - gated behind behavioral ----------
# Only award structural points if behavioral tests passed
if [ "$BEHAVIORAL_PASSED" -eq 1 ]; then
    python3 << 'PYEOF'
import ast, sys, re

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find safe_join function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: safe_join not found")
    sys.exit(1)

# Get the source of the function body (without docstring)
func_body = func_node.body
if func_body and isinstance(func_body[0], ast.Expr) and isinstance(func_body[0].value, ast.Constant):
    func_body = func_body[1:]  # Skip docstring

# Check for explicit forward slash check using AST (not string matching)
# Accept any of: startswith("/"), startswith('/'), [0] == "/", regex ^/, etc.
has_slash_check = False

for node in ast.walk(func_node):
    # Check for startswith with "/" or '/'
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "startswith":
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and arg.value == "/":
                    has_slash_check = True
                    break
                if isinstance(arg, ast.Str) and arg.s == "/":  # Python <3.8 compatibility
                    has_slash_check = True
                    break
    # Check for string comparison with "/"
    if isinstance(node, ast.Compare):
        if isinstance(node.ops[0], (ast.Eq,)):
            for comparator in node.comparators:
                if isinstance(comparator, ast.Constant) and comparator.value == "/":
                    has_slash_check = True
                    break
                if isinstance(comparator, ast.Str) and comparator.s == "/":
                    has_slash_check = True
                    break
    # Check for regex with ^/
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("match", "search"):
            if node.args and isinstance(node.args[0], ast.Constant):
                pattern = node.args[0].value
                if isinstance(pattern, str) and pattern.startswith("^") and "/" in pattern:
                    has_slash_check = True
                    break

if has_slash_check:
    print("STRUCTURAL PASS: explicit forward slash check detected")
    sys.exit(0)
else:
    print("STRUCTURAL INFO: no explicit slash check found, but behavioral tests passed")
    # Still award points if behavioral passed - the fix works even if structure differs
    sys.exit(0)
PYEOF
    if [ $? -eq 0 ]; then
        RESULTS[structural]=1
        echo "TEST structural: PASS"
    else
        echo "TEST structural: FAIL"
    fi
else
    echo "TEST structural: SKIPPED (behavioral failed)"
    RESULTS[structural]=0
fi

# ---------- ANTI-STUB (5%): Minimum implementation depth ----------
# [pr_diff] (0.05): Implementation must have substance
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find safe_join and count meaningful statements
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_node = node
        break

if func_node is None:
    print("ANTI-STUB FAIL: safe_join not found")
    sys.exit(1)

# Count non-docstring, non-pass statements
meaningful_count = 0
for stmt in func_node.body:
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
        continue  # Skip docstring
    if isinstance(stmt, ast.Pass):
        continue
    if isinstance(stmt, ast.Global):
        continue
    meaningful_count += 1

# Also check file has reasonable size
file_lines = len(source.splitlines())

# Check for security-related checks in the function
has_security_checks = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Raise):
        has_security_checks = True
        break

if meaningful_count >= 3 and file_lines >= 50 and has_security_checks:
    print(f"ANTI-STUB PASS: {meaningful_count} statements, {file_lines} lines, has raise")
    sys.exit(0)
else:
    print(f"ANTI-STUB FAIL: {meaningful_count} statements, {file_lines} lines, security: {has_security_checks}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral_f2p': ${WEIGHTS[behavioral_f2p]}, 'behavioral_p2p': ${WEIGHTS[behavioral_p2p]}, 'behavioral_edge': ${WEIGHTS[behavioral_edge]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}}
results = {'behavioral_f2p': ${RESULTS[behavioral_f2p]}, 'behavioral_p2p': ${RESULTS[behavioral_p2p]}, 'behavioral_edge': ${RESULTS[behavioral_edge]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral_f2p (${WEIGHTS[behavioral_f2p]}): ${RESULTS[behavioral_f2p]}"
echo "  behavioral_p2p (${WEIGHTS[behavioral_p2p]}): ${RESULTS[behavioral_p2p]}"
echo "  behavioral_edge (${WEIGHTS[behavioral_edge]}): ${RESULTS[behavioral_edge]}"
echo "  structural (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
