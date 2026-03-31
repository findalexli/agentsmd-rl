#!/usr/bin/env bash
set +e

TOTAL=0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd /repo

###############################################################################
# GATE: Syntax check — score 0 on failure
###############################################################################
# [pr_diff] (0): Python syntax valid
python3 -c "
import py_compile, sys
for f in ['src/transformers/utils/import_utils.py', 'src/transformers/utils/__init__.py']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'GATE FAIL: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

###############################################################################
# F2P (0.10): Function importable from transformers.utils
###############################################################################
# [pr_diff] (0.10): is_flash_attn_greater_or_equal_2_10 importable
if python3 -c "
from transformers.utils import is_flash_attn_greater_or_equal_2_10
assert callable(is_flash_attn_greater_or_equal_2_10)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): function importable from transformers.utils"
    add 0.10
else
    echo "FAIL (0.10): cannot import is_flash_attn_greater_or_equal_2_10"
fi

###############################################################################
# F2P (0.10): Returns False (bool) when flash_attn is not installed
###############################################################################
# [pr_diff] (0.10): correct return value without flash_attn
if python3 -c "
import warnings
warnings.simplefilter('ignore')
from transformers.utils.import_utils import is_flash_attn_greater_or_equal_2_10
if hasattr(is_flash_attn_greater_or_equal_2_10, 'cache_clear'):
    is_flash_attn_greater_or_equal_2_10.cache_clear()
result = is_flash_attn_greater_or_equal_2_10()
assert isinstance(result, bool), f'Expected bool, got {type(result)}'
assert result == False, f'Expected False without flash_attn, got {result}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): returns False without flash_attn"
    add 0.10
else
    echo "FAIL (0.10): wrong return type or value"
fi

###############################################################################
# F2P (0.30): Delegation — returns True when flash_attn >= 2.10 is present
###############################################################################
# [pr_diff] (0.30): function delegates to real version check, not hardcoded False
if python3 -c "
import sys, importlib, warnings
from types import ModuleType

# Inject a fake flash_attn module with version 2.11.0
fake_fa = ModuleType('flash_attn')
fake_fa.__version__ = '2.11.0'
sys.modules['flash_attn'] = fake_fa
# Some builds also probe flash_attn_2_cuda
fake_cuda = ModuleType('flash_attn_2_cuda')
sys.modules['flash_attn_2_cuda'] = fake_cuda

# Reload the module so it picks up the mock
import transformers.utils.import_utils as iu
importlib.reload(iu)

# Clear every lru_cache in the module
for name in dir(iu):
    obj = getattr(iu, name, None)
    if callable(obj) and hasattr(obj, 'cache_clear'):
        try: obj.cache_clear()
        except: pass

with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    result = iu.is_flash_attn_greater_or_equal_2_10()
    assert result == True, f'With flash_attn 2.11.0, expected True, got {result}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.30): returns True when flash_attn >= 2.10"
    add 0.30
else
    echo "FAIL (0.30): does not delegate to real version check"
fi

###############################################################################
# F2P (0.15): Emits deprecation warning on call
###############################################################################
# [pr_diff] (0.15): function warns about deprecation
if python3 -c "
import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    from transformers.utils.import_utils import is_flash_attn_greater_or_equal_2_10
    if hasattr(is_flash_attn_greater_or_equal_2_10, 'cache_clear'):
        is_flash_attn_greater_or_equal_2_10.cache_clear()
    is_flash_attn_greater_or_equal_2_10()
    dep = [x for x in w if issubclass(x.category, (FutureWarning, DeprecationWarning))]
    assert len(dep) >= 1, f'Expected deprecation warning, got {[x.category for x in w]}'
    msg = str(dep[0].message).lower()
    assert any(kw in msg for kw in ('deprecat', 'removed', 'use ')), \
        f'Warning does not mention deprecation/replacement: {msg}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.15): deprecation warning emitted"
    add 0.15
else
    echo "FAIL (0.15): no deprecation warning"
fi

###############################################################################
# P2P (0.10): Existing is_flash_attn_greater_or_equal still works
###############################################################################
# [pr_diff] (0.10): generic version check unbroken
if python3 -c "
from transformers.utils import is_flash_attn_greater_or_equal
result = is_flash_attn_greater_or_equal('2.1.0')
assert isinstance(result, bool), f'Expected bool, got {type(result)}'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): is_flash_attn_greater_or_equal still works"
    add 0.10
else
    echo "FAIL (0.10): is_flash_attn_greater_or_equal broken"
fi

###############################################################################
# P2P (0.10): Other core utils imports unbroken
###############################################################################
# [pr_diff] (0.10): utils module still exports core utilities
if python3 -c "
from transformers.utils import is_torch_available, is_flash_attn_available
assert callable(is_torch_available)
assert callable(is_flash_attn_available)
print('OK')
" 2>/dev/null; then
    echo "PASS (0.10): other utils imports work"
    add 0.10
else
    echo "FAIL (0.10): other utils imports broken"
fi

###############################################################################
# Anti-stub (0.10): Function body is non-trivial
###############################################################################
# [pr_diff] (0.10): real implementation, not a stub
if python3 -c "
import ast, sys
with open('src/transformers/utils/import_utils.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'is_flash_attn_greater_or_equal_2_10':
        # Filter out pass and docstrings, keep function calls and returns
        meaningful = [n for n in node.body
                      if not isinstance(n, ast.Pass)
                      and not (isinstance(n, ast.Expr)
                               and isinstance(getattr(n, 'value', None), ast.Constant))]
        assert len(meaningful) >= 2, f'Body too short: {len(meaningful)} meaningful stmts'
        has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
        assert has_return, 'No return statement found'
        print('OK')
        sys.exit(0)
print('Function not found', file=sys.stderr)
sys.exit(1)
" 2>/dev/null; then
    echo "PASS (0.10): function has real implementation"
    add 0.10
else
    echo "FAIL (0.10): function is stub or missing"
fi

###############################################################################
# Config (0.05): ruff check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ b0bba2d
if command -v ruff &>/dev/null; then
    if ruff check src/transformers/utils/import_utils.py src/transformers/utils/__init__.py --quiet 2>/dev/null; then
        echo "PASS (0.05): ruff check passes"
        add 0.05
    else
        echo "FAIL (0.05): ruff check fails"
    fi
else
    echo "SKIP (0.05): ruff not installed, awarding points"
    add 0.05
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
