#!/usr/bin/env bash
set +e

TOTAL=0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 4))"); }

cd /repo

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0): Python syntax valid
python3 -c "
import py_compile, sys
for f in ['src/transformers/__init__.py', 'src/transformers/image_processing_backends.py']:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print(f'GATE FAIL: {e}', file=sys.stderr)
        sys.exit(1)
print('GATE: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

###############################################################################
# Fail-to-pass: BaseImageProcessorFast importable AND resolves to correct class
###############################################################################
# [pr_diff] (0.30): BaseImageProcessorFast importable from legacy path and is TorchvisionBackend
if python3 -c "
from transformers.image_processing_utils_fast import BaseImageProcessorFast
from transformers.image_processing_backends import TorchvisionBackend
assert BaseImageProcessorFast is not None, 'BaseImageProcessorFast is None'
assert BaseImageProcessorFast is TorchvisionBackend, (
    f'Expected same class: got {BaseImageProcessorFast!r} vs {TorchvisionBackend!r}')
print('OK')
" 2>/dev/null; then
    echo "PASS (0.30): BaseImageProcessorFast importable and is TorchvisionBackend"
    add 0.30
else
    echo "FAIL (0.30): BaseImageProcessorFast not importable or not TorchvisionBackend"
fi

###############################################################################
# Fail-to-pass: divide_to_patches importable AND resolves to correct function
###############################################################################
# [pr_diff] (0.25): divide_to_patches importable from legacy path and is same function
if python3 -c "
from transformers.image_processing_utils_fast import divide_to_patches
from transformers.image_transforms import divide_to_patches as original
assert callable(divide_to_patches), 'divide_to_patches not callable'
assert divide_to_patches is original, (
    f'Expected same function: got {divide_to_patches!r} vs {original!r}')
print('OK')
" 2>/dev/null; then
    echo "PASS (0.25): divide_to_patches importable and is same function"
    add 0.25
else
    echo "FAIL (0.25): divide_to_patches not importable or not same function"
fi

###############################################################################
# Fail-to-pass: Alias module registered in sys.modules after import transformers
###############################################################################
# [pr_diff] (0.15): alias proactively registered during package init
if python3 -c "
import transformers
import sys
# Alias must be registered by __init__.py, not by explicit submodule import
assert 'transformers.image_processing_utils_fast' in sys.modules, \
    'image_processing_utils_fast not in sys.modules after import transformers'
mod = sys.modules['transformers.image_processing_utils_fast']
# __file__ must be set in __dict__ (not via __getattr__) to prevent circular import
assert '__file__' in mod.__dict__, '__file__ not directly set in module __dict__'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.15): alias registered in sys.modules with __file__ set"
    add 0.15
else
    echo "FAIL (0.15): alias not registered in sys.modules or __file__ not set"
fi

###############################################################################
# Fail-to-pass: inspect.getfile works on alias (circular import prevention)
###############################################################################
# [pr_diff] (0.10): inspect.getfile on alias module does not raise
if python3 -c "
import transformers
import sys, inspect
mod = sys.modules.get('transformers.image_processing_utils_fast')
if mod is None:
    # fallback: try explicit import
    import transformers.image_processing_utils_fast as mod
f = inspect.getfile(mod)
assert f is not None, 'getfile returned None'
print(f'OK: {f}')
" 2>/dev/null; then
    echo "PASS (0.10): inspect.getfile works on alias module"
    add 0.10
else
    echo "FAIL (0.10): inspect.getfile raises on alias module"
fi

###############################################################################
# Pass-to-pass: Existing tokenization aliases still work
###############################################################################
# [pr_diff] (0.05): tokenization_utils_fast alias unbroken
if python3 -c "
import transformers
import sys
assert 'transformers.tokenization_utils_fast' in sys.modules, \
    'tokenization_utils_fast alias broken'
assert 'transformers.tokenization_utils' in sys.modules, \
    'tokenization_utils alias broken'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): existing tokenization aliases still work"
    add 0.05
else
    echo "FAIL (0.05): tokenization aliases broken"
fi

###############################################################################
# Pass-to-pass: Direct import from image_processing_backends still works
###############################################################################
# [pr_diff] (0.05): image_processing_backends direct import unbroken
if python3 -c "
from transformers.image_processing_backends import TorchvisionBackend
assert TorchvisionBackend is not None
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): direct import from image_processing_backends works"
    add 0.05
else
    echo "FAIL (0.05): direct import from image_processing_backends broken"
fi

###############################################################################
# Config-derived: ruff format check on changed files
###############################################################################
# [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ e6ed96c
if command -v ruff &>/dev/null; then
    if ruff check src/transformers/__init__.py src/transformers/image_processing_backends.py --quiet 2>/dev/null; then
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
# Anti-stub: solution adds real alias logic, not a pass/stub
###############################################################################
# [pr_diff] (0.05): __init__.py contains alias setup code (AST-verified)
if python3 -c "
import ast
with open('src/transformers/__init__.py') as f:
    source = f.read()
tree = ast.parse(source)
# Look for string literal 'image_processing_utils_fast' in the AST
# (a comment containing the string would NOT appear in AST)
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if 'image_processing_utils_fast' in node.value:
            found = True
            break
assert found, 'image_processing_utils_fast not found as string literal in __init__.py AST'
print('OK')
" 2>/dev/null; then
    echo "PASS (0.05): anti-stub AST check passes"
    add 0.05
else
    echo "FAIL (0.05): anti-stub AST check fails"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total reward: $TOTAL"
echo "$TOTAL" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
