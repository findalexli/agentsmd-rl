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
# Weight allocation (>=80% behavioral):
#   TEST 1 (behavioral: aclose retry with FakeIterator)    = 0.40
#   TEST 2 (behavioral: aclose accepts retry params)       = 0.15
#   TEST 3 (behavioral: safe_aclose_iterator delegates)    = 0.15
#   TEST 4 (behavioral: real race condition simulation)    = 0.15
#   TEST 5 (pass-to-pass: class and function exist)        = 0.10
#   TEST 6 (anti-stub)                                     = 0.05
#   TOTAL                                                  = 1.00
###############################################################################
SCORE=0

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.40]: aclose retries on ValueError("already executing")
#
# Extract and execute: create a fake iterator that raises ValueError on first
# close() calls, then verify SyncToAsyncIterator.aclose() retries and succeeds.
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] behavioral: aclose retries when close() raises ValueError"
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

    # Check that aclose accepts timeout/retry_interval
    try:
        await iterator.aclose(retry_interval=0.01, timeout=5.0)
    except TypeError as e:
        print(f"FAIL: aclose() does not accept timeout/retry_interval parameters: {e}")
        return False
    except ValueError:
        print("FAIL: aclose() raised ValueError without retrying")
        return False

    if not fake._closed:
        print(f"FAIL: iterator not closed (calls={fake.close_call_count})")
        return False

    if fake.close_call_count < 2:
        print(f"FAIL: expected at least 2 close calls, got {fake.close_call_count}")
        return False

    print(f"PASS: aclose retried {fake.close_call_count} times and succeeded")
    return True

result = asyncio.run(test_retry())
sys.exit(0 if result else 1)
PYEOF
T1=$?
echo "  -> exit code: $T1"

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.15]: aclose parameter signature
#
# Verify aclose accepts timeout and retry_interval with proper defaults.
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] aclose accepts timeout/retry_interval parameters"
python3 << 'PYEOF'
import asyncio, sys, inspect
sys.path.insert(0, "/workspace/gradio")

try:
    from gradio.utils import SyncToAsyncIterator
except Exception as e:
    print(f"FAIL: could not import SyncToAsyncIterator: {e}")
    sys.exit(1)

# Check method signature accepts timeout and retry_interval
sig = inspect.signature(SyncToAsyncIterator.aclose)
params = list(sig.parameters.keys())

if 'timeout' not in params or 'retry_interval' not in params:
    print(f"FAIL: aclose missing timeout/retry_interval parameters, got: {params}")
    sys.exit(1)

# Check default values
timeout_param = sig.parameters.get('timeout')
retry_param = sig.parameters.get('retry_interval')

if timeout_param.default is inspect.Parameter.empty:
    print("FAIL: timeout has no default value")
    sys.exit(1)

if retry_param.default is inspect.Parameter.empty:
    print("FAIL: retry_interval has no default value")
    sys.exit(1)

# Values should be reasonable (timeout > 0, retry_interval > 0)
if timeout_param.default <= 0:
    print(f"FAIL: timeout default should be > 0, got {timeout_param.default}")
    sys.exit(1)

if retry_param.default <= 0:
    print(f"FAIL: retry_interval default should be > 0, got {retry_param.default}")
    sys.exit(1)

print(f"PASS: aclose(timeout={timeout_param.default}, retry_interval={retry_param.default})")
sys.exit(0)
PYEOF
T2=$?
echo "  -> exit code: $T2"

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.15]: safe_aclose_iterator delegates to aclose
#
# Verify that safe_aclose_iterator actually calls iterator.aclose() and
# propagates exceptions properly.
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] safe_aclose_iterator delegates to aclose"
python3 << 'PYEOF'
import asyncio, sys
sys.path.insert(0, "/workspace/gradio")

try:
    from gradio.utils import safe_aclose_iterator
except Exception as e:
    print(f"FAIL: could not import safe_aclose_iterator: {e}")
    sys.exit(1)

class MockIterator:
    def __init__(self):
        self.aclose_called = False
        self.aclose_args = None

    async def aclose(self, *args, **kwargs):
        self.aclose_called = True
        self.aclose_args = (args, kwargs)

async def test_delegation():
    mock = MockIterator()
    await safe_aclose_iterator(mock)

    if not mock.aclose_called:
        print("FAIL: safe_aclose_iterator did not call iterator.aclose()")
        return False

    print("PASS: safe_aclose_iterator delegates to aclose()")
    return True

result = asyncio.run(test_delegation())
sys.exit(0 if result else 1)
PYEOF
T3=$?
echo "  -> exit code: $T3"

###############################################################################
# TEST 4 [FAIL-TO-PASS, 0.15]: Race condition simulation
#
# Simulate closer to real conditions: iterator that takes time to close
# and raises ValueError intermittently.
###############################################################################
echo ""
echo "TEST 4: [fail-to-pass] race condition simulation"
python3 << 'PYEOF'
import asyncio, sys, time, threading
sys.path.insert(0, "/workspace/gradio")

try:
    from gradio.utils import SyncToAsyncIterator
except Exception as e:
    print(f"FAIL: could not import SyncToAsyncIterator: {e}")
    sys.exit(1)

class RacingIterator:
    """Simulates iterator that is executing when close() is called."""
    def __init__(self, fail_for_ms=50):
        self._executing = True
        self._closed = False
        self._lock = threading.Lock()
        self.fail_until = time.monotonic() + (fail_for_ms / 1000)

    def __next__(self):
        with self._lock:
            if self._closed:
                raise StopIteration
        return "item"

    def __iter__(self):
        return self

    def close(self):
        with self._lock:
            if time.monotonic() < self.fail_until:
                raise ValueError("generator already executing")
            self._closed = True

async def test_race_condition():
    racing = RacingIterator(fail_for_ms=50)
    iterator = SyncToAsyncIterator(racing, limiter=None)

    # Try to close while "executing"
    start = time.monotonic()
    try:
        await iterator.aclose(timeout=1.0, retry_interval=0.01)
        elapsed = time.monotonic() - start
        if elapsed < 0.04:  # Should have retried at least a few times
            print(f"WARNING: elapsed time {elapsed:.3f}s seems too fast, may not have retried")
    except ValueError as e:
        print(f"FAIL: aclose raised ValueError: {e}")
        return False

    if not racing._closed:
        print("FAIL: iterator was not closed")
        return False

    print(f"PASS: aclose handled race condition")
    return True

result = asyncio.run(test_race_condition())
sys.exit(0 if result else 1)
PYEOF
T4=$?
echo "  -> exit code: $T4"

###############################################################################
# TEST 5 [PASS-TO-PASS, 0.10]: Key structures still exist
###############################################################################
echo ""
echo "TEST 5: [pass-to-pass] SyncToAsyncIterator class and safe_aclose_iterator exist"
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
T5=$?
echo "  -> exit code: $T5"

###############################################################################
# TEST 6 [ANTI-STUB, 0.05]: File not replaced with stub
###############################################################################
echo ""
echo "TEST 6: [anti-stub] file is not a stub"
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

# Check for the specific anti-stub: no trivial pass-only aclose
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SyncToAsyncIterator':
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'aclose':
                # Count non-pass/non-docstring statements
                stmt_count = 0
                for stmt in item.body:
                    if isinstance(stmt, ast.Pass):
                        continue
                    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                        continue  # Docstring
                    stmt_count += 1
                if stmt_count < 3:
                    print(f"FAIL: aclose has only {stmt_count} meaningful statements (likely stub)")
                    sys.exit(1)

print(f"PASS: {line_count} lines, {funcs} functions, aclose has substance")
sys.exit(0)
PYEOF
T6=$?
echo "  -> exit code: $T6"

###############################################################################
# Final weighted score
###############################################################################
echo ""
SCORE=$(python3 -c "
t1 = 0.40 if $T1 == 0 else 0.0
t2 = 0.15 if $T2 == 0 else 0.0
t3 = 0.15 if $T3 == 0 else 0.0
t4 = 0.15 if $T4 == 0 else 0.0
t5 = 0.10 if $T5 == 0 else 0.0
t6 = 0.05 if $T6 == 0 else 0.0
score = t1 + t2 + t3 + t4 + t5 + t6
print(f'{score:.2f}')
")
echo "RESULT: score = $SCORE"
echo "  TEST 1 (behavioral: aclose retry)             = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.40]"
echo "  TEST 2 (behavioral: aclose parameters)        = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 3 (behavioral: safe_aclose delegates)    = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 4 (behavioral: race condition)           = $([ $T4 -eq 0 ] && echo PASS || echo FAIL) [0.15]"
echo "  TEST 5 (pass-to-pass: structures exist)       = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (anti-stub: file content)              = $([ $T6 -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
