#!/usr/bin/env bash
set +e

TARGET="/workspace/gradio/gradio/utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[regression]=0.25
WEIGHTS[structural]=0.20
WEIGHTS[antistub]=0.15

WEIGHTS[config_ruff_format]=0.05

for key in behavioral regression structural antistub config_ruff_format; do
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

# ---------- PRIMARY 1 (35%): Behavioral - SpacesReloader.swap_blocks calls get_config_file ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find SpacesReloader class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("BEHAVIORAL FAIL: SpacesReloader class not found")
    sys.exit(1)

# Find swap_blocks method in SpacesReloader
swap_blocks_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "swap_blocks":
        swap_blocks_node = item
        break

if swap_blocks_node is None:
    # The fix requires adding swap_blocks override - check if postrun calls get_config_file
    postrun_node = None
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "postrun":
            postrun_node = item
            break

    if postrun_node is not None:
        postrun_src = ast.get_source_segment(source, postrun_node) or ""
        if "get_config_file" in postrun_src:
            print("BEHAVIORAL PASS: get_config_file called in postrun (alternative fix)")
            sys.exit(0)

    print("BEHAVIORAL FAIL: SpacesReloader has no swap_blocks override and postrun does not call get_config_file")
    sys.exit(1)

# Check that swap_blocks calls get_config_file
swap_src = ast.get_source_segment(source, swap_blocks_node)
if swap_src is None:
    lines = source.splitlines()
    swap_src = "\n".join(lines[swap_blocks_node.lineno - 1 : swap_blocks_node.end_lineno])

if "get_config_file" in swap_src:
    print("BEHAVIORAL PASS: SpacesReloader.swap_blocks calls get_config_file")
    sys.exit(0)
else:
    print("BEHAVIORAL FAIL: swap_blocks does not call get_config_file")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Regression - SpacesReloader.swap_blocks calls super ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("REGRESSION FAIL: SpacesReloader class not found")
    sys.exit(1)

swap_blocks_node = None
for item in cls_node.body:
    if isinstance(item, ast.FunctionDef) and item.name == "swap_blocks":
        swap_blocks_node = item
        break

if swap_blocks_node is None:
    # If no swap_blocks, check postrun still calls swap_blocks
    postrun_node = None
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "postrun":
            postrun_node = item
            break
    if postrun_node:
        postrun_src = ast.get_source_segment(source, postrun_node) or ""
        if "swap_blocks" in postrun_src:
            print("REGRESSION PASS: postrun still calls swap_blocks")
            sys.exit(0)
    print("REGRESSION FAIL: no swap_blocks override")
    sys.exit(1)

swap_src = ast.get_source_segment(source, swap_blocks_node)
if swap_src is None:
    lines = source.splitlines()
    swap_src = "\n".join(lines[swap_blocks_node.lineno - 1 : swap_blocks_node.end_lineno])

if "super()" in swap_src or "super(" in swap_src:
    print("REGRESSION PASS: swap_blocks calls super()")
    sys.exit(0)
else:
    print("REGRESSION FAIL: swap_blocks does not call super()")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - postrun TODO comments removed ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SpacesReloader":
        cls_node = node
        break

if cls_node is None:
    print("STRUCTURAL FAIL: SpacesReloader class not found")
    sys.exit(1)

# Get full class source
cls_src = ast.get_source_segment(source, cls_node)
if cls_src is None:
    lines = source.splitlines()
    cls_src = "\n".join(lines[cls_node.lineno - 1 : cls_node.end_lineno])

# Check that the TODO comments about re-assign config are removed
if "TODO: re-assign config" in cls_src:
    print("STRUCTURAL FAIL: TODO comment about re-assign config still present")
    sys.exit(1)
else:
    print("STRUCTURAL PASS: TODO comments cleaned up")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[structural]=1
    echo "TEST structural: PASS"
else
    echo "TEST structural: FAIL"
fi

# ---------- Anti-stub check (20%) ----------
python3 << 'PYEOF'
import sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

checks = [
    ("class SpacesReloader" in source, "SpacesReloader class present"),
    ("class SourceFileReloader" in source, "SourceFileReloader class present"),
    ("def postrun" in source, "postrun method present"),
    ("swap_blocks" in source, "swap_blocks referenced"),
    (len(source.splitlines()) > 100, "file has substantial content"),
]

failures = [desc for ok, desc in checks if not ok]

if failures:
    print(f"ANTI-STUB FAIL: missing: {', '.join(failures)}")
    sys.exit(1)

print("ANTI-STUB PASS: file retains full implementation")
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[antistub]=1
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit 34ee825ae7111488655e68f983e45d55673455a2
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/utils.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then
    RESULTS[config_ruff_format]=1
    echo "TEST config_ruff_format: PASS"
else
    echo "TEST config_ruff_format: FAIL"
fi

# ---------- Final weighted score ----------
SCORE=$(python3 -c "
weights = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]}, 'structural': ${WEIGHTS[structural]}, 'antistub': ${WEIGHTS[antistub]}, 'config_ruff_format': ${WEIGHTS[config_ruff_format]}}
results = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]}, 'structural': ${RESULTS[structural]}, 'antistub': ${RESULTS[antistub]}, 'config_ruff_format': ${RESULTS[config_ruff_format]}}
score = sum(weights[k] * results[k] for k in weights)
print(f'{score:.2f}')
")
echo ""
echo "=== FINAL SCORE ==="
echo "  behavioral (${WEIGHTS[behavioral]}): ${RESULTS[behavioral]}"
echo "  regression (${WEIGHTS[regression]}): ${RESULTS[regression]}"
echo "  structural (${WEIGHTS[structural]}): ${RESULTS[structural]}"
echo "  antistub   (${WEIGHTS[antistub]}): ${RESULTS[antistub]}"
echo "  config_ruff_format (${WEIGHTS[config_ruff_format]}): ${RESULTS[config_ruff_format]}"
echo "  TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
