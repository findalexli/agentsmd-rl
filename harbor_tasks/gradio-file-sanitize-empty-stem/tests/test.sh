#!/usr/bin/env bash
set -euo pipefail

REPO=/workspace/gradio
RESULTS_DIR="/logs/verifier"
TOTAL=0.0
EARNED=0.0

add() {
    TOTAL=$(python3 -c "print($TOTAL + $1)")
    EARNED=$(python3 -c "print($EARNED + $2)")
}

cd "$REPO"

########################################
# GATE: Syntax check — abort on failure
########################################
# [pr_diff] (gate): Modified file must parse
if python3 -c "import py_compile; py_compile.compile('client/python/gradio_client/utils.py', doraise=True)" 2>/dev/null; then
    echo "GATE: syntax check passed"
else
    echo "GATE: syntax check FAILED — aborting"
    echo "0.0" > "$RESULTS_DIR/reward.txt"
    exit 0
fi

########################################
# Fail-to-pass: behavioral tests (0.70)
########################################

# [pr_diff] (0.20): Filename with entirely-stripped stem gets a valid extension
if python3 -c "
from gradio_client.utils import strip_invalid_filename_characters
from pathlib import Path
result = strip_invalid_filename_characters('#.txt')
assert Path(result).suffix == '.txt', f'Expected .txt suffix, got {Path(result).suffix!r} from {result!r}'
assert result != '.txt', f'Result should not be bare dotfile, got {result!r}'
print('PASS: #.txt preserves extension')
" 2>&1; then
    add 0.20 0.20
else
    add 0.20 0.0
    echo "FAIL: #.txt extension not preserved"
fi

# [pr_diff] (0.15): Multiple special chars stripped entirely
if python3 -c "
from gradio_client.utils import strip_invalid_filename_characters
from pathlib import Path
result = strip_invalid_filename_characters('###.pdf')
assert Path(result).suffix == '.pdf', f'Expected .pdf suffix, got {Path(result).suffix!r}'
assert result != '.pdf', f'Should not be bare dotfile'
print('PASS: ###.pdf preserves extension')
" 2>&1; then
    add 0.15 0.15
else
    add 0.15 0.0
    echo "FAIL: ###.pdf extension not preserved"
fi

# [pr_diff] (0.15): Mixed special chars stripped entirely
if python3 -c "
from gradio_client.utils import strip_invalid_filename_characters
from pathlib import Path
for fname, ext in [('@!\$.csv', '.csv'), ('!!!.json', '.json')]:
    result = strip_invalid_filename_characters(fname)
    assert Path(result).suffix == ext, f'{fname}: expected {ext}, got {Path(result).suffix!r}'
    assert result != ext, f'{fname}: should not be bare dotfile'
print('PASS: mixed special-char filenames preserve extension')
" 2>&1; then
    add 0.15 0.15
else
    add 0.15 0.0
    echo "FAIL: mixed special-char filenames broken"
fi

# [pr_diff] (0.20): Partial strip does NOT add fallback stem
if python3 -c "
from gradio_client.utils import strip_invalid_filename_characters
result = strip_invalid_filename_characters('a#.txt')
assert result == 'a.txt', f'Expected a.txt, got {result!r}'
print('PASS: partial strip keeps original stem chars')
" 2>&1; then
    add 0.20 0.20
else
    add 0.20 0.0
    echo "FAIL: partial strip behavior wrong"
fi

########################################
# Pass-to-pass: existing behavior (0.15)
########################################

# [repo_tests] (0.15): Existing parametrized tests still pass
if python3 -c "
from gradio_client.utils import strip_invalid_filename_characters
cases = [
    ('abc', 'abc'),
    ('\$\$AAabc&3', 'AAabc3'),
    ('\$\$AAa&..b-c3_', 'AAa..b-c3_'),
]
for inp, expected in cases:
    result = strip_invalid_filename_characters(inp)
    assert result == expected, f'{inp!r}: expected {expected!r}, got {result!r}'
print('PASS: existing strip_invalid tests pass')
" 2>&1; then
    add 0.15 0.15
else
    add 0.15 0.0
    echo "FAIL: existing strip_invalid tests broken"
fi

########################################
# Config-derived: ruff formatting (0.10)
########################################

# [agent_config] (0.10): "Python code is formatted with ruff" — AGENTS.md:43
if pip install --quiet ruff 2>/dev/null && ruff check client/python/gradio_client/utils.py --select E,W --quiet 2>&1; then
    echo "PASS: ruff lint passes"
    add 0.10 0.10
else
    echo "FAIL: ruff lint errors"
    add 0.10 0.0
fi

########################################
# Anti-stub check (0.05)
########################################

# [static] (0.05): Function body is not a stub/pass
if python3 -c "
import ast, sys
with open('client/python/gradio_client/utils.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'strip_invalid_filename_characters':
        body_stmts = [n for n in node.body if not isinstance(n, (ast.Expr,)) or not isinstance(getattr(n, 'value', None), ast.Constant)]
        assert len(body_stmts) > 2, 'Function body looks stubbed out'
        print('PASS: function is not a stub')
        sys.exit(0)
print('WARN: function not found')
sys.exit(1)
" 2>&1; then
    add 0.05 0.05
else
    add 0.05 0.0
    echo "FAIL: anti-stub check"
fi

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($EARNED / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $EARNED / $TOTAL = $REWARD"
echo "$REWARD" > "$RESULTS_DIR/reward.txt"

python3 -c "
import json
reward = $REWARD
data = {
    'reward': reward,
    'behavioral': round(min($EARNED, 0.70), 4),
    'regression': round(min(max($EARNED - 0.70, 0), 0.15), 4),
    'config': round(min(max($EARNED - 0.85, 0), 0.10), 4),
    'structural': round(min(max($EARNED - 0.95, 0), 0.05), 4),
}
with open('$RESULTS_DIR/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
