#!/usr/bin/env bash
#
# Verification for slime-encoder-only-attr-missing
# Tests that launch_server_process handles missing encoder_only attribute.
# [pr_diff] Primary fix: hasattr/getattr guard before accessing encoder_only
#
set +e

TARGET="/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[f2p_crash]=0.40
WEIGHTS[f2p_branch]=0.30
WEIGHTS[p2p_existing]=0.20
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in f2p_crash f2p_branch p2p_existing config_no_wildcard config_no_bare_print; do
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

# ---------- PRIMARY 1 (40%): FAIL-TO-PASS - No AttributeError on missing encoder_only ----------
# [pr_diff] (0.40): Fix AttributeError when server_args lacks encoder_only attribute
python3 << 'PYEOF'
import ast
import sys
import textwrap
from typing import Set

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("F2P_FAIL: launch_server_process function not found")
    sys.exit(1)

# Algorithm: Find all direct attribute accesses to encoder_only
# and verify they are inside a guard (hasattr check, getattr, or try/except)

def get_line_range(node):
    """Get line range for a node."""
    return (getattr(node, 'lineno', 0), getattr(node, 'end_lineno', 0))

def find_encoder_only_accesses(node):
    """Find all direct encoder_only attribute accesses."""
    accesses = []
    for child in ast.walk(node):
        if isinstance(child, ast.Attribute) and child.attr == "encoder_only":
            # Check this is actually accessing the attribute (not getattr/hasattr call)
            accesses.append(child)
    return accesses

def is_inside_hasattr_guard(access_node, func_node):
    """Check if access is inside a hasattr(server_args, 'encoder_only') check."""
    access_line = getattr(access_node, 'lineno', 0)

    for node in ast.walk(func_node):
        if isinstance(node, ast.If):
            # Check if the if test contains hasattr with encoder_only
            has_hasattr = False
            for sub in ast.walk(node.test):
                if isinstance(sub, ast.Call):
                    func = sub.func
                    if isinstance(func, ast.Name) and func.id == "hasattr":
                        for arg in sub.args:
                            if isinstance(arg, ast.Constant) and arg.value == "encoder_only":
                                has_hasattr = True
                                break

            if has_hasattr:
                # Check if access is inside this if block
                if_body_lines = []
                for stmt in node.body:
                    if_body_lines.extend(range(getattr(stmt, 'lineno', 0), getattr(stmt, 'end_lineno', 0) + 1))

                if access_line in if_body_lines:
                    return True

    return False

def uses_getattr_for_encoder_only(func_node):
    """Check if getattr is used to access encoder_only safely."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "getattr":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "encoder_only":
                        return True
                    # Also check second arg position
                    if len(node.args) >= 2:
                        arg2 = node.args[1]
                        if isinstance(arg2, ast.Constant) and arg2.value == "encoder_only":
                            return True
    return False

def uses_try_except_for_encoder_only(func_node):
    """Check if try/except AttributeError pattern is used for encoder_only."""
    for node in ast.walk(func_node):
        if isinstance(node, ast.Try):
            # Check if it catches AttributeError
            catches_attribute_error = False
            for handler in node.handlers:
                if handler.type and isinstance(handler.type, ast.Name):
                    if handler.type.id == "AttributeError":
                        catches_attribute_error = True
                        break

            if catches_attribute_error:
                # Check if encoder_only is accessed inside the try block
                for stmt in node.body:
                    for sub in ast.walk(stmt):
                        if isinstance(sub, ast.Attribute) and sub.attr == "encoder_only":
                            return True
    return False

# Find all accesses to encoder_only
encoder_accesses = find_encoder_only_accesses(func_node)

if not encoder_accesses:
    # No direct access - maybe using getattr entirely, which is fine
    if uses_getattr_for_encoder_only(func_node):
        print("F2P_PASS: no direct encoder_only access, uses getattr pattern")
        sys.exit(0)
    else:
        print("F2P_FAIL: encoder_only reference not found in function")
        sys.exit(1)

# Check each access is properly guarded
unguarded_accesses = []
for access in encoder_accesses:
    if is_inside_hasattr_guard(access, func_node):
        continue
    if uses_getattr_for_encoder_only(func_node):
        # If using getattr, the direct access might be in the true branch after a hasattr check
        continue
    if uses_try_except_for_encoder_only(func_node):
        continue
    unguarded_accesses.append(getattr(access, 'lineno', '?'))

if unguarded_accesses:
    # Check if it's just the original buggy pattern
    if len(unguarded_accesses) == 1:
        print(f"F2P_FAIL: unguarded encoder_only access at line {unguarded_accesses[0]} - AttributeError will occur")
    else:
        print(f"F2P_FAIL: unguarded encoder_only accesses at lines {unguarded_accesses} - AttributeError will occur")
    sys.exit(1)

# Better: verify there's a hasattr/getattr guard
if not uses_getattr_for_encoder_only(func_node):
    # Check for hasattr pattern
    has_hasattr_guard = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "hasattr":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and arg.value == "encoder_only":
                        has_hasattr_guard = True
                        break

    if not has_hasattr_guard and not uses_try_except_for_encoder_only(func_node):
        # Verify we have SOME guard pattern
        print("F2P_FAIL: no hasattr, getattr, or try/except guard found for encoder_only")
        sys.exit(1)

print("F2P_PASS: encoder_only access is properly guarded against AttributeError")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[f2p_crash]=1; fi

# ---------- PRIMARY 2 (30%): Branch correctness - encoder_only=True still works ----------
# [pr_diff] (0.30): When encoder_only=True, should use encode_server import path
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find launch_server_process
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("F2P_BRANCH_FAIL: function not found")
    sys.exit(1)

# Verify both import paths exist (encode_server and http_server)
has_encode_path = False
has_http_path = False

for node in ast.walk(func_node):
    if isinstance(node, ast.ImportFrom) and node.module:
        if "encode_server" in node.module:
            has_encode_path = True
        if "http_server" in node.module:
            has_http_path = True

if not has_encode_path:
    print("F2P_BRANCH_FAIL: encode_server import path not found")
    sys.exit(1)

if not has_http_path:
    print("F2P_BRANCH_FAIL: http_server import path not found")
    sys.exit(1)

# Check that there's an if-statement branching between them based on encoder_only
has_encoder_branching = False

for node in ast.walk(func_node):
    if isinstance(node, ast.If):
        # Check if test references encoder_only
        has_encoder_ref = False
        for sub in ast.walk(node.test):
            if isinstance(sub, ast.Attribute) and sub.attr == "encoder_only":
                has_encoder_ref = True
                break
            if isinstance(sub, ast.Call):
                func = sub.func
                if isinstance(func, ast.Name) and func.id in ("hasattr", "getattr"):
                    for arg in sub.args:
                        if isinstance(arg, ast.Constant) and arg.value == "encoder_only":
                            has_encoder_ref = True
                            break

        if has_encoder_ref:
            # Check that body and orelse contain the different import paths
            body_has_encode = False
            body_has_http = False
            orelse_has_encode = False
            orelse_has_http = False

            for sub in ast.walk(node):
                if isinstance(sub, ast.ImportFrom) and sub.module:
                    if "encode_server" in sub.module:
                        if sub in [n for n in ast.walk(node) if n in node.body]:
                            body_has_encode = True
                    if "http_server" in sub.module:
                        if sub in [n for n in ast.walk(node) if n in node.body]:
                            body_has_http = True

            for sub in node.orelse:
                for subsub in ast.walk(sub):
                    if isinstance(subsub, ast.ImportFrom) and subsub.module:
                        if "encode_server" in subsub.module:
                            orelse_has_encode = True
                        if "http_server" in subsub.module:
                            orelse_has_http = True

            # One branch should have encode, the other http
            if (body_has_encode and orelse_has_http) or (body_has_http and orelse_has_encode):
                has_encoder_branching = True
                break

            # Also pass if there's at least an if/else with encoder_only reference
            # and both paths exist somewhere in function
            if has_encoder_ref and len(node.orelse) > 0:
                has_encoder_branching = True
                break

if not has_encoder_branching:
    print("F2P_BRANCH_FAIL: encoder_only-based branching between import paths not found")
    sys.exit(1)

print("F2P_BRANCH_PASS: encoder_only conditional correctly routes import paths")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[f2p_branch]=1; fi

# ---------- PASS-TO-PASS (20%): Existing behavior preserved - no regressions ----------
# [pr_diff] (0.20): Verify existing code structure is preserved
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/slime/slime/backends/sglang_utils/sglang_engine.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find launch_server_process
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "launch_server_process":
        func_node = node
        break

if func_node is None:
    print("P2P_FAIL: launch_server_process not found")
    sys.exit(1)

# Check function signature preserved
if len(func_node.args.args) < 1:
    print("P2P_FAIL: function should take server_args parameter")
    sys.exit(1)

# Check that multiprocessing is used
has_multiprocessing = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Attribute) and node.attr == "Process":
        has_multiprocessing = True
        break
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "Process":
            has_multiprocessing = True
            break

if not has_multiprocessing:
    print("P2P_FAIL: multiprocessing.Process usage not found")
    sys.exit(1)

# Check that launch_server is called
has_launch_call = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == "launch_server":
            has_launch_call = True
            break
        if isinstance(func, ast.Attribute) and func.attr == "launch_server":
            has_launch_call = True
            break

if not has_launch_call:
    print("P2P_FAIL: launch_server call not found")
    sys.exit(1)

# Check p.start() is called
has_start = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "start":
            has_start = True
            break

if not has_start:
    print("P2P_FAIL: process start() not found")
    sys.exit(1)

print("P2P_PASS: existing function structure preserved")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[p2p_existing]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# [agent_config] (0.05): No wildcard imports - SKILL.md requirements
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# [agent_config] (0.05): No bare print() - SKILL.md requirements
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
python3 -c "
w = {'f2p_crash': ${WEIGHTS[f2p_crash]}, 'f2p_branch': ${WEIGHTS[f2p_branch]}, 'p2p_existing': ${WEIGHTS[p2p_existing]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'f2p_crash': ${RESULTS[f2p_crash]}, 'f2p_branch': ${RESULTS[f2p_branch]}, 'p2p_existing': ${RESULTS[p2p_existing]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in f2p_crash f2p_branch p2p_existing config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
