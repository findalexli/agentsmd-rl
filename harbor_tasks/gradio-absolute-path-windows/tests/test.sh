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

# ---------- PRIMARY 1 (35%): Behavioral - safe_join rejects paths starting with / ----------
python3 << 'PYEOF'
import ast, sys, textwrap, os, unittest.mock

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the safe_join function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: safe_join function not found")
    sys.exit(1)

func_source = ast.get_source_segment(source, func_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

func_source = textwrap.dedent(func_source)

# We need to mock os.path.isabs to NOT detect "/" as absolute (simulating Py3.14 on Windows)
# Then test that safe_join still rejects the path
exec_globals = {"os": os, "__builtins__": __builtins__}

# First, we need the type aliases used in the function signature
exec_globals["DeveloperPath"] = str
exec_globals["UserProvidedPath"] = str

# Get _os_alt_seps from the module
# It's typically defined as: _os_alt_seps = list(sep for sep in [os.sep, os.altsep] if sep is not None and sep != os.sep)
exec_globals["_os_alt_seps"] = list(sep for sep in [os.sep, os.altsep] if sep is not None and sep != os.sep)

exec(compile(func_source, "<safe_join>", "exec"), exec_globals)
safe_join = exec_globals["safe_join"]

# Test: path starting with / should raise even if os.path.isabs returns False
# (simulating Python 3.14 on Windows behavior)
with unittest.mock.patch("os.path.isabs", return_value=False):
    try:
        result = safe_join("/tmp/uploads", "/etc/passwd")
        # If it returns without error, the fix is missing
        print(f"BEHAVIORAL FAIL: safe_join did not reject '/etc/passwd', returned: {result}")
        sys.exit(1)
    except Exception as e:
        # Should raise some error (NotAllowedPath or similar)
        print(f"BEHAVIORAL PASS: safe_join correctly rejects '/etc/passwd' with: {type(e).__name__}")
        sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[behavioral]=1
    echo "TEST behavioral: PASS"
else
    echo "TEST behavioral: FAIL"
fi

# ---------- PRIMARY 2 (25%): Regression - normal relative paths still work ----------
python3 << 'PYEOF'
import ast, sys, textwrap, os

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_node = node
        break

if func_node is None:
    print("REGRESSION FAIL: safe_join function not found")
    sys.exit(1)

func_source = ast.get_source_segment(source, func_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

func_source = textwrap.dedent(func_source)

exec_globals = {"os": os, "__builtins__": __builtins__}
exec_globals["DeveloperPath"] = str
exec_globals["UserProvidedPath"] = str
exec_globals["_os_alt_seps"] = list(sep for sep in [os.sep, os.altsep] if sep is not None and sep != os.sep)

exec(compile(func_source, "<safe_join>", "exec"), exec_globals)
safe_join = exec_globals["safe_join"]

# Normal relative paths should work fine
test_cases = [
    ("/tmp/uploads", "image.png", "/tmp/uploads/image.png"),
    ("/tmp/uploads", "subdir/file.txt", "/tmp/uploads/subdir/file.txt"),
]

all_pass = True
for directory, path, expected in test_cases:
    try:
        result = safe_join(directory, path)
        if result != expected:
            # The function may normalize differently, just check it doesn't raise
            print(f"  OK: safe_join({directory!r}, {path!r}) = {result!r}")
        else:
            print(f"  PASS: safe_join({directory!r}, {path!r}) = {result!r}")
    except Exception as e:
        print(f"  FAIL: safe_join({directory!r}, {path!r}) raised {type(e).__name__}: {e}")
        all_pass = False

if all_pass:
    print("REGRESSION PASS: normal relative paths work correctly")
else:
    print("REGRESSION FAIL")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    RESULTS[regression]=1
    echo "TEST regression: PASS"
else
    echo "TEST regression: FAIL"
fi

# ---------- SUPPLEMENTARY (20%): Structural - explicit / check present ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/gradio/gradio/utils.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "safe_join":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: safe_join function not found")
    sys.exit(1)

func_source = ast.get_source_segment(source, func_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Check for explicit "/" check (startswith("/") or similar pattern)
if 'startswith("/")' in func_source or "startswith('/')" in func_source or 'startswith("/")' in func_source:
    print("STRUCTURAL PASS: explicit forward-slash check present in safe_join")
    sys.exit(0)
else:
    print("STRUCTURAL FAIL: no explicit forward-slash startswith check found")
    sys.exit(1)
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
    ("def safe_join" in source, "safe_join function present"),
    ("os.path.isabs" in source, "os.path.isabs check present"),
    ("_os_alt_seps" in source, "_os_alt_seps reference present"),
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
# Source: AGENTS.md line 43 @ commit e29e1ccd5874cb98b813ed4f7f72d9fef2935016
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
