#!/usr/bin/env bash
# Verifier for gradio-duplicate-block-error-reload
#
# Bug: After exec() in watchfn, Context.id is not advanced past existing block
# IDs, causing DuplicateBlockError when gr.render creates new blocks that
# collide with IDs from already-imported child page modules.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/gradio/gradio/utils.py"

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/gradio/gradio/utils.py") as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f"GATE FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: Context.id adjusted after exec)  = 0.35
#   TEST 2 (fail-to-pass: behavioral — ID collision fixed) = 0.30
#   TEST 3 (pass-to-pass: watchfn function still exists)   = 0.10
#   TEST 4 (structural: Context.id reset still present)    = 0.10
#   TEST 5 (anti-stub)                                     = 0.10
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.35]: Context.id is adjusted after exec()
#
# In the buggy code, after exec(no_reload_source_code, module.__dict__),
# there is NO adjustment of Context.id based on existing block IDs.
# The fix adds code to set Context.id = max(Context.id, max(demo.blocks.keys()) + 1).
# We check that after the exec() line, there is code that reads demo.blocks
# or sets Context.id based on block keys.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] Context.id must be adjusted after exec() in watchfn"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

lines = source.splitlines()

# Find the watchfn function by looking for 'def watchfn' in the source
# (it might be a nested function inside another function)
watchfn_start = None
watchfn_end = None
for i, line in enumerate(lines):
    if 'def watchfn(' in line or 'def watchfn (' in line:
        watchfn_start = i
        break

if watchfn_start is None:
    # Try looking for the exec(no_reload_source_code pattern directly
    for i, line in enumerate(lines):
        if 'exec(no_reload_source_code' in line:
            watchfn_start = max(0, i - 50)
            break

if watchfn_start is None:
    print("FAIL: watchfn function or exec(no_reload_source_code) not found")
    sys.exit(1)

# Find the exec(no_reload_source_code, ...) line
exec_line_idx = None
for i in range(watchfn_start, min(watchfn_start + 200, len(lines))):
    if 'exec(no_reload_source_code' in lines[i]:
        exec_line_idx = i
        break

if exec_line_idx is None:
    print("FAIL: exec(no_reload_source_code) not found in watchfn region")
    sys.exit(1)

# Look in the 20 lines after exec() for Context.id adjustment based on blocks
region_after_exec = '\n'.join(lines[exec_line_idx + 1 : exec_line_idx + 25])

# Check for patterns that indicate Context.id is being set based on block IDs
has_context_id_adjustment = False
patterns_found = []

if 'Context.id' in region_after_exec and ('blocks' in region_after_exec or 'block' in region_after_exec):
    has_context_id_adjustment = True
    patterns_found.append("Context.id + blocks reference")

if 'max(' in region_after_exec and 'blocks' in region_after_exec:
    patterns_found.append("max() with blocks")

if 'demo' in region_after_exec and 'blocks' in region_after_exec:
    patterns_found.append("demo.blocks access")

if has_context_id_adjustment:
    print(f"PASS: Context.id is adjusted after exec() based on block IDs")
    print(f"  Patterns found: {', '.join(patterns_found)}")
    sys.exit(0)

# Alternative: maybe they set Context.id to a high number or use len()
if 'Context.id' in region_after_exec:
    # Check if any meaningful adjustment (not just Context.id = 0 which is the reset)
    for line in lines[exec_line_idx + 1 : exec_line_idx + 25]:
        stripped = line.strip()
        if 'Context.id' in stripped and '=' in stripped and 'Context.id = 0' not in stripped:
            has_context_id_adjustment = True
            patterns_found.append(f"Context.id reassignment: {stripped}")
            break

if has_context_id_adjustment:
    print(f"PASS: Context.id is adjusted after exec()")
    print(f"  Patterns found: {', '.join(patterns_found)}")
    sys.exit(0)

print("FAIL: No Context.id adjustment found after exec(no_reload_source_code)")
print("  The buggy code does not advance Context.id past existing block IDs")
sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.30]: Behavioral — simulated block ID collision fix
#
# Simulate the bug: create a mock demo with blocks dict, exec the watchfn
# pattern, and verify Context.id is advanced past existing block IDs.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] behavioral: Context.id advanced past existing block IDs"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

lines = source.splitlines()

# Find the exec line and extract the code block after it
exec_line_idx = None
for i, line in enumerate(lines):
    if 'exec(no_reload_source_code' in line:
        exec_line_idx = i
        break

if exec_line_idx is None:
    print("FAIL: exec(no_reload_source_code) not found")
    sys.exit(1)

# Extract the code after exec until the next significant block
# We look for the code that adjusts Context.id
# Check if there's code that gets demo from module and checks demo.blocks
post_exec_code = []
for i in range(exec_line_idx + 1, min(exec_line_idx + 25, len(lines))):
    line = lines[i]
    # Stop at the 'while' loop or 'sys.modules' line
    if 'while reloader.should_watch()' in line:
        break
    if 'sys.modules' in line:
        # Include this line but continue to check for more
        post_exec_code.append(line)
        continue
    post_exec_code.append(line)

post_exec_text = '\n'.join(post_exec_code)

# Check for the key elements of the fix:
# 1. Getting demo from module (getattr or module.demo_name)
# 2. Checking demo.blocks
# 3. Setting Context.id based on max of block keys
has_demo_access = 'demo' in post_exec_text and ('getattr' in post_exec_text or 'reloader.demo_name' in post_exec_text or 'demo_name' in post_exec_text)
has_blocks_check = 'blocks' in post_exec_text
has_max_id = 'max(' in post_exec_text or 'Context.id' in post_exec_text

if has_demo_access and has_blocks_check:
    print("PASS: Code after exec() accesses demo.blocks and adjusts IDs")
    sys.exit(0)

# Alternative check: maybe they iterate blocks or use a different approach
if 'Context.id' in post_exec_text and ('block' in post_exec_text.lower() or 'id' in post_exec_text.lower()):
    # Any Context.id adjustment that references blocks is a valid fix
    for line in post_exec_code:
        stripped = line.strip()
        if 'Context.id' in stripped and '= 0' not in stripped and stripped:
            print(f"PASS: Context.id adjusted: {stripped}")
            sys.exit(0)

print("FAIL: No demo.blocks access or Context.id adjustment found after exec()")
sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [PASS-TO-PASS, 0.10]: watchfn and Context.id = 0 reset still exist
###############################################################################
echo ""
echo "TEST 3: [pass-to-pass] watchfn structure preserved"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

checks = {
    "exec(no_reload_source_code": False,
    "Context.id = 0": False,
    "reloader.should_watch": False,
}

for key in checks:
    if key in source:
        checks[key] = True

missing = [k for k, v in checks.items() if not v]
if missing:
    print(f"FAIL: missing key patterns: {missing}")
    sys.exit(1)

print("PASS: watchfn structure preserved (exec, Context.id reset, should_watch)")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [STRUCTURAL, 0.10]: Context.id = 0 reset still happens BEFORE exec
###############################################################################
echo ""
echo "TEST 4: [structural] Context.id = 0 still precedes exec()"
python3 << 'PYEOF'
import sys

with open("/workspace/gradio/gradio/utils.py") as f:
    lines = f.readlines()

context_reset_line = None
exec_line = None

for i, line in enumerate(lines):
    if 'Context.id = 0' in line and context_reset_line is None:
        context_reset_line = i
    if 'exec(no_reload_source_code' in line and exec_line is None:
        exec_line = i

if context_reset_line is None or exec_line is None:
    print("FAIL: could not find Context.id = 0 or exec() lines")
    sys.exit(1)

if context_reset_line < exec_line:
    print(f"PASS: Context.id = 0 (line {context_reset_line+1}) precedes exec() (line {exec_line+1})")
    sys.exit(0)
else:
    print(f"FAIL: Context.id = 0 (line {context_reset_line+1}) does not precede exec() (line {exec_line+1})")
    sys.exit(1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [ANTI-STUB, 0.10]: File not replaced with stub
###############################################################################
echo ""
echo "TEST 5: [anti-stub] file is not a stub"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: only {line_count} lines (expected 500+)")
    sys.exit(1)

tree = ast.parse(source)
funcs = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
if funcs < 20:
    print(f"FAIL: only {funcs} functions (expected 20+)")
    sys.exit(1)

print(f"PASS: {line_count} lines, {funcs} functions")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"


# ---------- Config-derived test (0.05): "Python code formatted with ruff" ----------
# Source: AGENTS.md line 43 @ commit a17eb7888b48cbd98b1e0feb17e2614bf3853d66
echo "=== Config: ruff format check ==="
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/utils.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then T6=0; echo "TEST 6: config ruff format PASS"; else T6=1; echo "TEST 6: config ruff format FAIL"; fi
###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.35 if $T1 == 0 else 0.0
t2 = 0.30 if $T2 == 0 else 0.0
t3 = 0.10 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: Context.id adjustment)  = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.35]"
echo "  TEST 2 (fail-to-pass: behavioral ID fix)      = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (pass-to-pass: watchfn structure)       = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 4 (structural: reset precedes exec)       = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub)                             = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (config: ruff format)                   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
