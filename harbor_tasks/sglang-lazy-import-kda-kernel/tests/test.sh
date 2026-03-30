#!/usr/bin/env bash
#
# Verification for sglang-lazy-import-kda-kernel
#
# Tests that CuteDSLKDAKernel is NOT imported at the top level of
# kda_backend.py, and IS imported lazily inside the is_cutedsl() branch.
#
# Weights:
#   Behavioral (fail-to-pass):  Test 1 (0.35) = 0.35
#   Pass-to-pass (regression):  Test 2 (0.25) = 0.25
#   Structural (supplementary): Test 3 (0.20) = 0.20
#   Anti-stub:                  Test 4 (0.10) = 0.10
#   Config-derived:             Test 5 (0.10) = 0.10
#   Total: 1.00
#
set +e

TARGET="/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

SCORE=0

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
# Test 1 (0.35): Behavioral fail-to-pass — no top-level import of CuteDSLKDAKernel
#   The buggy code imports CuteDSLKDAKernel at the top level, which chains to
#   cuda.bindings.driver and crashes on non-CUDA platforms.
#   AST check: CuteDSLKDAKernel must NOT appear in any top-level ImportFrom.
###############################################################################

echo ""
echo "=== Test 1/4 [0.35]: Behavioral — no top-level CuteDSLKDAKernel import ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check top-level imports only (direct children of Module)
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "CuteDSLKDAKernel":
                print(f"FAIL: CuteDSLKDAKernel is imported at top level (line {node.lineno})")
                sys.exit(1)
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if "CuteDSLKDAKernel" in alias.name:
                print(f"FAIL: CuteDSLKDAKernel is imported at top level (line {node.lineno})")
                sys.exit(1)

print("PASS: CuteDSLKDAKernel is NOT imported at top level")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.35)"); fi

###############################################################################
# Test 2 (0.25): Pass-to-pass — CuteDSLKDAKernel import still exists somewhere
#   The import must still exist in the file (just not at the top level).
###############################################################################

echo ""
echo "=== Test 2/4 [0.25]: Pass-to-pass — CuteDSLKDAKernel import still exists ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

if "CuteDSLKDAKernel" not in source:
    print("FAIL: CuteDSLKDAKernel not found anywhere in file")
    sys.exit(1)

# Verify it appears in an import statement somewhere (could be nested)
tree = ast.parse(source)
found_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "CuteDSLKDAKernel":
                found_import = True
                break

if not found_import:
    print("FAIL: no import statement for CuteDSLKDAKernel found")
    sys.exit(1)

# Verify TritonKDAKernel is still imported at top level (not broken)
found_triton = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "TritonKDAKernel":
                found_triton = True
                break

if not found_triton:
    print("FAIL: TritonKDAKernel top-level import missing")
    sys.exit(1)

print("PASS: CuteDSLKDAKernel import exists (lazy), TritonKDAKernel still at top level")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi

###############################################################################
# Test 3 (0.20): Structural — import is inside a function/method body
###############################################################################

echo ""
echo "=== Test 3/5 [0.20]: Structural — import is inside function body ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find CuteDSLKDAKernel import that is NOT a direct child of Module
# (i.e., it must be nested inside a class method or function)
found_nested_import = False
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.ImportFrom):
                for alias in subnode.names:
                    if alias.name == "CuteDSLKDAKernel":
                        found_nested_import = True
                        break

if not found_nested_import:
    print("FAIL: CuteDSLKDAKernel import not found inside any function/method")
    sys.exit(1)

print("PASS: CuteDSLKDAKernel import is inside a function body (lazy)")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.20)"); fi

###############################################################################
# Test 4 (0.10): Anti-stub — file retains full implementation
###############################################################################

echo ""
echo "=== Test 4/5 [0.10]: Anti-stub check ==="
python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Must have a class definition
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
if not classes:
    print("FAIL: no class definitions found")
    sys.exit(1)

# File must have reasonable content
if len(source.splitlines()) < 30:
    print(f"FAIL: file too short ({len(source.splitlines())} lines)")
    sys.exit(1)

# Key identifiers must be present
required = ["TritonKDAKernel", "CuteDSLKDAKernel", "decode_kernel",
            "is_cuda", "is_cutedsl"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing identifiers: {missing}")
    sys.exit(1)

print(f"PASS: file has {len(source.splitlines())} lines, classes: {classes}")
PYEOF
if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.10)"); fi

###############################################################################
# Test 5 (0.10): Config-derived — "Has `if __name__ == '__main__': unittest.main()`"
# Source: .claude/skills/write-sglang-test/SKILL.md lines 8-10 @ 75682f1d2f60797fb438da8fd6fe40e92e1a26fe
###############################################################################

echo ""
echo "=== Test 5/5 [0.10]: Config-derived — new test files have main guard ==="
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
