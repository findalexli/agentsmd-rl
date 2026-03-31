#!/usr/bin/env bash
#
# Verification for sglang-lazy-import-kda-kernel
#
# Tests that CuteDSLKDAKernel is NOT imported at the top level of
# kda_backend.py, preventing AMD/ROCm crash at import time.
#
# Weights:
#   Behavioral (fail-to-pass):  Import test on non-CUDA (0.40)
#   Pass-to-pass (regression):  Existing functionality preserved (0.25)
#   Structural (supplementary): Anti-stub + lazy pattern (0.25)
#   Config-derived:             Main guard for new tests (0.10)
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
# Test 1 [0.40]: FAIL-TO-PASS — kda_backend imports without crashing
#   The buggy code imports CuteDSLKDAKernel at top level, which chains to
#   cuda.bindings.driver and crashes on non-CUDA platforms.
#   This test runs in a clean subprocess to verify the import works.
###############################################################################

echo ""
echo "=== Test 1/4 [0.40]: FAIL-TO-PASS — kda_backend imports without crash ==="

# Run import test in subprocess to isolate any crash
python3 << 'PYEOF'
import subprocess
import sys

# Test: Can we import kda_backend without ModuleNotFoundError?
# On CPU-only systems, the buggy code crashes with:
#   ModuleNotFoundError: No module named 'cuda'

result = subprocess.run(
    [
        sys.executable,
        "-c",
        """
import sys
sys.path.insert(0, '/workspace/sglang/python')
try:
    from sglang.srt.layers.attention.linear import kda_backend
    print('PASS: kda_backend imported successfully')
except ModuleNotFoundError as e:
    if 'cuda' in str(e).lower() or 'kda_cutedsl' in str(e).lower():
        print(f'FAIL: CUDA-related import error: {e}')
        sys.exit(1)
    else:
        # Some other unrelated import error, re-raise to investigate
        raise
except ImportError as e:
    # Check if it's the specific top-level CUDA import crash
    if 'cuda' in str(e).lower():
        print(f'FAIL: CUDA import error: {e}')
        sys.exit(1)
    # Other ImportErrors might be expected (missing deps we can't install)
    # but the specific 'no module named cuda' must NOT happen
    print(f'PASS: Import succeeded (other deps ok): {e}')
"""
    ],
    capture_output=True,
    text=True,
    timeout=30
)

print(result.stdout, end='')
if result.returncode != 0:
    print(result.stderr, end='')
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    SCORE=$(python3 -c "print($SCORE + 0.40)")
    IMPORT_PASSED=1
else
    IMPORT_PASSED=0
fi

###############################################################################
# Test 2 [0.25]: PASS-TO-PASS — CuteDSLKDAKernel functionality preserved
#   The import must still exist (for CUDA users) and the class must be
#   accessible when actually needed.
###############################################################################

echo ""
echo "=== Test 2/4 [0.25]: PASS-TO-PASS — CuteDSLKDAKernel accessible when needed ==="

python3 << 'PYEOF'
import ast
import sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check that CuteDSLKDAKernel is still referenced (not deleted)
found_reference = False
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and node.id == "CuteDSLKDAKernel":
        found_reference = True
        break
    if isinstance(node, ast.Attribute) and node.attr == "CuteDSLKDAKernel":
        found_reference = True
        break

if not found_reference:
    print("FAIL: CuteDSLKDAKernel not referenced anywhere (was deleted)")
    sys.exit(1)

# Check that TritonKDAKernel is still imported at top level
# (regression: ensure we didn't break the triton backend)
found_triton_toplevel = False
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "TritonKDAKernel":
                found_triton_toplevel = True
                break

if not found_triton_toplevel:
    print("FAIL: TritonKDAKernel top-level import missing (regression)")
    sys.exit(1)

# Verify the file has the KDAKernelDispatcher class (main functionality)
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
if "KDAKernelDispatcher" not in classes:
    print("FAIL: KDAKernelDispatcher class missing")
    sys.exit(1)

# Verify decode_kernel attribute is assigned somewhere (key functionality)
found_decode_kernel = False
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr == "decode_kernel":
        found_decode_kernel = True
        break

if not found_decode_kernel:
    print("FAIL: decode_kernel not found in class")
    sys.exit(1)

print("PASS: CuteDSLKDAKernel referenced, TritonKDAKernel at top level, dispatcher intact")
PYEOF

if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi

###############################################################################
# Test 3 [0.25]: Structural — lazy import pattern validated
#   Gate: Only run if Test 1 passed (import works)
###############################################################################

echo ""
echo "=== Test 3/4 [0.25]: Structural — lazy import pattern ==="

if [ "$IMPORT_PASSED" -ne 1 ]; then
    echo "SKIPPED: Import test failed, skip structural checks"
else
    python3 << 'PYEOF'
import ast
import sys

with open("/workspace/sglang/python/sglang/srt/layers/attention/linear/kda_backend.py") as f:
    source = f.read()

tree = ast.parse(source)

# Check: CuteDSLKDAKernel import is NOT at module level
found_toplevel_cutedsl = False
toplevel_lines = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name == "CuteDSLKDAKernel":
                found_toplevel_cutedsl = True
                toplevel_lines.append(node.lineno)

if found_toplevel_cutedsl:
    print(f"FAIL: CuteDSLKDAKernel imported at top level (lines: {toplevel_lines})")
    sys.exit(1)

# Check: CuteDSLKDAKernel import IS inside a function/method
# AND verify it's from the correct module
found_nested_import = False
import_from_correct_module = False

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.ImportFrom):
                for alias in subnode.names:
                    if alias.name == "CuteDSLKDAKernel":
                        found_nested_import = True
                        # Verify import source module
                        if subnode.module and "kda_cutedsl" in subnode.module:
                            import_from_correct_module = True
                        elif subnode.module and "sglang" in subnode.module:
                            # Accept any sglang module path (handles refactoring)
                            import_from_correct_module = True

if not found_nested_import:
    print("WARNING: CuteDSLKDAKernel import not found inside function")
    # Allow top-level conditional import as alternative valid pattern
    # Check for module-level conditional import
    found_conditional_toplevel = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.If):
            # Check if body contains the import
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.ImportFrom):
                    if subnode.module and "kda_cutedsl" in subnode.module:
                        for alias in subnode.names:
                            if alias.name == "CuteDSLKDAKernel":
                                found_conditional_toplevel = True
    if found_conditional_toplevel:
        print("INFO: Found conditional top-level import (valid alternative)")
        import_from_correct_module = True
    else:
        print("FAIL: CuteDSLKDAKernel import not found in valid location")
        sys.exit(1)

if not import_from_correct_module:
    print("FAIL: CuteDSLKDAKernel not imported from valid kda_cutedsl module")
    sys.exit(1)

# File must have reasonable content (anti-stub)
if len(source.splitlines()) < 30:
    print(f"FAIL: file too short ({len(source.splitlines())} lines, need >=30)")
    sys.exit(1)

# Must have class definition
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
if not classes:
    print("FAIL: no class definitions found (stub detected)")
    sys.exit(1)

# Required identifiers must be present
required = ["TritonKDAKernel", "CuteDSLKDAKernel", "decode_kernel",
            "is_cuda", "is_cutedsl"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing identifiers: {missing}")
    sys.exit(1)

print(f"PASS: lazy import validated, {len(source.splitlines())} lines, classes: {classes}")
PYEOF

    if [ $? -eq 0 ]; then SCORE=$(python3 -c "print($SCORE + 0.25)"); fi
fi

###############################################################################
# Test 4 [0.10]: Config-derived — new test files have main guard
###############################################################################

echo ""
echo "=== Test 4/4 [0.10]: Config-derived — new test files have main guard ==="

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
