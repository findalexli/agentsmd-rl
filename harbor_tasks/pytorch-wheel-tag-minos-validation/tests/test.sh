#!/usr/bin/env bash
set +e
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
SMOKE="/workspace/.ci/pytorch/smoke_test/smoke_test.py"

# ── GATE: Syntax check ──
# [pr_diff] (0.00): New module must parse without syntax errors
python3 -c "
import ast, sys
try:
    ast.parse(open('$SRC').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
" 2>&1
if [ $? -ne 0 ]; then
    echo "0.0" > /logs/verifier/reward.txt
    echo "GATE FAILED: syntax error in check_wheel_tags.py"
    exit 0
fi

# ── F2P-1 (0.25): _extract_wheel_tags extracts correct tags from mock wheel ──
# [pr_diff] (0.25): Function reads Tag: lines from WHEEL metadata inside a zip archive
RESULT=$(python3 -c "
import sys, tempfile, zipfile
from pathlib import Path
sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test')

with tempfile.TemporaryDirectory() as td:
    whl = Path(td) / 'torch-2.12.0-cp312-cp312-linux_x86_64.whl'
    with zipfile.ZipFile(whl, 'w') as zf:
        zf.writestr('torch-2.12.0.dist-info/WHEEL', (
            'Wheel-Version: 1.0\n'
            'Generator: bdist_wheel\n'
            'Root-Is-Purelib: false\n'
            'Tag: cp312-cp312-linux_x86_64\n'
            'Tag: cp312-cp312-manylinux_2_17_x86_64\n'
        ))
    from check_wheel_tags import _extract_wheel_tags
    tags = _extract_wheel_tags(whl)
    assert isinstance(tags, (list, tuple, set)), f'Expected iterable, got {type(tags)}'
    tags = list(tags)
    assert 'cp312-cp312-linux_x86_64' in tags, f'Missing expected tag, got {tags}'
    assert 'cp312-cp312-manylinux_2_17_x86_64' in tags, f'Missing second tag, got {tags}'
    assert len(tags) == 2, f'Expected 2 tags, got {len(tags)}: {tags}'
    print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.25 1 "Extract tags from mock .whl file (multiple tags)"
else
    add_result 0.25 0 "Extract tags from mock .whl file: $RESULT"
fi

# ── F2P-2 (0.30): check_wheel_platform_tag accepts valid AND rejects invalid ──
# [pr_diff] (0.30): Combined test — both behaviors must work; a no-op function fails
RESULT=$(python3 -c "
import sys, os, tempfile, zipfile, importlib
from pathlib import Path
sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test')

errors = []

# Part A: Valid wheel with matching platform should NOT raise
with tempfile.TemporaryDirectory() as td:
    whl = Path(td) / 'torch-2.12.0-cp312-cp312-linux_x86_64.whl'
    with zipfile.ZipFile(whl, 'w') as zf:
        zf.writestr('torch-2.12.0.dist-info/WHEEL', 'Tag: cp312-cp312-linux_x86_64\n')
    os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = td
    os.environ['TARGET_OS'] = 'linux'
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    try:
        check_wheel_tags.check_wheel_platform_tag()
    except RuntimeError as e:
        errors.append(f'Part A: valid wheel raised RuntimeError: {e}')
    finally:
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)

# Part B: Wrong platform should raise RuntimeError
with tempfile.TemporaryDirectory() as td:
    whl = Path(td) / 'torch-2.12.0-cp312-cp312-win_amd64.whl'
    with zipfile.ZipFile(whl, 'w') as zf:
        zf.writestr('torch-2.12.0.dist-info/WHEEL', 'Tag: cp312-cp312-win_amd64\n')
    os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = td
    os.environ['TARGET_OS'] = 'linux'
    importlib.reload(check_wheel_tags)
    try:
        check_wheel_tags.check_wheel_platform_tag()
        errors.append('Part B: no exception raised for platform mismatch (win_amd64 on linux)')
    except RuntimeError:
        pass  # expected
    except Exception as e:
        errors.append(f'Part B: wrong exception type {type(e).__name__}: {e}')
    finally:
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)

if errors:
    print('FAIL: ' + '; '.join(errors))
else:
    print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.30 1 "Platform tag check accepts valid, rejects invalid"
else
    add_result 0.30 0 "Platform tag accept/reject: $RESULT"
fi

# ── F2P-3 (0.10): Malformed tag (wrong number of parts) raises RuntimeError ──
# [pr_diff] (0.10): Tags with != 3 dash-separated parts must be rejected
RESULT=$(python3 -c "
import sys, os, tempfile, zipfile, importlib
from pathlib import Path
sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test')

with tempfile.TemporaryDirectory() as td:
    whl = Path(td) / 'torch-2.12.0-cp312-cp312-linux_x86_64.whl'
    with zipfile.ZipFile(whl, 'w') as zf:
        # Malformed: only 2 parts instead of 3
        zf.writestr('torch-2.12.0.dist-info/WHEEL', 'Tag: cp312-linux_x86_64\n')
    os.environ['PYTORCH_FINAL_PACKAGE_DIR'] = td
    os.environ['TARGET_OS'] = 'linux'
    import check_wheel_tags
    importlib.reload(check_wheel_tags)
    try:
        check_wheel_tags.check_wheel_platform_tag()
        print('FAIL: no exception raised for malformed tag (2 parts)')
    except RuntimeError:
        print('PASS')
    except Exception as e:
        # Accept ValueError too — both are reasonable for malformed input
        if isinstance(e, (ValueError, TypeError)):
            print('PASS')
        else:
            print(f'FAIL: unexpected exception {type(e).__name__}: {e}')
    finally:
        os.environ.pop('PYTORCH_FINAL_PACKAGE_DIR', None)
        os.environ.pop('TARGET_OS', None)
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.10 1 "Malformed tag raises error"
else
    add_result 0.10 0 "Malformed tag: $RESULT"
fi

# ── F2P-4 (0.10): EXPECTED_PLATFORM_TAGS patterns are correct and specific ──
# [pr_diff] (0.10): Patterns must match correct platforms and reject wrong ones
RESULT=$(python3 -c "
import sys, re
sys.path.insert(0, '/workspace/.ci/pytorch/smoke_test')
from check_wheel_tags import EXPECTED_PLATFORM_TAGS

required = {'linux', 'windows', 'darwin'}
# Accept 'win32' as alias for 'windows'
keys = set(EXPECTED_PLATFORM_TAGS.keys())
has_win = 'windows' in keys or 'win32' in keys
if 'linux' not in keys:
    print('FAIL: missing linux key')
    sys.exit(0)
if not has_win:
    print('FAIL: missing windows/win32 key')
    sys.exit(0)
if 'darwin' not in keys:
    print('FAIL: missing darwin key')
    sys.exit(0)

linux_pat = EXPECTED_PLATFORM_TAGS['linux']
win_key = 'windows' if 'windows' in keys else 'win32'
win_pat = EXPECTED_PLATFORM_TAGS[win_key]
darwin_pat = EXPECTED_PLATFORM_TAGS['darwin']

errors = []
# Linux must match x86_64 linux platforms
if not re.search(linux_pat, 'linux_x86_64') and not re.search(linux_pat, 'manylinux_2_17_x86_64'):
    errors.append('linux pattern rejects linux_x86_64')
# Linux must NOT match windows
if re.search(linux_pat, 'win_amd64'):
    errors.append('linux pattern accepts win_amd64 (too broad)')
# Windows must match win_amd64
if not re.search(win_pat, 'win_amd64'):
    errors.append('windows pattern rejects win_amd64')
# Windows must NOT match linux
if re.search(win_pat, 'linux_x86_64'):
    errors.append('windows pattern accepts linux_x86_64 (too broad)')
# Darwin must match macosx arm64
if not re.search(darwin_pat, 'macosx_11_0_arm64'):
    errors.append('darwin pattern rejects macosx_11_0_arm64')
# Darwin must NOT match linux
if re.search(darwin_pat, 'linux_x86_64'):
    errors.append('darwin pattern accepts linux_x86_64 (too broad)')

if errors:
    print('FAIL: ' + '; '.join(errors))
else:
    print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.10 1 "Platform patterns are correct and specific"
else
    add_result 0.10 0 "Platform patterns: $RESULT"
fi

# ── P2P (0.10): smoke_test.py structure preserved ──
# [pr_diff] (0.10): Existing smoke_test.py must still parse and have main()
RESULT=$(python3 -c "
import ast, sys
try:
    tree = ast.parse(open('$SMOKE').read())
except SyntaxError as e:
    print(f'FAIL: syntax error: {e}')
    sys.exit(0)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
if 'main' not in funcs:
    print('FAIL: main() not found in smoke_test.py')
else:
    print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.10 1 "smoke_test.py structure preserved"
else
    add_result 0.10 0 "smoke_test.py structure: $RESULT"
fi

# ── Integration (0.10): smoke_test.py imports check_wheel_tags (AST-verified) ──
# [pr_diff] (0.10): Must be a real import statement, not a comment or string
RESULT=$(python3 -c "
import ast, sys
tree = ast.parse(open('$SMOKE').read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module and 'check_wheel_tags' in node.module:
        found = True
        break
    if isinstance(node, ast.Import):
        for alias in node.names:
            if 'check_wheel_tags' in alias.name:
                found = True
                break
if found:
    print('PASS')
else:
    print('FAIL: no import of check_wheel_tags found in smoke_test.py AST')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.10 1 "smoke_test.py imports check_wheel_tags (AST-verified)"
else
    add_result 0.10 0 "smoke_test.py integration: $RESULT"
fi

# ── Anti-stub (0.05): Implementation has substance ──
# [pr_diff] (0.05): Functions must have real logic, not empty bodies
RESULT=$(python3 -c "
import ast
tree = ast.parse(open('$SRC').read())
funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
if len(funcs) < 3:
    print(f'FAIL: only {len(funcs)} functions, need >=3')
    exit(0)
for fn in funcs:
    body = fn.body
    # Skip docstring
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0].value, 'value', None), str):
        body = body[1:]
    if len(body) < 3:
        print(f'FAIL: {fn.name}() has only {len(body)} non-docstring statements, need >=3')
        exit(0)
print('PASS')
" 2>&1)
if echo "$RESULT" | grep -q "^PASS"; then
    add_result 0.05 1 "Implementation has substance (anti-stub)"
else
    add_result 0.05 0 "Anti-stub: $RESULT"
fi

# ── Report ──
echo ""
echo "=== Test Results ==="
echo -e "$DETAILS"
echo "Score: $SCORE / $TOTAL"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
