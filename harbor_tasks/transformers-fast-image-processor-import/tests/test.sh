#!/usr/bin/env bash
# Verifier for transformers-fast-image-processor-import
# Bug: importing fast image processor modules via full path fails with ModuleNotFoundError
# Files: __init__.py, check_repo.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

echo "=== transformers-fast-image-processor-import verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
for path in [
    "/workspace/transformers/src/transformers/__init__.py",
    "/workspace/transformers/utils/check_repo.py",
]:
    try:
        with open(path) as f:
            ast.parse(f.read())
        print(f"  OK: {path} parses successfully")
    except SyntaxError as e:
        print(f"  FAIL: SyntaxError in {path}: {e}")
        sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAV_MODULE_ALIAS=0.23
W_BEHAV_CLASS_REDIRECT=0.24
W_BEHAV_CHECK_REPO=0.14
W_STRUCT_RGLOB=0.14
W_PASSTOPASS=0.10
W_ANTISTUB=0.10
W_CONFIG_RUFF=0.05

SCORE="0.0"

# ── TEST 1 (PRIMARY): behavioral — fast image processor module alias resolves ──
echo ""
echo "TEST 1: behavioral — fast image processor module alias created (weight=$W_BEHAV_MODULE_ALIAS)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    source = f.read()

# The fix should iterate over image_processing_*.py files and create _fast aliases
if "image_processing_" in source and "_fast" in source and ("rglob" in source or "glob" in source):
    if "_create_module_alias" in source:
        lines = source.splitlines()
        found_fast_alias = False
        for i, line in enumerate(lines):
            if "_create_module_alias" in line and "_fast" in line and "models" in line:
                found_fast_alias = True
                break
        if found_fast_alias:
            print("PASS: module alias creation for image_processing_*_fast found")
            sys.exit(0)
        else:
            print("FAIL: _create_module_alias found but no _fast alias for model image processors")
            sys.exit(1)
    else:
        print("FAIL: no _create_module_alias call found")
        sys.exit(1)
else:
    print("FAIL: no glob/rglob pattern for image_processing_*_fast aliases")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MODULE_ALIAS)")
fi

# ── TEST 2 (PRIMARY): behavioral — __getattr__ redirect for Fast class names ──
echo ""
echo "TEST 2: behavioral — __getattr__ redirects Fast class names (weight=$W_BEHAV_CLASS_REDIRECT)"
T2=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    source = f.read()

# The fix should install a __getattr__ on the alias modules that strips "Fast" suffix
if "removesuffix" in source and "Fast" in source and "__getattr__" in source:
    if "getattr_factory" in source or ("__getattr__" in source and "removesuffix" in source):
        print("PASS: __getattr__ with Fast->non-Fast redirect found")
        sys.exit(0)

# Alternative: check for any mechanism that handles Fast suffix removal
lines = source.splitlines()
found_redirect = False
for i, line in enumerate(lines):
    if ("Fast" in line and ("removesuffix" in line or "replace" in line or "[:-4]" in line)):
        found_redirect = True
        break

if found_redirect:
    print("PASS: Fast class name redirect mechanism found")
    sys.exit(0)
else:
    print("FAIL: no Fast->non-Fast class redirect found in __init__.py")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CLASS_REDIRECT)")
fi

# ── TEST 3 (PRIMARY): behavioral — check_repo.py ignores _fast aliases ──
echo ""
echo "TEST 3: behavioral — check_repo.py ignores image_processing_*_fast (weight=$W_BEHAV_CHECK_REPO)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/utils/check_repo.py") as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "ignore_undocumented":
        func_node = node
        break

if func_node is None:
    print("FAIL: ignore_undocumented function not found")
    sys.exit(1)

lines = source.splitlines()
func_src = "\n".join(lines[func_node.lineno - 1:func_node.end_lineno])

if "image_processing_" in func_src and "_fast" in func_src:
    print("PASS: ignore_undocumented handles image_processing_*_fast")
    sys.exit(0)
else:
    print("FAIL: ignore_undocumented does not handle image_processing_*_fast")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_CHECK_REPO)")
fi

# ── TEST 4: structural — rglob pattern or equivalent iteration ──
echo ""
echo "TEST 4: structural — dynamic iteration over image_processing files (weight=$W_STRUCT_RGLOB)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    source = f.read()

if any(pattern in source for pattern in ["rglob(\"image_processing_", "glob(\"image_processing_",
                                           "rglob('image_processing_", "glob('image_processing_"]):
    print("PASS: dynamic file iteration for image_processing aliases found")
    sys.exit(0)

if source.count("image_processing_") > 5 and "_create_module_alias" in source:
    print("PASS: multiple image_processing alias entries found (manual approach)")
    sys.exit(0)

print("FAIL: no dynamic iteration over image_processing files")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCT_RGLOB)")
fi

# ── TEST 5: pass-to-pass — existing aliases still present ──
echo ""
echo "TEST 5: pass-to-pass — existing module aliases preserved (weight=$W_PASSTOPASS)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    source = f.read()

required = [
    "tokenization_utils_fast",
    "tokenization_utils_sentencepiece",
    "image_processing_utils_fast",
    "image_processing_backends",
    "_create_module_alias",
]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing expected content: {missing}")
    sys.exit(1)

print("PASS: existing module aliases preserved")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 6: anti-stub ──
echo ""
echo "TEST 6: anti-stub — files retain original content (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/__init__.py") as f:
    lines = len(f.read().splitlines())
if lines < 500:
    print(f"FAIL: __init__.py too short: {lines} lines")
    sys.exit(1)

with open("/workspace/transformers/utils/check_repo.py") as f:
    source = f.read()
if "ignore_undocumented" not in source:
    print("FAIL: check_repo.py missing ignore_undocumented")
    sys.exit(1)
if len(source.splitlines()) < 500:
    print("FAIL: check_repo.py too short")
    sys.exit(1)

print("PASS: files retain original content")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# -- CONFIG-DERIVED: ruff format check on changed files (weight=$W_CONFIG_RUFF) --
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit 29db503cdef2f00d1f0ecd5841c3a486708ed1dd
echo ""
echo "CONFIG: ruff format check (weight=$W_CONFIG_RUFF)"
T_RUFF=$(python3 << 'PYRUFF'
import subprocess, sys
files = ['/workspace/transformers/src/transformers/__init__.py']
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
