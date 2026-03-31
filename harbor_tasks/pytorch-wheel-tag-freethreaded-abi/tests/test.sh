#!/usr/bin/env bash
set -uo pipefail

SCORE=0
TOTAL=0
DETAILS=""

add_result() {
    local weight="$1" pass="$2" desc="$3"
    TOTAL=$(python3 -c "print(round($TOTAL + $weight, 4))")
    if [ "$pass" = "1" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
        DETAILS="${DETAILS}PASS ($weight): $desc\n"
    else
        DETAILS="${DETAILS}FAIL ($weight): $desc\n"
    fi
}

SRC="/workspace/.ci/pytorch/smoke_test/check_wheel_tags.py"

# ── GATE: Syntax check ──
# [pr_diff] (0.00): File must parse without syntax errors
python3 -c "
import ast, sys
try:
    ast.parse(open('$SRC').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "GATE FAILED: syntax error"
    exit 0
fi

# ── Fail-to-pass: Free-threaded Python ABI detection (0.40) ──
# [pr_diff] (0.40): Free-threaded Python (no GIL) should produce 't' ABI suffix
RESULT=$(python3 -c "
import sys, os, unittest.mock as mock

# Simulate free-threaded Python: abiflags='', _is_gil_enabled returns False
with mock.patch.object(sys, 'abiflags', ''):
    orig = getattr(sys, '_is_gil_enabled', None)
    sys._is_gil_enabled = lambda: False
    try:
        exec_globals = {}
        exec(open('$SRC').read(), exec_globals)

        import tempfile, zipfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            major, minor = sys.version_info.major, sys.version_info.minor
            # Create wheel WITH the 't' ABI tag (correct for free-threaded)
            whl_name = f'torch-2.7.0-cp{major}{minor}t-cp{major}{minor}t-linux_x86_64.whl'
            whl_path = Path(tmpdir) / whl_name
            with zipfile.ZipFile(whl_path, 'w') as zf:
                zf.writestr('torch-2.7.0.dist-info/WHEEL',
                            f'Tag: cp{major}{minor}t-cp{major}{minor}t-linux_x86_64')

            os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = tmpdir
            os.environ['TARGET_OS'] = 'linux'
            try:
                exec_globals['check_wheel_platform_tag']()
                print('PASS')
            except RuntimeError as e:
                if 'ABI' in str(e) or 'tag' in str(e).lower():
                    print('FAIL_ABI')
                else:
                    print(f'FAIL_OTHER: {e}')
    finally:
        if orig is not None:
            sys._is_gil_enabled = orig
        elif hasattr(sys, '_is_gil_enabled'):
            del sys._is_gil_enabled
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.40 1 "Free-threaded Python ABI tag detection"
else
    add_result 0.40 0 "Free-threaded Python ABI tag detection: $RESULT"
fi

# ── Fail-to-pass: Inverse — wrong tag rejected under free-threaded (0.15) ──
# [pr_diff] (0.15): A wheel WITHOUT 't' suffix must FAIL under free-threaded Python
RESULT=$(python3 -c "
import sys, os, unittest.mock as mock

with mock.patch.object(sys, 'abiflags', ''):
    orig = getattr(sys, '_is_gil_enabled', None)
    sys._is_gil_enabled = lambda: False
    try:
        exec_globals = {}
        exec(open('$SRC').read(), exec_globals)

        import tempfile, zipfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            major, minor = sys.version_info.major, sys.version_info.minor
            # Create wheel WITHOUT 't' tag (wrong for free-threaded)
            whl_name = f'torch-2.7.0-cp{major}{minor}-cp{major}{minor}-linux_x86_64.whl'
            whl_path = Path(tmpdir) / whl_name
            with zipfile.ZipFile(whl_path, 'w') as zf:
                zf.writestr('torch-2.7.0.dist-info/WHEEL',
                            f'Tag: cp{major}{minor}-cp{major}{minor}-linux_x86_64')

            os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = tmpdir
            os.environ['TARGET_OS'] = 'linux'
            try:
                exec_globals['check_wheel_platform_tag']()
                print('WRONGLY_PASSED')
            except RuntimeError:
                print('CORRECTLY_REJECTED')
            except Exception as e:
                print(f'OTHER_ERROR: {e}')
    finally:
        if orig is not None:
            sys._is_gil_enabled = orig
        elif hasattr(sys, '_is_gil_enabled'):
            del sys._is_gil_enabled
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)
" 2>&1)
if echo "$RESULT" | grep -q "CORRECTLY_REJECTED"; then
    add_result 0.15 1 "Wrong tag rejected under free-threaded Python"
else
    add_result 0.15 0 "Wrong tag not rejected under free-threaded Python: $RESULT"
fi

# ── Fail-to-pass: check_mac_wheel_minos Mode 2 — doesn't silently skip (0.10) ──
# [pr_diff] (0.10): When PYTORCH_FINAL_PACKAGE_DIR is unset, check_mac_wheel_minos should
#   attempt installed-package verification (Mode 2), not silently return.
RESULT=$(python3 -c "
import os, io, contextlib

os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
os.environ['TARGET_OS'] = 'darwin'

exec_globals = {}
exec(open('$SRC').read(), exec_globals)

fn = exec_globals.get('check_mac_wheel_minos')
if fn is None:
    print('NO_FUNCTION')
else:
    f = io.StringIO()
    try:
        with contextlib.redirect_stdout(f):
            fn()
        output = f.getvalue().lower()
        # Buggy: silently prints skip/skipping and returns
        if 'skip' in output:
            print('BUGGY_SKIP')
        else:
            print('MODE2_OK')
    except Exception:
        # Fixed code attempts Mode 2 but may fail (torch not installed) — that's fine
        print('MODE2_ATTEMPTED')
    finally:
        os.environ.pop('TARGET_OS', None)
" 2>&1)
if echo "$RESULT" | grep -q "MODE2"; then
    add_result 0.10 1 "check_mac_wheel_minos attempts Mode 2 when no wheel dir"
else
    add_result 0.10 0 "check_mac_wheel_minos silently skips: $RESULT"
fi

# ── Pass-to-pass: Normal wheel tag validation still works (0.10) ──
# [pr_diff] (0.10): Standard (non-free-threaded) wheels must still validate
RESULT=$(python3 -c "
import sys, os, tempfile, zipfile
from pathlib import Path

exec_globals = {}
exec(open('$SRC').read(), exec_globals)

major, minor = sys.version_info.major, sys.version_info.minor
abiflags = getattr(sys, 'abiflags', '')
abi = f'cp{major}{minor}{abiflags}'

with tempfile.TemporaryDirectory() as tmpdir:
    whl_name = f'torch-2.7.0-cp{major}{minor}-{abi}-linux_x86_64.whl'
    whl_path = Path(tmpdir) / whl_name
    with zipfile.ZipFile(whl_path, 'w') as zf:
        zf.writestr('torch-2.7.0.dist-info/WHEEL', f'Tag: cp{major}{minor}-{abi}-linux_x86_64')

    os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = tmpdir
    os.environ['TARGET_OS'] = 'linux'
    try:
        exec_globals['check_wheel_platform_tag']()
        print('PASS')
    except Exception as e:
        print(f'FAIL: {e}')
    finally:
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)
" 2>&1)
if echo "$RESULT" | grep -q "PASS"; then
    add_result 0.10 1 "Standard wheel tag validation still works"
else
    add_result 0.10 0 "Standard wheel tag validation broken: $RESULT"
fi

# ── Pass-to-pass: _extract_wheel_tags still works (0.05) ──
# [pr_diff] (0.05): Wheel tag extraction from zip unchanged
RESULT=$(python3 -c "
import tempfile, zipfile
from pathlib import Path

exec_globals = {}
exec(open('$SRC').read(), exec_globals)

with tempfile.TemporaryDirectory() as tmpdir:
    whl_path = Path(tmpdir) / 'test.whl'
    with zipfile.ZipFile(whl_path, 'w') as zf:
        zf.writestr('pkg-1.0.dist-info/WHEEL', 'Tag: cp312-cp312-linux_x86_64\nTag: cp312-cp312-manylinux1_x86_64')
    tags = exec_globals['_extract_wheel_tags'](whl_path)
    assert len(tags) == 2, f'Expected 2 tags, got {len(tags)}'
    assert tags[0] == 'cp312-cp312-linux_x86_64'
    print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "PASS"; then
    add_result 0.05 1 "_extract_wheel_tags still works"
else
    add_result 0.05 0 "_extract_wheel_tags broken: $RESULT"
fi

# ── Structural: Dead code removal (0.05) ──
# [pr_diff] (0.05): No unreachable continue after raise in tag validation loop
# WHY AST: detecting unreachable code is not callable behavior
RESULT=$(python3 -c "
import ast

with open('$SRC') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.For, ast.While)):
        body = node.body
        for i in range(len(body) - 1):
            if isinstance(body[i], ast.Raise) and isinstance(body[i+1], ast.Continue):
                print('DEAD_CODE_FOUND')
                exit(0)
print('CLEAN')
" 2>&1)
if [ "$RESULT" = "CLEAN" ]; then
    add_result 0.05 1 "Dead continue-after-raise removed"
else
    add_result 0.05 0 "Dead continue-after-raise still present"
fi

# ── Anti-stub: key functions are non-trivial (0.05) ──
# [pr_diff] (0.05): Core functions must have real implementations, not stubs
RESULT=$(python3 -c "
import ast

with open('$SRC') as f:
    tree = ast.parse(f.read())

REQUIRED = {'check_wheel_platform_tag', 'check_mac_wheel_minos', '_extract_wheel_tags'}
found = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in REQUIRED:
        # Count non-docstring, non-pass statements
        stmts = node.body
        if stmts and isinstance(stmts[0], ast.Expr) and isinstance(stmts[0].value, (ast.Constant, ast.Str)):
            stmts = stmts[1:]  # skip docstring
        real = [s for s in stmts if not isinstance(s, ast.Pass)]
        found[node.name] = len(real)

missing = REQUIRED - set(found.keys())
if missing:
    print(f'MISSING: {missing}')
    exit(1)
stubs = {k: v for k, v in found.items() if v < 3}
if stubs:
    print(f'STUB: {stubs}')
    exit(1)
print('OK')
" 2>&1)
if echo "$RESULT" | grep -q "^OK"; then
    add_result 0.05 1 "Core functions are non-trivial"
else
    add_result 0.05 0 "Stubbed or missing functions: $RESULT"
fi

# ── Config-derived: Minimize comments (0.05) ──
# [agent_config] (0.05): "Minimize comments; be concise" — CLAUDE.md:55
RESULT=$(python3 -c "
with open('$SRC') as f:
    lines = f.readlines()

comment_count = sum(1 for line in lines if line.strip().startswith('#'))
if comment_count > 30:
    print(f'TOO_MANY: {comment_count}')
else:
    print('OK')
" 2>&1)
if echo "$RESULT" | grep -q "^OK"; then
    add_result 0.05 1 "Comments are concise"
else
    add_result 0.05 0 "Too many comments: $RESULT"
fi

# ── Regression: no new syntax or import errors in helpers (0.05) ──
# [pr_diff] (0.05): All top-level callables must be importable without error
RESULT=$(python3 -c "
exec_globals = {}
try:
    exec(open('$SRC').read(), exec_globals)
except Exception as e:
    print(f'IMPORT_ERROR: {e}')
    exit(1)

# Verify core public functions exist and are callable
for name in ['check_wheel_platform_tag', 'check_mac_wheel_minos', '_extract_wheel_tags']:
    fn = exec_globals.get(name)
    if fn is None or not callable(fn):
        print(f'MISSING: {name}')
        exit(1)
print('OK')
" 2>&1)
if echo "$RESULT" | grep -q "^OK"; then
    add_result 0.05 1 "All core functions importable"
else
    add_result 0.05 0 "Import/callable error: $RESULT"
fi

# ── Output results ──
echo ""
echo "=== RESULTS ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"

echo "$SCORE" > /logs/verifier/reward.txt

python3 -c "
import json
data = {
    'reward': $SCORE,
    'behavioral': round(min($SCORE, 0.85), 4),
    'regression': round(min(max($SCORE - 0.85, 0), 0.10), 4),
    'config': round(min(max($SCORE - 0.95, 0), 0.05), 4)
}
json.dump(data, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
