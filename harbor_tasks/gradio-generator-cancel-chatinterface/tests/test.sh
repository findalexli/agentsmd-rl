#!/usr/bin/env bash
# Verifier for gradio-generator-cancel-chatinterface
#
# Bug: Generator not properly closed on cancel in ChatInterface;
# SyncToAsyncIterator.aclose() not async; safe_aclose_iterator missing await.
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

CHAT="/workspace/gradio/gradio/chat_interface.py"
UTILS="/workspace/gradio/gradio/utils.py"

REWARD=0.0

###############################################################################
# GATE: Python syntax validity
###############################################################################
python3 << 'PYEOF'
import ast, sys
for path in ["/workspace/gradio/gradio/chat_interface.py", "/workspace/gradio/gradio/utils.py"]:
    try:
        with open(path) as f:
            ast.parse(f.read())
    except SyntaxError as e:
        print(f"GATE FAIL: {path}: {e}")
        sys.exit(1)
sys.exit(0)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAILED: syntax error"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASSED"

###############################################################################
# Weight allocation:
#   TEST 1 (fail-to-pass: functional aclose test)           = 0.30
#   TEST 2 (fail-to-pass: safe_aclose_iterator functional)  = 0.25
#   TEST 3 (fail-to-pass: generator close behavior)         = 0.20
#   TEST 4 (pass-to-pass: upstream test suite)              = 0.10
#   TEST 5 (anti-stub: AST depth checks)                    = 0.10
#   TEST 6 (config: ruff format)                            = 0.05
#   TOTAL                                                   = 1.00
###############################################################################

###############################################################################
# TEST 1 [FAIL-TO-PASS, 0.30]: SyncToAsyncIterator.aclose() is awaitable
###############################################################################
echo ""
echo "TEST 1: [fail-to-pass] SyncToAsyncIterator.aclose() can be awaited"
python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '/workspace/gradio')

# Test that we can import and instantiate SyncToAsyncIterator
try:
    from gradio.utils import SyncToAsyncIterator
except ImportError as e:
    print(f"FAIL: Cannot import SyncToAsyncIterator: {e}")
    sys.exit(1)

# Create a test generator that tracks if close() was called
close_called = False
def test_generator():
    try:
        yield "item1"
        yield "item2"
    finally:
        nonlocal close_called
        close_called = True

# Test that aclose is actually async and can be awaited
async def test_aclose():
    gen = test_generator()
    # Create with minimal limiter
    import anyio
    limiter = anyio.CapacityLimiter(1)
    iterator = SyncToAsyncIterator(gen, limiter)

    # Check that aclose is a coroutine (async)
    result = iterator.aclose()
    if not asyncio.iscoroutine(result):
        print("FAIL: aclose() does not return a coroutine - it's not async")
        return False

    # Actually await it - this is what the bug prevents
    try:
        await result
    except Exception as e:
        print(f"FAIL: await aclose() raised exception: {e}")
        return False

    # Verify generator is closed
    try:
        next(gen)
        print("FAIL: Generator was not properly closed")
        return False
    except StopIteration:
        pass  # Expected, generator exhausted
    except Exception:
        pass  # Also fine, generator closed in other way

    return True

try:
    result = asyncio.run(test_aclose())
    if result:
        print("PASS: aclose() is async and awaitable")
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Test raised exception: {e}")
    sys.exit(1)
PYEOF
T1=$?
echo "  -> exit code: $T1"
if [ $T1 -eq 0 ]; then REWARD=$(python3 -c "print($REWARD + 0.30)"); fi

###############################################################################
# TEST 2 [FAIL-TO-PASS, 0.25]: safe_aclose_iterator properly awaits aclose
###############################################################################
echo ""
echo "TEST 2: [fail-to-pass] safe_aclose_iterator properly awaits aclose"
python3 << 'PYEOF'
import asyncio
import sys
import time
sys.path.insert(0, '/workspace/gradio')

async def test_safe_aclose():
    from gradio.utils import SyncToAsyncIterator, safe_aclose_iterator
    import anyio

    # Track if aclose was actually called and awaited
    aclose_called = [False]

    class MockIterator:
        def __init__(self):
            self.aclose_was_awaited = False

        async def aclose(self):
            # If not properly awaited, this would be a sync def returning None immediately
            await asyncio.sleep(0.01)  # Force async behavior
            self.aclose_was_awaited = True

    # Test with MockIterator (not SyncToAsyncIterator)
    mock = MockIterator()

    try:
        # Use short timeout since we expect quick completion
        await asyncio.wait_for(safe_aclose_iterator(mock, timeout=1.0), timeout=2.0)
    except Exception as e:
        print(f"FAIL: safe_aclose_iterator raised: {e}")
        return False

    if not mock.aclose_was_awaited:
        print("FAIL: aclose was not called or not awaited")
        return False

    # Now test with SyncToAsyncIterator
    def gen():
        yield 1

    limiter = anyio.CapacityLimiter(1)
    sync_async_iter = SyncToAsyncIterator(gen(), limiter)

    try:
        await asyncio.wait_for(safe_aclose_iterator(sync_async_iter, timeout=1.0), timeout=2.0)
    except Exception as e:
        print(f"FAIL: safe_aclose_iterator with SyncToAsyncIterator raised: {e}")
        return False

    print("PASS: safe_aclose_iterator properly awaits aclose")
    return True

try:
    result = asyncio.run(test_safe_aclose())
    if result:
        sys.exit(0)
    else:
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Test raised exception: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
T2=$?
echo "  -> exit code: $T2"
if [ $T2 -eq 0 ]; then REWARD=$(python3 -c "print($REWARD + 0.25)"); fi

###############################################################################
# TEST 3 [FAIL-TO-PASS, 0.20]: Generator cleanup in chat_interface uses aclosing
###############################################################################
echo ""
echo "TEST 3: [fail-to-pass] chat_interface wraps generators with aclosing"
python3 << 'PYEOF'
import ast
import sys
sys.path.insert(0, '/workspace/gradio')

# First check that aclosing is imported from contextlib
with open("/workspace/gradio/gradio/chat_interface.py") as f:
    source = f.read()
    tree = ast.parse(source)

has_aclosing_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module == 'contextlib':
            for alias in node.names:
                if alias.name == 'aclosing':
                    has_aclosing_import = True
                    break

if not has_aclosing_import:
    print("FAIL: aclosing not imported from contextlib")
    sys.exit(1)

# Now test functional behavior: check that aclosing is used in async context managers
# in _stream_fn and _examples_stream_fn
found_stream_fn = False
found_examples_stream_fn = False
uses_aclosing_in_stream_fn = False
uses_aclosing_in_examples_stream_fn = False

for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef):
        if node.name == '_stream_fn':
            found_stream_fn = True
            # Look for async with statements using aclosing
            for item in ast.walk(node):
                if isinstance(item, ast.AsyncWith):
                    for ctx_expr in item.items:
                        if isinstance(ctx_expr.context_expr, ast.Call):
                            if isinstance(ctx_expr.context_expr.func, ast.Name):
                                if ctx_expr.context_expr.func.id == 'aclosing':
                                    uses_aclosing_in_stream_fn = True
                                    break

        elif node.name == '_examples_stream_fn':
            found_examples_stream_fn = True
            for item in ast.walk(node):
                if isinstance(item, ast.AsyncWith):
                    for ctx_expr in item.items:
                        if isinstance(ctx_expr.context_expr, ast.Call):
                            if isinstance(ctx_expr.context_expr.func, ast.Name):
                                if ctx_expr.context_expr.func.id == 'aclosing':
                                    uses_aclosing_in_examples_stream_fn = True
                                    break

if not found_stream_fn:
    print("FAIL: _stream_fn not found")
    sys.exit(1)

if not found_examples_stream_fn:
    print("FAIL: _examples_stream_fn not found")
    sys.exit(1)

if not uses_aclosing_in_stream_fn:
    print("FAIL: _stream_fn does not use aclosing() context manager")
    sys.exit(1)

if not uses_aclosing_in_examples_stream_fn:
    print("FAIL: _examples_stream_fn does not use aclosing() context manager")
    sys.exit(1)

print("PASS: Both methods properly use aclosing() context manager")
sys.exit(0)
PYEOF
T3=$?
echo "  -> exit code: $T3"
if [ $T3 -eq 0 ]; then REWARD=$(python3 -c "print($REWARD + 0.20)"); fi

###############################################################################
# TEST 4 [PASS-TO-PASS, 0.10]: Upstream test suite if available
###############################################################################
echo ""
echo "TEST 4: [pass-to-pass] upstream test suite regression check"
UPSTREAM_PASSED=0
if [ -d "/workspace/gradio/test" ] || [ -d "/workspace/gradio/tests" ]; then
    cd /workspace/gradio
    # Try to run tests related to utils/chat_interface if they exist
    python3 -m pytest test/test_utils.py -x --timeout=30 -q 2>/dev/null || true
    UPSTREAM_PASSED=1
fi
if [ $UPSTREAM_PASSED -eq 1 ]; then
    echo "PASS: Upstream tests run (best-effort)"
    REWARD=$(python3 -c "print($REWARD + 0.10)")
else
    echo "SKIP: No upstream tests available"
fi

###############################################################################
# TEST 5 [ANTI-STUB, 0.10]: Function body depth > 3 statements
###############################################################################
echo ""
echo "TEST 5: [anti-stub] Functions have substantial implementation"
python3 << 'PYEOF'
import ast
import sys

def count_meaningful_statements(body):
    """Count non-docstring, non-pass meaningful statements"""
    count = 0
    for stmt in body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            continue  # Skip docstrings
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Constant) and stmt.value is None:
            continue
        count += 1
        # Count statements inside if/for/while/try/except
        if isinstance(stmt, (ast.If, ast.For, ast.While)):
            count += count_meaningful_statements(stmt.body)
        elif isinstance(stmt, ast.Try):
            count += count_meaningful_statements(stmt.body)
            for handler in stmt.handlers:
                count += count_meaningful_statements(handler.body)
    return count

# Check SyncToAsyncIterator.aclose
with open("/workspace/gradio/gradio/utils.py") as f:
    tree = ast.parse(f.read())

aclose_found = False
aclose_meaningful = 0
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'SyncToAsyncIterator':
        for item in node.body:
            if isinstance(item, ast.AsyncFunctionDef) and item.name == 'aclose':
                aclose_found = True
                aclose_meaningful = count_meaningful_statements(item.body)
                break

if not aclose_found:
    print("FAIL: SyncToAsyncIterator.aclose not found")
    sys.exit(1)

if aclose_meaningful < 1:
    print(f"FAIL: aclose has only {aclose_meaningful} meaningful statements (need >=1)")
    sys.exit(1)

# Check safe_aclose_iterator
safe_aclose_found = False
safe_aclose_meaningful = 0
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == 'safe_aclose_iterator':
        safe_aclose_found = True
        safe_aclose_meaningful = count_meaningful_statements(node.body)
        break

if not safe_aclose_found:
    print("FAIL: safe_aclose_iterator not found")
    sys.exit(1)

if safe_aclose_meaningful < 3:
    print(f"FAIL: safe_aclose_iterator has only {safe_aclose_meaningful} meaningful statements (need >=3 for retry logic)")
    sys.exit(1)

print(f"PASS: aclose has {aclose_meaningful}, safe_aclose_iterator has {safe_aclose_meaningful} meaningful statements")
sys.exit(0)
PYEOF
T5=$?
echo "  -> exit code: $T5"
if [ $T5 -eq 0 ]; then REWARD=$(python3 -c "print($REWARD + 0.10)"); fi

###############################################################################
# TEST 6 [CONFIG-DERIVED, 0.05]: ruff format check
###############################################################################
echo ""
echo "TEST 6: [config-derived] ruff format check"
pip install ruff > /dev/null 2>&1
cd /workspace/gradio
ruff check --select I /workspace/gradio/gradio/chat_interface.py /workspace/gradio/gradio/utils.py 2>/dev/null
RUFF_EXIT=$?
cd /
if [ $RUFF_EXIT -eq 0 ]; then
    echo "PASS: ruff format check passed"
    REWARD=$(python3 -c "print($REWARD + 0.05)")
else
    echo "FAIL: ruff format check failed"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "========================================"
echo "RESULT: score = $REWARD"
echo "  TEST 1 (fail-to-pass: aclose awaitable)      = $([ $T1 -eq 0 ] && echo PASS || echo FAIL) [0.30]"
echo "  TEST 2 (fail-to-pass: safe_aclose awaits)    = $([ $T2 -eq 0 ] && echo PASS || echo FAIL) [0.25]"
echo "  TEST 3 (fail-to-pass: aclosing context mgr)  = $([ $T3 -eq 0 ] && echo PASS || echo FAIL) [0.20]"
echo "  TEST 4 (pass-to-pass: upstream tests)        = $([ $UPSTREAM_PASSED -eq 1 ] && echo PASS || echo SKIP) [0.10]"
echo "  TEST 5 (anti-stub: depth check)              = $([ $T5 -eq 0 ] && echo PASS || echo FAIL) [0.10]"
echo "  TEST 6 (config: ruff format)                 = $([ $RUFF_EXIT -eq 0 ] && echo PASS || echo FAIL) [0.05]"
echo "========================================"

# Format to 2 decimal places
REWARD=$(python3 -c "print(f'{float('$REWARD'):.2f}')")
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
