#!/usr/bin/env bash
set +e

FILE="tests/v1/engine/test_abort_final_step.py"
TOTAL=0
add_score() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

# ── GATE (0.00): Python syntax check ──
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "import ast; ast.parse(open('$FILE').read())" 2>/dev/null; then
    echo "GATE FAILED: $FILE has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# ── F2P BEHAVIORAL (0.35): Polling captures delayed status write ──
# [pr_diff] (0.35): Extracts the wait/poll logic from the test function and runs it
# against a status file that gets FINISHED_ABORTED written after 300ms.
# The buggy code (fixed sleep 0.1s then single read) fails because the status
# hasn't been written yet at 100ms. Any correct polling implementation succeeds.
python3 << 'PYEOF'
import ast, sys, textwrap, re, tempfile, time, os, threading, subprocess

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find the test function
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    print("Could not find test_abort function")
    sys.exit(1)

# Get function source lines
all_lines = source.splitlines()
func_lines = all_lines[test_func.lineno - 1 : test_func.end_lineno]

# Find gen_task await and first captured_statuses/FINISHED_ assert
gen_idx = None
assert_idx = None
for i, line in enumerate(func_lines):
    s = line.strip()
    if gen_idx is None and 'gen_task' in s and 'await' in s:
        gen_idx = i
    if gen_idx is not None and 'assert' in s and ('captured_statuses' in s or 'FINISHED_' in s):
        assert_idx = i
        break

if gen_idx is None or assert_idx is None:
    print("Could not find gen_task/assert boundaries")
    sys.exit(1)

# Extract the wait section between gen_task and assertion
wait_lines = func_lines[gen_idx + 1 : assert_idx]

# Filter out lines referencing engine-specific variables (outputs, final_output)
filtered = []
skip_continuation = False
for line in wait_lines:
    s = line.strip()
    if not s or s.startswith('#'):
        continue
    # Skip assertions about outputs/final_output
    if 'assert' in s and ('outputs' in s or 'final_output' in s):
        skip_continuation = True
        continue
    if skip_continuation:
        if s.startswith(('f"', '"', "f'", "'", ")", 'f"')):
            continue
        skip_continuation = False
    if any(kw in s for kw in ['final_output', '.outputs[', 'finish_reason']):
        continue
    filtered.append(line)

if not filtered:
    print("No wait logic found between gen_task and assertion")
    sys.exit(1)

# Dedent to minimum indentation
indents = [len(l) - len(l.lstrip()) for l in filtered if l.strip()]
if not indents:
    sys.exit(1)
min_ind = min(indents)
dedented = [l[min_ind:] if len(l) >= min_ind else l for l in filtered]
wait_code = "\n".join(dedented)

# Detect the file-path variable name used in open() calls
open_match = re.search(r'open\((\w+)', wait_code)
file_var = open_match.group(1) if open_match else 'status_file'

is_async = 'await' in wait_code

# Create temp status file with initial content
sf = tempfile.mktemp(suffix='.txt')
with open(sf, 'w') as f:
    f.write("INIT:WORKER\nINIT:SCHEDULER\n")

# Build a harness that runs the extracted code with a delayed write
indent_wait = textwrap.indent(wait_code, "    ")

if is_async:
    harness = f'''import asyncio, time, os, sys, threading
from pathlib import Path

def delayed_write():
    time.sleep(0.3)
    with open("{sf}", "a") as f:
        f.write("FINISHED_ABORTED\\n")

threading.Thread(target=delayed_write, daemon=True).start()

async def _run():
    {file_var} = "{sf}"
    timeout = 2.0
    start = time.time()
    captured_statuses = []
    status_lines = []
{indent_wait}
    return captured_statuses

try:
    result = asyncio.run(_run())
    sys.exit(0 if "FINISHED_ABORTED" in result else 1)
except Exception:
    sys.exit(1)
finally:
    try: os.unlink("{sf}")
    except: pass
'''
else:
    harness = f'''import time, os, sys, threading
from pathlib import Path

def delayed_write():
    time.sleep(0.3)
    with open("{sf}", "a") as f:
        f.write("FINISHED_ABORTED\\n")

threading.Thread(target=delayed_write, daemon=True).start()

{file_var} = "{sf}"
timeout = 2.0
start = time.time()
captured_statuses = []
status_lines = []

{wait_code}

try: os.unlink("{sf}")
except: pass
sys.exit(0 if "FINISHED_ABORTED" in captured_statuses else 1)
'''

harness_file = '/tmp/_poll_behavioral_test.py'
with open(harness_file, 'w') as f:
    f.write(harness)

result = subprocess.run([sys.executable, harness_file], timeout=15,
                       capture_output=True, text=True)
try: os.unlink(harness_file)
except: pass
try: os.unlink(sf)
except: pass

if result.returncode != 0:
    print(f"Harness stderr: {result.stderr[:200]}")
sys.exit(result.returncode)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: Polling captures delayed FINISHED_ABORTED write"
    add_score 0.35
else
    echo "FAIL: Polling did not capture delayed FINISHED_ABORTED"
fi

# ── F2P BEHAVIORAL (0.20): Timeout prevents indefinite hanging ──
# [pr_diff] (0.20): Runs the polling code against a file that NEVER gets
# FINISHED_. Must complete (timeout/error) without hanging.
# Buggy code with no timeout would hang forever.
timeout 10 python3 << 'PYEOF'
import ast, sys, textwrap, re, tempfile, time, os, subprocess

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find test function
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    sys.exit(1)

# Same extraction as above
all_lines = source.splitlines()
func_lines = all_lines[test_func.lineno - 1 : test_func.end_lineno]

gen_idx = None
assert_idx = None
for i, line in enumerate(func_lines):
    s = line.strip()
    if gen_idx is None and 'gen_task' in s and 'await' in s:
        gen_idx = i
    if gen_idx is not None and 'assert' in s and ('captured_statuses' in s or 'FINISHED_' in s):
        assert_idx = i
        break

if gen_idx is None or assert_idx is None:
    sys.exit(1)

wait_lines = func_lines[gen_idx + 1 : assert_idx]
filtered = []
skip_continuation = False
for line in wait_lines:
    s = line.strip()
    if not s or s.startswith('#'):
        continue
    if 'assert' in s and ('outputs' in s or 'final_output' in s):
        skip_continuation = True
        continue
    if skip_continuation:
        if s.startswith(('f"', '"', "f'", "'", ")", 'f"')):
            continue
        skip_continuation = False
    if any(kw in s for kw in ['final_output', '.outputs[', 'finish_reason']):
        continue
    filtered.append(line)

if not filtered:
    sys.exit(1)

indents = [len(l) - len(l.lstrip()) for l in filtered if l.strip()]
if not indents:
    sys.exit(1)
min_ind = min(indents)
dedented = [l[min_ind:] if len(l) >= min_ind else l for l in filtered]
wait_code = "\n".join(dedented)

open_match = re.search(r'open\((\w+)', wait_code)
file_var = open_match.group(1) if open_match else 'status_file'
is_async = 'await' in wait_code

# Create temp status file that will NEVER get FINISHED_ written
sf = tempfile.mktemp(suffix='.txt')
with open(sf, 'w') as f:
    f.write("INIT:WORKER\nINIT:SCHEDULER\n")

indent_wait = textwrap.indent(wait_code, "    ")

if is_async:
    harness = f'''import asyncio, time, os, sys
from pathlib import Path

async def _run():
    {file_var} = "{sf}"
    timeout = 1.0  # Short timeout so test finishes quickly
    start = time.time()
    captured_statuses = []
    status_lines = []
{indent_wait}
    return captured_statuses

try:
    asyncio.run(_run())
    # If it returns without error, that means no hang (might have empty result)
    sys.exit(0)
except (TimeoutError, asyncio.TimeoutError):
    # Good: timeout raised instead of hanging
    sys.exit(0)
except Exception:
    # Some error, but at least it didn't hang
    sys.exit(0)
finally:
    try: os.unlink("{sf}")
    except: pass
'''
else:
    harness = f'''import time, os, sys
from pathlib import Path

{file_var} = "{sf}"
timeout = 1.0
start = time.time()
captured_statuses = []
status_lines = []

try:
{textwrap.indent(wait_code, "    ")}
except (TimeoutError,):
    pass
finally:
    try: os.unlink("{sf}")
    except: pass
sys.exit(0)
'''

harness_file = '/tmp/_timeout_behavioral_test.py'
with open(harness_file, 'w') as f:
    f.write(harness)

result = subprocess.run([sys.executable, harness_file], timeout=8,
                       capture_output=True, text=True)
try: os.unlink(harness_file)
except: pass
try: os.unlink(sf)
except: pass
sys.exit(result.returncode)
PYEOF

RET=$?
if [ $RET -eq 0 ]; then
    echo "PASS: Timeout mechanism prevents hanging"
    add_score 0.20
elif [ $RET -eq 124 ]; then
    echo "FAIL: Polling hangs forever (no timeout mechanism)"
else
    echo "FAIL: Timeout test error (exit $RET)"
fi

# ── F2P STRUCTURAL (0.05): No fixed sleep as sole wait mechanism ──
# [pr_diff] (0.05): asyncio.sleep(0.1) must not be the only wait before reading status
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find the test function
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    sys.exit(1)

# Check for standalone await asyncio.sleep(0.1) NOT inside a while loop
# This is the buggy pattern
while_ranges = set()
for node in ast.walk(test_func):
    if isinstance(node, ast.While):
        while_ranges.add((node.lineno, node.end_lineno))

for node in ast.walk(test_func):
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Await):
        call = node.value.value
        if (isinstance(call, ast.Call) and
            isinstance(call.func, ast.Attribute) and
            call.func.attr == 'sleep' and
            len(call.args) == 1 and
            isinstance(call.args[0], ast.Constant) and
            call.args[0].value == 0.1):
            # Check if this sleep is inside a while loop
            in_loop = any(start <= node.lineno <= end for start, end in while_ranges)
            if not in_loop:
                # Found standalone sleep(0.1) - buggy pattern
                sys.exit(1)
sys.exit(0)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: No standalone asyncio.sleep(0.1) as sole wait"
    add_score 0.05
else
    echo "FAIL: Buggy asyncio.sleep(0.1) pattern still present"
fi

# ── P2P REGRESSION (0.10): FINISHED_ABORTED assertion preserved ──
# [pr_diff] (0.10): Test must still assert on FINISHED_ABORTED status
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find test function and check for FINISHED_ABORTED in an assert
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    sys.exit(1)

# Check for FINISHED_ABORTED in assertion context
func_src = ast.get_source_segment(source, test_func)
if func_src and 'FINISHED_ABORTED' in func_src and 'assert' in func_src:
    sys.exit(0)
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: FINISHED_ABORTED assertion preserved"
    add_score 0.10
else
    echo "FAIL: FINISHED_ABORTED assertion missing from test function"
fi

# ── P2P REGRESSION (0.05): Test function signature preserved ──
# [pr_diff] (0.05): Both parametrized test variants must still exist
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Check for async test function with parametrize on async_scheduling
found_func = False
found_param = False
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name and 'final' in node.name:
            found_func = True
            # Check for async_scheduling parameter
            for arg in node.args.args:
                if arg.arg == 'async_scheduling':
                    found_param = True
if 'async_scheduling' in source and 'parametrize' in source:
    found_param = True  # parametrize decorator references it

sys.exit(0 if (found_func and found_param) else 1)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: Test function signature and parametrize preserved"
    add_score 0.05
else
    echo "FAIL: Test function signature or parametrize missing"
fi

# ── ANTI-GAMING (0.10): Polling logic is inside the test function ──
# [pr_diff] (0.10): The wait/poll code must be reachable from the test function,
# not dead code in an unrelated function
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find test function
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    sys.exit(1)

func_src = ast.get_source_segment(source, test_func) or ""

# The polling/wait logic must be inside the test function OR in a helper called from it
# Check: test function body contains either:
# 1. A while loop with file reading (direct polling), OR
# 2. A call to a function that contains such a loop

# Direct check
has_direct_poll = False
for node in ast.walk(test_func):
    if isinstance(node, ast.While):
        seg = ast.get_source_segment(source, node) or ""
        if 'FINISHED_' in seg or 'open(' in seg:
            has_direct_poll = True
            break

# Helper check: find function calls in test body, check if those functions poll
has_helper_poll = False
if not has_direct_poll:
    # Get all function/method names called from test body
    called_names = set()
    for node in ast.walk(test_func):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.add(node.func.attr)

    # Check if any top-level function with those names contains polling
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            if node.name in called_names:
                seg = ast.get_source_segment(source, node) or ""
                if ('while' in seg.lower() or 'for' in seg.lower()) and 'FINISHED_' in seg:
                    has_helper_poll = True
                    break

sys.exit(0 if (has_direct_poll or has_helper_poll) else 1)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: Polling logic is reachable from test function"
    add_score 0.10
else
    echo "FAIL: No reachable polling logic in test function"
fi

# ── ANTI-STUB (0.10): File is not trivially emptied ──
# [static] (0.10): File must have substantial content
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Count meaningful statements (not just line count)
line_count = len(source.splitlines())
func_count = sum(1 for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))

# Must have >200 lines AND >5 functions (the file has DummyKVConnector methods etc.)
if line_count > 200 and func_count > 5:
    sys.exit(0)
sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    LINE_COUNT=$(wc -l < "$FILE")
    echo "PASS: File is not a stub ($LINE_COUNT lines)"
    add_score 0.10
else
    echo "FAIL: File appears to be a stub"
fi

# ── P2P REGRESSION (0.05): captured_statuses used in assertion ──
# [pr_diff] (0.05): The polling result must feed into the FINISHED_ABORTED assertion
python3 << 'PYEOF'
import ast, sys

FILE = "tests/v1/engine/test_abort_final_step.py"
with open(FILE) as f:
    source = f.read()
tree = ast.parse(source)

# Find test function
test_func = None
for node in ast.walk(tree):
    if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
        if 'test_abort' in node.name:
            test_func = node
            break
if not test_func:
    sys.exit(1)

# Check that there's an assert referencing both status results AND FINISHED_ABORTED
func_src = ast.get_source_segment(source, test_func) or ""
has_status_assert = ('captured_statuses' in func_src or 'status' in func_src.lower())
has_abort_assert = 'FINISHED_ABORTED' in func_src
has_assert = 'assert' in func_src

sys.exit(0 if (has_status_assert and has_abort_assert and has_assert) else 1)
PYEOF

if [ $? -eq 0 ]; then
    echo "PASS: Status result feeds into FINISHED_ABORTED assertion"
    add_score 0.05
else
    echo "FAIL: Missing connection between polling result and assertion"
fi

echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# Write detailed results
python3 -c "
import json, sys
reward = float(open('/logs/verifier/reward.txt').read().strip())
json.dump({
    'reward': reward,
    'behavioral': min(reward, 0.55),
    'regression': min(max(reward - 0.55, 0), 0.20),
    'anti_stub': min(max(reward - 0.75, 0), 0.10),
    'anti_gaming': min(max(reward - 0.85, 0), 0.10)
}, open('/logs/verifier/reward.json', 'w'))
" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
