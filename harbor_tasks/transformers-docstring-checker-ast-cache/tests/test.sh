#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0

log_check() {
    local name="$1" weight="$2" result="$3" tag="$4"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$result" = "pass" ]; then
        SCORE=$(python3 -c "print($SCORE + $weight)")
        echo "  PASS ($weight) $tag: $name"
    else
        echo "  FAIL ($weight) $tag: $name"
    fi
}

cd /workspace/transformers

echo "=== GATE: Syntax check ==="
# [pr_diff] (gate): Modified files must parse without syntax errors
if python3 -c "
import ast, sys
for f in ['utils/check_docstrings.py']:
    try:
        with open(f) as fh:
            ast.parse(fh.read(), filename=f)
    except SyntaxError as e:
        print(f'Syntax error in {f}: {e}', file=sys.stderr)
        sys.exit(1)
print('Syntax OK')
"; then
    echo "  GATE PASSED"
else
    echo "  GATE FAILED — aborting"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

echo ""
echo "=== Fail-to-pass behavioral tests ==="

# --- T1: _get_auto_docstring_names detects decorated names ---
# [pr_diff] (0.20): New function correctly identifies @auto_docstring decorated names
T1=$(python3 -c "
import sys, os, tempfile, textwrap
sys.path.insert(0, 'utils')
from check_docstrings import _get_auto_docstring_names

src = textwrap.dedent('''
@auto_docstring
class Foo:
    pass

class Bar:
    pass

@auto_docstring()
class Baz:
    pass

@auto_docstring
def qux():
    pass

@other_decorator
class NotThis:
    pass
''').strip()

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(src)
    path = f.name

try:
    names = _get_auto_docstring_names(path)
    assert isinstance(names, set), f'Expected set, got {type(names)}'
    assert 'Foo' in names, f'Foo missing from {names}'
    assert 'Baz' in names, f'Baz missing from {names}'
    assert 'qux' in names, f'qux missing from {names}'
    assert 'Bar' not in names, f'Bar should not be in {names}'
    assert 'NotThis' not in names, f'NotThis should not be in {names}'
    assert len(names) == 3, f'Expected 3 names, got {len(names)}: {names}'
    print('OK')
finally:
    os.unlink(path)
" 2>&1 && echo "pass" || echo "fail")
T1_RESULT="${T1##*$'\n'}"
log_check "_get_auto_docstring_names detects decorated names" 0.20 "$T1_RESULT" "[pr_diff]"

# --- T2: _get_auto_docstring_names caching works ---
# [pr_diff] (0.10): Cache returns identical object with correct contents on repeated calls
T2=$(python3 -c "
import sys, os, tempfile
sys.path.insert(0, 'utils')
from check_docstrings import _get_auto_docstring_names

src = '@auto_docstring\nclass X:\n    pass\n\n@auto_docstring()\ndef y(): pass\n'
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(src)
    path = f.name

try:
    cache = {}
    r1 = _get_auto_docstring_names(path, cache=cache)
    r2 = _get_auto_docstring_names(path, cache=cache)
    assert r1 is r2, 'Cache must return the same object'
    assert path in cache, 'Path must be stored in cache'
    assert 'X' in r1, f'Expected X in result, got {r1}'
    assert 'y' in r1, f'Expected y in result, got {r1}'
    print('OK')
finally:
    os.unlink(path)
" 2>&1 && echo "pass" || echo "fail")
T2_RESULT="${T2##*$'\n'}"
log_check "_get_auto_docstring_names caching returns same object" 0.10 "$T2_RESULT" "[pr_diff]"

# --- T3: _build_ast_indexes actually USES the provided tree ---
# [pr_diff] (0.15): When tree= is given, function uses it instead of re-parsing source
T3=$(python3 -c "
import sys, ast, textwrap
sys.path.insert(0, 'utils')
from check_docstrings import _build_ast_indexes

# Source with TWO decorated classes
source = textwrap.dedent('''
@auto_docstring
class Alpha:
    def __init__(self, size=10):
        self.size = size

@auto_docstring
class Beta:
    def __init__(self, dim=20):
        self.dim = dim
''').strip()

# Full tree → both classes
full_tree = ast.parse(source)
full_items = _build_ast_indexes(source, tree=full_tree)
full_names = {it.name for it in full_items}
assert 'Alpha' in full_names and 'Beta' in full_names, f'Full tree should yield both classes, got {full_names}'

# Modified tree: remove Beta from top-level body
mod_tree = ast.parse(source)
mod_tree.body = [n for n in mod_tree.body if not (isinstance(n, ast.ClassDef) and n.name == 'Beta')]

# If function actually uses tree, it should only find Alpha
mod_items = _build_ast_indexes(source, tree=mod_tree)
mod_names = {it.name for it in mod_items}
assert 'Beta' not in mod_names, f'Function ignored tree param! Modified tree has no Beta, but got {mod_names}'
assert 'Alpha' in mod_names, f'Alpha should still be found, got {mod_names}'
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T3_RESULT="${T3##*$'\n'}"
log_check "_build_ast_indexes uses provided tree" 0.15 "$T3_RESULT" "[pr_diff]"

# --- T4: _find_typed_dict_classes actually USES the provided tree ---
# [pr_diff] (0.15): When tree= is given, function uses it instead of re-parsing source
T4=$(python3 -c "
import sys, ast, textwrap
sys.path.insert(0, 'utils')
from check_docstrings import _find_typed_dict_classes

# Source with TWO TypedDict classes
source = textwrap.dedent('''
class FooKwargs(TypedDict):
    x: int
    y: str

class BarKwargs(TypedDict):
    a: float
''').strip()

# Full tree → 2 results
full_tree = ast.parse(source)
full_result = _find_typed_dict_classes(source, tree=full_tree)
full_names = {r['name'] for r in full_result}
assert len(full_result) == 2, f'Expected 2 TypedDicts from full tree, got {len(full_result)}'

# Modified tree: remove BarKwargs
mod_tree = ast.parse(source)
mod_tree.body = [n for n in mod_tree.body if not (isinstance(n, ast.ClassDef) and n.name == 'BarKwargs')]

# If function uses tree, should only find FooKwargs
mod_result = _find_typed_dict_classes(source, tree=mod_tree)
mod_names = {r['name'] for r in mod_result}
assert 'BarKwargs' not in mod_names, f'Function ignored tree param! Modified tree has no BarKwargs, but got {mod_names}'
assert 'FooKwargs' in mod_names, f'FooKwargs should still be found, got {mod_names}'
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T4_RESULT="${T4##*$'\n'}"
log_check "_find_typed_dict_classes uses provided tree" 0.15 "$T4_RESULT" "[pr_diff]"

# --- T5: has_auto_docstring_decorator uses cache parameter ---
# [pr_diff] (0.10): Cache-based lookup works for decorator detection
T5=$(python3 -c "
import sys, os, tempfile, inspect
from unittest.mock import patch
sys.path.insert(0, 'utils')
from check_docstrings import has_auto_docstring_decorator

src = '@auto_docstring\nclass Cached:\n    pass\n'
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(src)
    path = f.name

try:
    cache = {path: {'Cached'}}
    Cached = type('Cached', (), {})
    Other = type('Other', (), {})
    with patch.object(inspect, 'getfile', return_value=path):
        assert has_auto_docstring_decorator(Cached, cache=cache) == True, 'Should find Cached'
        assert has_auto_docstring_decorator(Other, cache=cache) == False, 'Should not find Other'
    print('OK')
finally:
    os.unlink(path)
" 2>&1 && echo "pass" || echo "fail")
T5_RESULT="${T5##*$'\n'}"
log_check "has_auto_docstring_decorator uses cache param" 0.10 "$T5_RESULT" "[pr_diff]"

# --- T6: _get_auto_docstring_names handles syntax errors ---
# [pr_diff] (0.05): Syntax error files return empty set, don't crash
T6=$(python3 -c "
import sys, os, tempfile
sys.path.insert(0, 'utils')
from check_docstrings import _get_auto_docstring_names

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write('def broken(\n')
    path = f.name

try:
    result = _get_auto_docstring_names(path)
    assert result == set(), f'Syntax error file should return empty set, got {result}'
    print('OK')
finally:
    os.unlink(path)
" 2>&1 && echo "pass" || echo "fail")
T6_RESULT="${T6##*$'\n'}"
log_check "_get_auto_docstring_names handles syntax errors" 0.05 "$T6_RESULT" "[pr_diff]"

echo ""
echo "=== Pass-to-pass regression tests ==="

# --- T7: _build_ast_indexes backward compat (no tree param) ---
# [pr_diff] (0.05): Still works when called without tree parameter
T7=$(python3 -c "
import sys, textwrap
sys.path.insert(0, 'utils')
from check_docstrings import _build_ast_indexes

source = textwrap.dedent('''
@auto_docstring
def my_func(x, y=10):
    pass
''').strip()

items = _build_ast_indexes(source)
assert len(items) == 1
assert items[0].name == 'my_func'
assert 'x' in items[0].args
assert 'y' in items[0].args
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T7_RESULT="${T7##*$'\n'}"
log_check "_build_ast_indexes backward compat (no tree)" 0.05 "$T7_RESULT" "[pr_diff]"

# --- T8: _find_typed_dict_classes backward compat (no tree param) ---
# [pr_diff] (0.05): Still works when called without tree parameter
T8=$(python3 -c "
import sys, textwrap
sys.path.insert(0, 'utils')
from check_docstrings import _find_typed_dict_classes

source = textwrap.dedent('''
class MyKwargs(TypedDict):
    x: int
''').strip()

result = _find_typed_dict_classes(source)
assert len(result) == 1
assert result[0]['name'] == 'MyKwargs'
print('OK')
" 2>&1 && echo "pass" || echo "fail")
T8_RESULT="${T8##*$'\n'}"
log_check "_find_typed_dict_classes backward compat (no tree)" 0.05 "$T8_RESULT" "[pr_diff]"

echo ""
echo "=== Config-derived checks ==="

# --- T9: ruff lint check ---
# [agent_config] (0.10): "make style runs formatters and linters (ruff)" — CLAUDE.md:2 @ 1f553bdc
T9=$(python3 -c "
import subprocess, sys
result = subprocess.run(
    ['ruff', 'check', '--select=E,W,F', '--no-fix', 'utils/check_docstrings.py'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('OK')
else:
    print(result.stdout[:500])
    print(result.stderr[:500])
    sys.exit(1)
" 2>&1 && echo "pass" || echo "fail")
T9_RESULT="${T9##*$'\n'}"
log_check "ruff lint check on utils/check_docstrings.py" 0.10 "$T9_RESULT" "[agent_config]"

echo ""
echo "=== Results ==="
echo "Score: $SCORE / $TOTAL"

# Write reward
mkdir -p /logs/verifier
REWARD=$(python3 -c "print(f'{min(1.0, $SCORE):.4f}')")
echo "$REWARD" > /logs/verifier/reward.txt
echo "reward=$REWARD"

# Write detailed JSON
python3 -c "
import json
data = {
    'reward': min(1.0, $SCORE),
    'behavioral': sum([
        $( [ \"$T1_RESULT\" = \"pass\" ] && echo 0.20 || echo 0 ),
        $( [ \"$T2_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
        $( [ \"$T3_RESULT\" = \"pass\" ] && echo 0.15 || echo 0 ),
        $( [ \"$T4_RESULT\" = \"pass\" ] && echo 0.15 || echo 0 ),
        $( [ \"$T5_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
        $( [ \"$T6_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
    ]),
    'regression': sum([
        $( [ \"$T7_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
        $( [ \"$T8_RESULT\" = \"pass\" ] && echo 0.05 || echo 0 ),
    ]),
    'config': $( [ \"$T9_RESULT\" = \"pass\" ] && echo 0.10 || echo 0 ),
}
print(json.dumps(data, indent=2))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
