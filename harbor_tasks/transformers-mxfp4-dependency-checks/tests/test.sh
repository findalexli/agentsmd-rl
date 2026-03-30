#!/usr/bin/env bash
# Verifier for transformers-mxfp4-dependency-checks
# Bug: combined kernels_available boolean prevents identifying which dependency is missing
# File: src/transformers/quantizers/quantizer_mxfp4.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py"

echo "=== transformers-mxfp4-dependency-checks verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAV_SEPARATE_VARS=0.19
W_BEHAV_TRITON_WARNING=0.14
W_BEHAV_KERNELS_WARNING=0.14
W_BEHAV_TRITON_ERROR=0.14
W_BEHAV_KERNELS_ERROR=0.14
W_PASSTOPASS=0.10
W_ANTISTUB=0.10
W_CONFIG_RUFF=0.05

SCORE="0.0"

# ── TEST 1 (PRIMARY): behavioral — separate triton/kernels variables ──
echo ""
echo "TEST 1: behavioral — triton and kernels checked separately (weight=$W_BEHAV_SEPARATE_VARS)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find validate_environment method
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[item.lineno - 1:item.end_lineno])

                # The buggy code combines them: kernels_available = is_triton_available(...) and is_kernels_available()
                # The fix should have separate variables
                if "kernels_available = is_triton_available" in func_src:
                    print("FAIL: still using combined kernels_available variable (the bug)")
                    sys.exit(1)

                # Check for separate variables
                has_triton_var = ("triton_available" in func_src or "triton_ok" in func_src)
                has_kernels_var = ("kernels_installed" in func_src or "kernels_available" in func_src)

                # Make sure they are separate assignments
                assigns = []
                for subnode in ast.walk(item):
                    if isinstance(subnode, ast.Assign):
                        for target in subnode.targets:
                            if isinstance(target, ast.Name):
                                assigns.append(target.id)

                triton_assign = any("triton" in a.lower() for a in assigns)
                kernels_assign = any("kernel" in a.lower() for a in assigns)

                if triton_assign and kernels_assign:
                    print("PASS: triton and kernels have separate variable assignments")
                    sys.exit(0)
                elif has_triton_var and has_kernels_var:
                    print("PASS: separate triton and kernels variables found")
                    sys.exit(0)
                else:
                    print(f"FAIL: could not find separate variables (assigns={assigns})")
                    sys.exit(1)

print("FAIL: validate_environment method not found")
sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_SEPARATE_VARS)")
fi

# ── TEST 2 (PRIMARY): behavioral — triton-specific warning when pre_quantized ──
echo ""
echo "TEST 2: behavioral — triton-specific warning for pre_quantized (weight=$W_BEHAV_TRITON_WARNING)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[item.lineno - 1:item.end_lineno])

                # Find warning_once calls that are specifically about triton (not combined)
                # Look for a condition checking triton AND a warning mentioning triton specifically
                # The fix should have: if not triton_available: logger.warning_once("...triton...")
                # separate from: if not kernels_installed: logger.warning_once("...kernels...")

                # Count warning_once calls that mention dependency-specific text
                warning_sections = func_src.split("warning_once")

                triton_specific_warning = False
                for section in warning_sections[1:]:  # skip first split before any warning_once
                    # Check within next ~200 chars
                    snippet = section[:300].lower()
                    # Must mention triton but NOT be a combined "triton and kernels" message
                    if "triton" in snippet and "triton and kernels" not in snippet:
                        triton_specific_warning = True
                        break

                if triton_specific_warning:
                    print("PASS: triton-specific warning found (not combined with kernels)")
                    sys.exit(0)
                else:
                    print("FAIL: no triton-specific warning found")
                    sys.exit(1)

print("FAIL: validate_environment not found")
sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TRITON_WARNING)")
fi

# ── TEST 3 (PRIMARY): behavioral — kernels-specific warning when pre_quantized ──
echo ""
echo "TEST 3: behavioral — kernels-specific warning for pre_quantized (weight=$W_BEHAV_KERNELS_WARNING)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[item.lineno - 1:item.end_lineno])

                warning_sections = func_src.split("warning_once")

                kernels_specific_warning = False
                for section in warning_sections[1:]:
                    snippet = section[:300].lower()
                    if "kernels" in snippet and "triton and kernels" not in snippet:
                        kernels_specific_warning = True
                        break

                if kernels_specific_warning:
                    print("PASS: kernels-specific warning found (not combined with triton)")
                    sys.exit(0)
                else:
                    print("FAIL: no kernels-specific warning found")
                    sys.exit(1)

print("FAIL: validate_environment not found")
sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_KERNELS_WARNING)")
fi

# ── TEST 4 (PRIMARY): behavioral — triton-specific ValueError when not pre_quantized ──
echo ""
echo "TEST 4: behavioral — triton-specific ValueError (weight=$W_BEHAV_TRITON_ERROR)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[item.lineno - 1:item.end_lineno])

                # Find ValueError raises
                raise_sections = func_src.split("raise ValueError")

                triton_specific_error = False
                for section in raise_sections[1:]:
                    snippet = section[:300].lower()
                    if "triton" in snippet and "triton and kernels" not in snippet:
                        triton_specific_error = True
                        break

                if triton_specific_error:
                    print("PASS: triton-specific ValueError found")
                    sys.exit(0)
                else:
                    print("FAIL: no triton-specific ValueError found")
                    sys.exit(1)

print("FAIL: validate_environment not found")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TRITON_ERROR)")
fi

# ── TEST 5 (PRIMARY): behavioral — kernels-specific ValueError when not pre_quantized ──
echo ""
echo "TEST 5: behavioral — kernels-specific ValueError (weight=$W_BEHAV_KERNELS_ERROR)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[item.lineno - 1:item.end_lineno])

                raise_sections = func_src.split("raise ValueError")

                kernels_specific_error = False
                for section in raise_sections[1:]:
                    snippet = section[:300].lower()
                    if "kernels" in snippet and "triton and kernels" not in snippet:
                        kernels_specific_error = True
                        break

                if kernels_specific_error:
                    print("PASS: kernels-specific ValueError found")
                    sys.exit(0)
                else:
                    print("FAIL: no kernels-specific ValueError found")
                    sys.exit(1)

print("FAIL: validate_environment not found")
sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_KERNELS_ERROR)")
fi

# ── TEST 6: pass-to-pass — validate_environment structure intact ──
echo ""
echo "TEST 6: pass-to-pass — validate_environment structure intact (weight=$W_PASSTOPASS)"
T6=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "Mxfp4" in node.name:
        method_names = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
        if "validate_environment" not in method_names:
            print("FAIL: validate_environment missing")
            sys.exit(1)

        for m in node.body:
            if isinstance(m, ast.FunctionDef) and m.name == "validate_environment":
                lines = source.splitlines()
                func_src = "\n".join(lines[m.lineno - 1:m.end_lineno])
                # Check key elements still present
                required = ["is_device_supported_mxfp4", "pre_quantized", "dequantize",
                           "is_triton_available", "is_kernels_available"]
                missing = [r for r in required if r not in func_src]
                if missing:
                    print(f"FAIL: missing elements: {missing}")
                    sys.exit(1)
                print("PASS: validate_environment structure intact")
                sys.exit(0)

print("FAIL: Mxfp4 quantizer class not found")
sys.exit(1)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 7: anti-stub ──
echo ""
echo "TEST 7: anti-stub — file retains original logic (weight=$W_ANTISTUB)"
T7=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py") as f:
    source = f.read()

required = ["Mxfp4HfQuantizer", "validate_environment", "is_triton_available",
            "is_kernels_available", "HfQuantizer", "quantization_config"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 80:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# -- CONFIG-DERIVED: ruff format check on changed files (weight=$W_CONFIG_RUFF) --
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit a8732d5546d84bfb4519b6dbf461c947a5de45f6
echo ""
echo "CONFIG: ruff format check (weight=$W_CONFIG_RUFF)"
T_RUFF=$(python3 << 'PYRUFF'
import subprocess, sys
files = ['/workspace/transformers/src/transformers/quantizers/quantizer_mxfp4.py']
all_ok = True
for f in files:
    result = subprocess.run(["ruff", "check", "--select", "I", f], capture_output=True, text=True)
    if result.returncode != 0:
        all_ok = False
        print(f"FAIL: ruff check failed on {f}")
if all_ok:
    print("PASS: all changed files pass ruff import sort check")
    sys.exit(0)
else:
    sys.exit(1)
PYRUFF
)
echo "$T_RUFF"
if echo "$T_RUFF" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_RUFF)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
