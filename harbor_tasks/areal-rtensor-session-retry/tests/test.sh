#!/usr/bin/env bash
# Test: areal-rtensor-session-retry
set +e  # Allow individual test failures without aborting

SCORE=0
OUTPUT_DIR="${OUTPUT_DIR:-/logs/verifier}"
mkdir -p "$OUTPUT_DIR"

add_score() {
    SCORE=$(python3 -c "print(round($SCORE + $1, 4))")
}

# ---------- GATE: Syntax check ----------
# [static] (0.00): Abort if modified files have syntax errors
echo "=== GATE: Syntax check ==="
python3 -c "
import py_compile, sys
for f in ['areal/infra/rpc/rtensor.py', 'areal/utils/logging.py']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'SYNTAX ERROR: {e}')
        sys.exit(1)
print('PASS: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "0.0" > "$OUTPUT_DIR/reward.txt"
    echo '{"reward": 0.0, "gate": "syntax_fail"}' > "$OUTPUT_DIR/reward.json"
    exit 0
fi

# ---------- Mock ray and bypass areal/__init__.py to avoid heavy deps ----------
MOCK_SETUP='
import sys, types, importlib

# Mock ray
ray_mock = types.ModuleType("ray")
ray_mock.ObjectRef = object
ray_mock.is_initialized = lambda: False
ray_mock.put = lambda x: x
ray_mock.get = lambda x: x
ray_mock.internal = types.ModuleType("ray.internal")
ray_mock.internal.free = lambda x: None
sys.modules["ray"] = ray_mock
sys.modules["ray.internal"] = ray_mock.internal

# Pre-populate areal package hierarchy to prevent __init__.py from importing
# the entire dependency tree (flask, controllers, etc.)
for pkg, path in [
    ("areal", "/repo/areal"),
    ("areal.infra", "/repo/areal/infra"),
    ("areal.infra.rpc", "/repo/areal/infra/rpc"),
    ("areal.infra.utils", "/repo/areal/infra/utils"),
    ("areal.utils", "/repo/areal/utils"),
]:
    m = types.ModuleType(pkg)
    m.__path__ = [path]
    m.__package__ = pkg
    sys.modules[pkg] = m

# Load only the submodules rtensor actually needs
for mod in ["areal.utils.logging", "areal.infra.utils.concurrent", "areal.infra.utils.http"]:
    sys.modules[mod] = importlib.import_module(mod)
'

# ---------- Test 1 [pr_diff] (0.30): _create_session configures timeout, buffer, connector ----------
echo ""
echo "=== Test 1: _create_session configuration ==="
python3 -c "
$MOCK_SETUP
import asyncio, aiohttp

async def test():
    from areal.infra.rpc.rtensor import HttpRTensorBackend
    from areal.infra.utils.http import DEFAULT_REQUEST_TIMEOUT

    backend = HttpRTensorBackend()
    session = backend._create_session()
    try:
        # Check timeout matches DEFAULT_REQUEST_TIMEOUT (3600)
        assert session.timeout.total == DEFAULT_REQUEST_TIMEOUT, \
            f'timeout.total={session.timeout.total}, expected {DEFAULT_REQUEST_TIMEOUT}'

        # Check read buffer >= 10MB
        bufsize = session._read_bufsize
        assert bufsize >= 10 * 1024 * 1024, \
            f'read_bufsize={bufsize}, expected >= {10*1024*1024}'

        # Check connector is TCPConnector
        assert isinstance(session.connector, aiohttp.TCPConnector), \
            f'connector type={type(session.connector).__name__}, expected TCPConnector'

        print('PASS')
    finally:
        await session.close()

asyncio.run(test())
" && { echo "  PASS (0.30)"; add_score 0.30; } || echo "  FAIL"

# ---------- Test 2 [pr_diff] (0.30): _fetch_tensor actually retries (timing verification) ----------
echo ""
echo "=== Test 2: _fetch_tensor retry behavior (timing verification) ==="
python3 -c "
$MOCK_SETUP
import asyncio, time, aiohttp

async def test():
    from areal.infra.rpc.rtensor import HttpRTensorBackend

    backend = HttpRTensorBackend()
    session = backend._create_session()
    try:
        delay = 0.08

        # With max_retries=1: should fail quickly (single attempt, no delay)
        t0 = time.monotonic()
        try:
            await backend._fetch_tensor(
                session, 'fake-shard', '127.0.0.1:1',
                max_retries=1, retry_delay=delay
            )
        except (RuntimeError, Exception):
            pass
        t1_elapsed = time.monotonic() - t0

        # With max_retries=4: should take >= 3 * delay (3 retry waits)
        t0 = time.monotonic()
        try:
            await backend._fetch_tensor(
                session, 'fake-shard', '127.0.0.1:1',
                max_retries=4, retry_delay=delay
            )
        except (RuntimeError, Exception):
            pass
        t4_elapsed = time.monotonic() - t0

        # A stub that immediately raises would take ~0s for both.
        # Real retry logic with delays: 4 retries needs >= 3*delay sleep.
        min_expected = 3 * delay * 0.7  # 70% margin for timing jitter
        assert t4_elapsed >= min_expected, \
            f'4-retry elapsed={t4_elapsed:.3f}s, expected >= {min_expected:.3f}s — no real retry delays?'

        # 4 retries must be noticeably slower than 1 retry
        assert t4_elapsed > t1_elapsed + 2 * delay * 0.5, \
            f'4-retry ({t4_elapsed:.3f}s) not meaningfully slower than 1-retry ({t1_elapsed:.3f}s)'

        print('PASS')
    finally:
        await session.close()

asyncio.run(test())
" && { echo "  PASS (0.30)"; add_score 0.30; } || echo "  FAIL"

# ---------- Test 3 [pr_diff] (0.10): _fetch_tensor raises informative error after exhausting retries ----------
echo ""
echo "=== Test 3: _fetch_tensor error reporting ==="
python3 -c "
$MOCK_SETUP
import asyncio, aiohttp

async def test():
    from areal.infra.rpc.rtensor import HttpRTensorBackend

    backend = HttpRTensorBackend()
    session = backend._create_session()
    try:
        # Should raise RuntimeError after exhausting retries
        try:
            await backend._fetch_tensor(
                session, 'fake-shard', '127.0.0.1:1',
                max_retries=2, retry_delay=0.01
            )
            raise AssertionError('Should have raised an error')
        except RuntimeError as e:
            msg = str(e)
            # Must mention the number of attempts (2)
            assert '2' in msg, f'Error should mention attempt count 2: {e}'
            # Must include some error context (not just a bare count)
            lower = msg.lower()
            assert any(w in lower for w in ['error', 'fail', 'attempt', 'retry']), \
                f'Error should include failure context: {e}'
            print(f'Error message OK: {msg[:120]}')

        print('PASS')
    finally:
        await session.close()

asyncio.run(test())
" && { echo "  PASS (0.10)"; add_score 0.10; } || echo "  FAIL"

# ---------- Test 4 [repo_tests] (0.10): fetch([]) returns empty list (pass-to-pass) ----------
echo ""
echo "=== Test 4: fetch([]) returns empty list ==="
python3 -c "
$MOCK_SETUP
from areal.infra.rpc.rtensor import HttpRTensorBackend

backend = HttpRTensorBackend()
result = backend.fetch([])
assert result == [], f'Expected [], got {result}'
print('PASS')
" && { echo "  PASS (0.10)"; add_score 0.10; } || echo "  FAIL"

# ---------- Test 5 [pr_diff] (0.05): Anti-stub — _create_session returns a real session ----------
echo ""
echo "=== Test 5: Anti-stub — _create_session is functional ==="
python3 -c "
$MOCK_SETUP
import asyncio, aiohttp

async def test():
    from areal.infra.rpc.rtensor import HttpRTensorBackend

    backend = HttpRTensorBackend()
    session = backend._create_session()
    try:
        # Must return an actual ClientSession, not a stub
        assert isinstance(session, aiohttp.ClientSession), \
            f'Expected ClientSession, got {type(session)}'
        # Must have a non-default timeout (default aiohttp is 300)
        assert session.timeout.total != 300, \
            'Timeout is still default (300) — session not properly configured'
        print('PASS')
    finally:
        await session.close()

asyncio.run(test())
" && { echo "  PASS (0.05)"; add_score 0.05; } || echo "  FAIL"

# ---------- Test 6 [agent_config] (0.05): No wildcard imports ----------
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ 9639749e
echo ""
echo "=== Test 6: No wildcard imports ==="
if grep -rn 'from .* import \*' areal/infra/rpc/rtensor.py areal/utils/logging.py 2>/dev/null; then
    echo "  FAIL: wildcard import found"
else
    echo "  PASS (0.05)"
    add_score 0.05
fi

# ---------- Test 7 [agent_config] (0.05): Logger registered in color map ----------
# [agent_config] (0.05): "Register new loggers with color in areal/utils/logging.py" — AGENTS.md:89-90 @ 9639749e
echo ""
echo "=== Test 7: HttpRTensor logger registered in color map ==="
if grep -q '"HttpRTensor"' areal/utils/logging.py 2>/dev/null; then
    echo "  PASS (0.05)"
    add_score 0.05
else
    echo "  FAIL: HttpRTensor not registered in logging.py color map"
fi

# ---------- Test 8 [pr_diff] (0.05): Module has a logger ----------
echo ""
echo "=== Test 8: Module-level logger exists ==="
python3 -c "
$MOCK_SETUP
import logging
import areal.infra.rpc.rtensor as mod

# Check that the module has a logger instance (any name is fine)
found = False
for name, obj in vars(mod).items():
    if isinstance(obj, logging.Logger):
        found = True
        print(f'Found logger: {obj.name}')
        break
assert found, 'No module-level Logger found in rtensor module'
print('PASS')
" && { echo "  PASS (0.05)"; add_score 0.05; } || echo "  FAIL"

# ---------- Final score ----------
echo ""
echo "=== Final Score: $SCORE ==="
echo "$SCORE" > "$OUTPUT_DIR/reward.txt"

python3 -c "
import json
score = float('$SCORE')
behavioral = round(min(score, 0.90), 4)
config = round(min(0.10, max(0, score - 0.90)), 4)
print(json.dumps({
    'reward': score,
    'behavioral': behavioral,
    'config': config
}))
" > "$OUTPUT_DIR/reward.json" 2>/dev/null || true

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
