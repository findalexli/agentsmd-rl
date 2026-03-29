#!/usr/bin/env bash
# Verifier for vllm-triton-cache-autotuning
# Task: add os.environ.setdefault("TRITON_CACHE_AUTOTUNING", "1") to vllm/env_override.py

set +e

PASS=0
TOTAL=5
REPO=/workspace/vllm
TARGET="$REPO/vllm/env_override.py"

mkdir -p /logs/verifier

echo "=== vllm triton cache autotuning verifier ==="

# ── GATE: Python syntax validity (non-scoring) ───────────────────────────
echo ""
echo "GATE: Python syntax validity of vllm/env_override.py"
python3 << 'PYEOF'
import ast, sys
try:
    ast.parse(open("/workspace/vllm/vllm/env_override.py").read())
    print("  OK: syntax valid")
    sys.exit(0)
except SyntaxError as e:
    print("  FAIL:", str(e))
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file — aborting with score 0"
    echo "0.0000" > /logs/verifier/reward.txt
    exit 0
fi
echo "GATE PASS"

# ── TEST 1: file contains TRITON_CACHE_AUTOTUNING string ─────────────────
echo ""
echo "TEST 1: file contains TRITON_CACHE_AUTOTUNING string"
python3 << 'PYEOF'
import sys
src = open("/workspace/vllm/vllm/env_override.py").read()
if "TRITON_CACHE_AUTOTUNING" in src:
    print("  OK: TRITON_CACHE_AUTOTUNING found")
    sys.exit(0)
else:
    print("  FAIL: TRITON_CACHE_AUTOTUNING not found in file")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then echo "PASS"; PASS=$((PASS + 1)); else echo "FAIL"; fi

# ── TEST 2: uses os.environ.setdefault (not direct assignment) ────────────
echo ""
echo "TEST 2: uses os.environ.setdefault for TRITON_CACHE_AUTOTUNING"
python3 << 'PYEOF'
import ast, sys

src = open("/workspace/vllm/vllm/env_override.py").read()
tree = ast.parse(src)

found_setdefault = False
for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    # Match os.environ.setdefault(...)
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "setdefault":
        # Check the first arg is "TRITON_CACHE_AUTOTUNING"
        if node.args and isinstance(node.args[0], ast.Constant):
            if node.args[0].value == "TRITON_CACHE_AUTOTUNING":
                found_setdefault = True
                break

if found_setdefault:
    print("  OK: os.environ.setdefault('TRITON_CACHE_AUTOTUNING', ...) found")
    sys.exit(0)
else:
    print("  FAIL: no setdefault call with TRITON_CACHE_AUTOTUNING")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then echo "PASS"; PASS=$((PASS + 1)); else echo "FAIL"; fi

# ── TEST 3: value is set to "1" (enabled) ────────────────────────────────
echo ""
echo "TEST 3: TRITON_CACHE_AUTOTUNING default value is '1'"
python3 << 'PYEOF'
import ast, sys

src = open("/workspace/vllm/vllm/env_override.py").read()
tree = ast.parse(src)

found_correct_value = False
for node in ast.walk(tree):
    if not isinstance(node, ast.Call):
        continue
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr == "setdefault":
        if node.args and isinstance(node.args[0], ast.Constant):
            if node.args[0].value == "TRITON_CACHE_AUTOTUNING":
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                    if node.args[1].value == "1":
                        found_correct_value = True
                        break

if found_correct_value:
    print("  OK: value is '1'")
    sys.exit(0)
else:
    print("  FAIL: value is not '1'")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then echo "PASS"; PASS=$((PASS + 1)); else echo "FAIL"; fi

# ── TEST 4: behavioral — importing the module sets the env var ────────────
echo ""
echo "TEST 4: behavioral — importing env_override sets TRITON_CACHE_AUTOTUNING in os.environ"
python3 << 'PYEOF'
import os, sys

# Make sure the var is NOT set before exec
os.environ.pop("TRITON_CACHE_AUTOTUNING", None)

# env_override.py imports torch at module level which isn't installed.
# Instead of importing the whole module, exec just the lines we care about
# in an isolated namespace with a minimal mock.
src = open("/workspace/vllm/vllm/env_override.py").read()

# Extract only lines that don't require torch/heavy imports:
# run each top-level os.environ.setdefault line
import ast
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        call = node.value
        func = call.func
        if (isinstance(func, ast.Attribute) and func.attr == "setdefault"
            and isinstance(func.value, ast.Attribute) and func.value.attr == "environ"):
            seg = ast.get_source_segment(src, node)
            if seg and "TRITON_CACHE_AUTOTUNING" in seg:
                exec(seg)
                break

val = os.environ.get("TRITON_CACHE_AUTOTUNING")
if val == "1":
    print("  OK: TRITON_CACHE_AUTOTUNING='1' after exec of setdefault line")
    sys.exit(0)
elif val is not None:
    print("  PARTIAL: TRITON_CACHE_AUTOTUNING set but value is", repr(val), "not '1'")
    sys.exit(1)
else:
    print("  FAIL: TRITON_CACHE_AUTOTUNING not set")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then echo "PASS"; PASS=$((PASS + 1)); else echo "FAIL"; fi

# ── TEST 5: anti-stub — file still contains original env_override logic ───
echo ""
echo "TEST 5: anti-stub — file retains original env_override content"
python3 << 'PYEOF'
import sys

src = open("/workspace/vllm/vllm/env_override.py").read()

# Check for known env vars that should already exist in the file
# env_override.py sets various environment variable defaults for vllm
known_markers = 0
markers = [
    "os.environ",
    "setdefault",
]
for m in markers:
    if m in src:
        known_markers += 1

# File should have reasonable length (not a stub)
lines = len(src.strip().splitlines())
if lines < 5:
    print("  FAIL: file too short ({} lines) — likely a stub".format(lines))
    sys.exit(1)

if known_markers < 2:
    print("  FAIL: missing expected content (found {}/{} markers)".format(known_markers, len(markers)))
    sys.exit(1)

print("  OK: file has {} lines and {}/{} expected markers".format(lines, known_markers, len(markers)))
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then echo "PASS"; PASS=$((PASS + 1)); else echo "FAIL"; fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "=== Results: $PASS/$TOTAL ==="

REWARD=$(python3 -c "print('{:.4f}'.format(min($PASS/float($TOTAL), 1.0)))")
echo "Reward: $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt
