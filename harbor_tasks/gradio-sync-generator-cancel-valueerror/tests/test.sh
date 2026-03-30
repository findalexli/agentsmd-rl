#!/usr/bin/env bash
# Verifier for gradio-sync-generator-cancel-valueerror
#
# Bug: SyncToAsyncIterator.aclose() calls self.iterator.close() without retry,
# causing ValueError("generator already executing") when cancelling sync
# generators mid-iteration. The retry logic exists in safe_aclose_iterator()
# but is not reachable from the aclosing() path.
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
#   TEST 1 (fail-to-pass: aclose has retry logic)          = 0.30
#   TEST 2 (fail-to-pass: behavioral — aclose retries)     = 0.30
#   TEST 3 (fail-to-pass: safe_aclose_iterator simplified) = 0.15
#   TEST 4 (pass-to-pass: class and function exist)        = 0.10
#   TEST 5 (anti-stub)                                     = 0.10
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: SyncToAsyncIterator.aclose() has retry logic
#
# In the buggy code, aclose() is simply:
#   async def aclose(self):
#       self.iterator.close()
# The fix adds a retry loop that catches ValueError("already executing").
# We check that the aclose method body contains retry/loop logic.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] SyncToAsyncIterator.aclose() must have retry logic for ValueError"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find SyncToAsyncIterator class
cls_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SyncToAsyncIterator':
        cls_node = node
        break

if cls_node is None:
    print("FAIL: SyncToAsyncIterator class not found")
    sys.exit(1)

# Find aclose method
aclose_node = None
for item in cls_node.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'aclose':
        aclose_node = item
        break

if aclose_node is None:
    print("FAIL: aclose method not found in SyncToAsyncIterator")
    sys.exit(1)

# Check that aclose has retry logic: must contain a While loop or a try/except
# that catches ValueError
has_while = False
has_try_valueerror = False
has_sleep = False

for node in ast.walk(aclose_node):
    if isinstance(node, ast.While):
        has_while = True
    if isinstance(node, ast.ExceptHandler):
        if node.type is not None:
            if isinstance(node.type, ast.Name) and node.type.id == 'ValueError':
                has_try_valueerror = True
            elif isinstance(node.type, ast.Tuple):
                for elt in node.type.elts:
                    if isinstance(elt, ast.Name) and elt.id == 'ValueError':
                        has_try_valueerror = True
    # Check for asyncio.sleep or anyio.sleep or time.sleep
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == 'sleep':
            has_sleep = True

# The buggy code has none of these. A correct fix must have retry with sleep.
if has_while and has_try_valueerror and has_sleep:
    print("PASS: aclose() has retry loop with ValueError handling and sleep")
    sys.exit(0)
elif has_try_valueerror and has_sleep:
    # Maybe uses recursion instead of while — still valid
    print("PASS: aclose() has ValueError handling with sleep (non-while retry)")
    sys.exit(0)
else:
    missing = []
    if not has_while:
        missing.append("while loop")
    if not has_try_valueerror:
        missing.append("ValueError handler")
    if not has_sleep:
        missing.append("sleep call")
    print(f"FAIL: aclose() missing retry components: {', '.join(missing)}")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.30]: Behavioral — aclose retries on ValueError
#
# Extract and execute: create a fake iterator that raises ValueError on first
# close() call, then verify SyncToAsyncIterator.aclose() retries and succeeds.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] behavioral: aclose retries when close() raises ValueError"
python3 << 'PYEOF'
import asyncio, sys, time
sys.path.insert(0, "/workspace/gradio")

try:
    from gradio.utils import SyncToAsyncIterator
except Exception as e:
    print(f"FAIL: could not import SyncToAsyncIterator: {e}")
    sys.exit(1)

class FakeIterator:
    """Iterator whose close() fails N times with ValueError before succeeding."""
    def __init__(self, fail_count=2):
        self.close_call_count = 0
        self._fail_count = fail_count
        self._closed = False

    def close(self):
        self.close_call_count += 1
        if self.close_call_count <= self._fail_count:
            raise ValueError("generator already executing")
        self._closed = True

    def __next__(self):
        raise StopIteration

    def __iter__(self):
        return self

async def test_retry():
    fake = FakeIterator(fail_count=2)
    iterator = SyncToAsyncIterator(fake, limiter=None)
    try:
        # Use small retry_interval for fast test
        await iterator.aclose(retry_interval=0.01, timeout=5.0)
    except TypeError:
        # If aclose doesn't accept kwargs, it hasn't been fixed
        print("FAIL: aclose() does not accept timeout/retry_interval parameters")
        return False
    except ValueError:
        print("FAIL: aclose() raised ValueError without retrying")
        return False

    if fake._closed and fake.close_call_count == 3:
        print(f"PASS: aclose retried {fake.close_call_count} times and succeeded")
        return True
    elif fake._closed:
        print(f"PASS: aclose succeeded after {fake.close_call_count} attempts")
        return True
    else:
        print(f"FAIL: iterator not closed (calls={fake.close_call_count})")
        return False

result = asyncio.run(test_retry())
sys.exit(0 if result else 1)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: safe_aclose_iterator simplified
#
# In the buggy code, safe_aclose_iterator has SyncToAsyncIterator-specific
# retry logic (isinstance check + while loop). The fix simplifies it to just
# delegate to iterator.aclose(). We verify it no longer has the isinstance
# check for SyncToAsyncIterator.
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] safe_aclose_iterator no longer has SyncToAsyncIterator isinstance check"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find safe_aclose_iterator function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'safe_aclose_iterator':
        func_node = node
        break

if func_node is None:
    print("FAIL: safe_aclose_iterator function not found")
    sys.exit(1)

# Check that the function body does NOT contain isinstance check for SyncToAsyncIterator
func_source = ast.get_source_segment(source, func_node) or ""
has_isinstance_check = False
has_while_loop = False

for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id == 'isinstance':
            # Check if it's checking for SyncToAsyncIterator
            if len(node.args) >= 2:
                arg2 = node.args[1]
                if isinstance(arg2, ast.Name) and arg2.id == 'SyncToAsyncIterator':
                    has_isinstance_check = True
    if isinstance(node, ast.While):
        has_while_loop = True

if has_isinstance_check:
    print("FAIL: safe_aclose_iterator still has isinstance(iterator, SyncToAsyncIterator) check")
    sys.exit(1)

if has_while_loop:
    print("FAIL: safe_aclose_iterator still has retry while loop (should be in aclose now)")
    sys.exit(1)

# Verify the function signature no longer has timeout/retry_interval params
params = [arg.arg for arg in func_node.args.args]
if 'timeout' in params or 'retry_interval' in params:
    print("FAIL: safe_aclose_iterator still has timeout/retry_interval parameters")
    sys.exit(1)

print("PASS: safe_aclose_iterator is simplified (no isinstance check, no while loop, no retry params)")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: Key structures still exist
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] SyncToAsyncIterator class and safe_aclose_iterator exist"
python3 << 'PYEOF'
import ast, sys

with open("/workspace/gradio/gradio/utils.py") as f:
    source = f.read()

tree = ast.parse(source)

found_class = False
found_func = False
found_aclose = False
found_anext = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SyncToAsyncIterator':
        found_class = True
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if item.name == 'aclose':
                    found_aclose = True
                if item.name == '__anext__':
                    found_anext = True
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'safe_aclose_iterator':
        found_func = True

missing = []
if not found_class:
    missing.append("SyncToAsyncIterator class")
if not found_aclose:
    missing.append("aclose method")
if not found_anext:
    missing.append("__anext__ method")
if not found_func:
    missing.append("safe_aclose_iterator function")

if missing:
    print(f"FAIL: missing: {', '.join(missing)}")
    sys.exit(1)

print("PASS: all key structures present")
sys.exit(0)
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
# Source: AGENTS.md line 43 @ commit a09c0e891709e007e4f265fc48f466175f5a2a22
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
t1 = 0.30 if $T1 == 0 else 0.0
t2 = 0.30 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.10 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (fail-to-pass: aclose retry logic)     = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: behavioral retry)       = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 3 (fail-to-pass: simplified safe_aclose) = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (pass-to-pass: structures exist)       = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 5 (anti-stub)                            = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (config: ruff format)                   = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
