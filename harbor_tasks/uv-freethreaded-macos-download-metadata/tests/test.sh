#!/usr/bin/env bash
set -uo pipefail

TOTAL=0.0
SCORE=0.0

add() { SCORE=$(python3 -c "print($SCORE + $1)"); }
total() { TOTAL=$(python3 -c "print($TOTAL + $1)"); }

SCRIPT="crates/uv-python/fetch-download-metadata.py"

# -------------------------------------------------------------------
# GATE: syntax check — abort on failure
# -------------------------------------------------------------------
# [pr_diff] (0.00): Script must be valid Python
python3 -c "
import ast, sys
try:
    ast.parse(open('$SCRIPT').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
print('GATE PASS: syntax OK')
"
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0,"style_rubric":0.0}' > /logs/verifier/reward.json
    exit 0
fi

# -------------------------------------------------------------------
# BEHAVIORAL: Fail-to-pass tests (0.70 total)
# -------------------------------------------------------------------

# [pr_diff] (0.30): Freethreaded macOS platform suffix is stripped and promoted to build option
total 0.30
python3 -c "
import sys, os, importlib.util
sys.path.insert(0, '.')

# Load the script as a module
spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)

# We need httpx available or mock it minimally
try:
    import httpx
except ImportError:
    # Create a minimal mock
    import types
    httpx = types.ModuleType('httpx')
    class _Client:
        pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec.loader.exec_module(mod)

# Create a CPythonFinder instance with a dummy client
finder = mod.CPythonFinder(client=None)

# Test artifact: freethreaded macOS aarch64
artifact = {
    'url': 'https://example.com/cpython-3.15.0a7%2B20260320-aarch64-apple-darwin-freethreaded-install_only_stripped.tar.gz',
    'sha256': 'abc123',
    'platform': 'aarch64-apple-darwin-freethreaded',
    'variant': 'install_only_stripped',
}
version = mod.Version(3, 15, 0, 'a7')
result = finder._parse_ndjson_artifact(version, 20260320, artifact)

if result is None:
    print('FAIL: _parse_ndjson_artifact returned None for freethreaded macOS artifact')
    sys.exit(1)

if 'freethreaded' not in result.build_options:
    print(f'FAIL: build_options={result.build_options}, expected \"freethreaded\" in list')
    sys.exit(1)

print('PASS: freethreaded extracted into build_options')
" 2>&1
if [ $? -eq 0 ]; then add 0.30; fi

# [pr_diff] (0.20): Variant is correctly set to FREETHREADED
total 0.20
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)
artifact = {
    'url': 'https://example.com/cpython-3.14.3%2B20260320-x86_64-apple-darwin-freethreaded-install_only_stripped.tar.gz',
    'sha256': 'def456',
    'platform': 'x86_64-apple-darwin-freethreaded',
    'variant': 'install_only_stripped',
}
result = finder._parse_ndjson_artifact(mod.Version(3, 14, 3, ''), 20260320, artifact)
if result is None:
    print('FAIL: returned None')
    sys.exit(1)

if result.variant != mod.Variant.FREETHREADED:
    print(f'FAIL: variant={result.variant}, expected Variant.FREETHREADED')
    sys.exit(1)

print('PASS: variant is FREETHREADED')
" 2>&1
if [ $? -eq 0 ]; then add 0.20; fi

# [pr_diff] (0.20): Platform triple is clean (no -freethreaded suffix leaking into triple)
total 0.20
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)

# Parse both a normal and a freethreaded artifact — triples should match
normal_artifact = {
    'url': 'https://example.com/cpython-3.15.0a7-aarch64-apple-darwin-install_only_stripped.tar.gz',
    'sha256': 'aaa',
    'platform': 'aarch64-apple-darwin',
    'variant': 'install_only_stripped',
}
ft_artifact = {
    'url': 'https://example.com/cpython-3.15.0a7-aarch64-apple-darwin-freethreaded-install_only_stripped.tar.gz',
    'sha256': 'bbb',
    'platform': 'aarch64-apple-darwin-freethreaded',
    'variant': 'install_only_stripped',
}
v = mod.Version(3, 15, 0, 'a7')
normal = finder._parse_ndjson_artifact(v, 20260320, normal_artifact)
ft = finder._parse_ndjson_artifact(v, 20260320, ft_artifact)

if normal is None or ft is None:
    print('FAIL: one of the artifacts returned None')
    sys.exit(1)

if normal.triple != ft.triple:
    print(f'FAIL: triples differ: normal={normal.triple} vs freethreaded={ft.triple}')
    sys.exit(1)

print(f'PASS: triples match: {normal.triple}')
" 2>&1
if [ $? -eq 0 ]; then add 0.20; fi

# -------------------------------------------------------------------
# REGRESSION: Pass-to-pass (0.15 total)
# -------------------------------------------------------------------

# [pr_diff] (0.10): Debug suffix still stripped correctly (existing behavior)
total 0.10
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)
artifact = {
    'url': 'https://example.com/cpython-3.14.3-aarch64-apple-darwin-debug-install_only.tar.gz',
    'sha256': 'ccc',
    'platform': 'aarch64-apple-darwin-debug',
    'variant': 'install_only',
}
result = finder._parse_ndjson_artifact(mod.Version(3, 14, 3, ''), 20260320, artifact)
if result is None:
    print('FAIL: returned None for debug artifact')
    sys.exit(1)
if 'debug' not in result.build_options:
    print(f'FAIL: build_options={result.build_options}, expected debug')
    sys.exit(1)
if result.variant != mod.Variant.DEBUG:
    print(f'FAIL: variant={result.variant}, expected DEBUG')
    sys.exit(1)
print('PASS: debug suffix handled correctly')
" 2>&1
if [ $? -eq 0 ]; then add 0.10; fi

# [pr_diff] (0.05): Non-macOS platform strings are unaffected
total 0.05
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)
artifact = {
    'url': 'https://example.com/cpython-3.14.3-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz',
    'sha256': 'ddd',
    'platform': 'x86_64-unknown-linux-gnu',
    'variant': 'install_only_stripped',
}
result = finder._parse_ndjson_artifact(mod.Version(3, 14, 3, ''), 20260320, artifact)
if result is None:
    print('FAIL: returned None for linux artifact')
    sys.exit(1)
if result.triple.platform != 'linux':
    print(f'FAIL: platform={result.triple.platform}, expected linux')
    sys.exit(1)
if result.variant is not None:
    print(f'FAIL: variant={result.variant}, expected None for non-freethreaded linux')
    sys.exit(1)
print('PASS: linux artifact unaffected')
" 2>&1
if [ $? -eq 0 ]; then add 0.05; fi

# -------------------------------------------------------------------
# CONFIG-DERIVED: Rules from CLAUDE.md (0.15 total)
# -------------------------------------------------------------------

# [agent_config] (0.05): "AVOID using panic!, unreachable!, .unwrap(), unsafe code" — CLAUDE.md:7
# Applied to Python: no bare raise without context, no sys.exit in library code
# We check that the parsing method doesn't crash on edge cases
total 0.05
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)

# Edge case: platform that ends with suffix but has no triple match
artifact = {
    'url': 'https://example.com/test.tar.gz',
    'sha256': 'eee',
    'platform': 'unknown-platform-freethreaded',
    'variant': 'install_only_stripped',
}
# Should return None gracefully, not crash
result = finder._parse_ndjson_artifact(mod.Version(3, 14, 3, ''), 20260320, artifact)
# We accept None (unrecognized triple) — the point is no crash
print('PASS: no crash on unknown platform with suffix')
" 2>&1
if [ $? -eq 0 ]; then add 0.05; fi

# [agent_config] (0.10): "ALWAYS attempt to add a test case for changed behavior" — CLAUDE.md:2
# Verify the changed code path is actually reachable and tested above by confirming
# the freethreaded+debug combined variant works (tests both suffixes interact correctly)
total 0.10
python3 -c "
import sys, importlib.util
sys.path.insert(0, '.')

try:
    import httpx
except ImportError:
    import types
    httpx = types.ModuleType('httpx')
    class _Client: pass
    httpx.AsyncClient = _Client
    sys.modules['httpx'] = httpx

spec = importlib.util.spec_from_file_location('fetch_dm', '$SCRIPT')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

finder = mod.CPythonFinder(client=None)

# Variant string encodes freethreaded via variant, platform has debug suffix
artifact = {
    'url': 'https://example.com/cpython-3.14.3-aarch64-apple-darwin-debug-freethreaded+debug+full.tar.zst',
    'sha256': 'fff',
    'platform': 'aarch64-apple-darwin-debug',
    'variant': 'freethreaded+debug+full',
}
result = finder._parse_ndjson_artifact(mod.Version(3, 14, 3, ''), 20260320, artifact)
if result is None:
    print('FAIL: returned None')
    sys.exit(1)
if 'debug' not in result.build_options:
    print(f'FAIL: debug not in build_options={result.build_options}')
    sys.exit(1)
if 'freethreaded' not in result.build_options:
    print(f'FAIL: freethreaded not in build_options={result.build_options}')
    sys.exit(1)
if result.variant != mod.Variant.FREETHREADED_DEBUG:
    print(f'FAIL: variant={result.variant}, expected FREETHREADED_DEBUG')
    sys.exit(1)
print('PASS: combined debug+freethreaded variant works')
" 2>&1
if [ $? -eq 0 ]; then add 0.10; fi

# -------------------------------------------------------------------
# Compute final reward
# -------------------------------------------------------------------
REWARD=$(python3 -c "print(round($SCORE, 2))")
echo "$REWARD" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "print(min($SCORE, 0.70))")
REGRESSION=$(python3 -c "b=$SCORE-0.70; print(round(max(0, min(b, 0.15)), 2))")
CONFIG=$(python3 -c "b=$SCORE-0.85; print(round(max(0, min(b, 0.15)), 2))")

echo "{\"reward\":$REWARD,\"behavioral\":$BEHAVIORAL,\"regression\":$REGRESSION,\"config\":$CONFIG,\"style_rubric\":0.0}" > /logs/verifier/reward.json

echo "=== RESULTS ==="
echo "Score: $SCORE / $TOTAL"
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
