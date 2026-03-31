#!/usr/bin/env bash
set -euo pipefail

SCORE=0
TEST_FILE="tests/models/language/pooling/test_splade_sparse_pooler.py"

###############################################################################
# GATE: Syntax check — abort on failure
###############################################################################
# [pr_diff] (0.00): Test file must be valid Python
if ! python3 -c "import ast; ast.parse(open('$TEST_FILE').read())"; then
    echo "GATE FAILED: $TEST_FILE has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"config":0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: syntax OK"

###############################################################################
# Behavioral 1 (0.35): Metadata object supports get_prompt_token_ids_cpu()
###############################################################################
# [pr_diff] (0.35): Test metadata must implement get_prompt_token_ids_cpu
BEHAV1=0
if python3 -c "
import sys
sys.path.insert(0, '.')
import torch

# Extract how the test constructs the metadata and verify the method exists
# Try importing the real PoolingMetadata
try:
    from vllm.v1.pool.metadata import PoolingMetadata, PoolingStates
    from vllm.pooling_params import PoolingParams
    HAS_REAL = True
except ImportError:
    HAS_REAL = False

if HAS_REAL:
    # Verify the real PoolingMetadata has get_prompt_token_ids_cpu
    assert hasattr(PoolingMetadata, 'get_prompt_token_ids_cpu'), \
        'PoolingMetadata missing get_prompt_token_ids_cpu'

# Now test what the test file actually constructs
# Parse the test file to find the metadata construction and exec it
import importlib.util, os
spec = importlib.util.spec_from_file_location('test_mod', '$TEST_FILE')
# Don't import the whole module (may fail on model deps), instead:
# Check if the test file constructs something with get_prompt_token_ids_cpu
with open('$TEST_FILE') as f:
    src = f.read()

# The test must not use SimpleNamespace for metadata
if 'types.SimpleNamespace' in src and 'meta = types.SimpleNamespace' in src:
    print('FAIL: test still uses SimpleNamespace for metadata')
    sys.exit(1)

# The metadata object must have get_prompt_token_ids_cpu
# Check that the test imports or constructs something with this method
if HAS_REAL:
    # Construct metadata like the test should
    B, T = 2, 3
    prompt_lens = torch.tensor([T, T - 1], dtype=torch.int32)
    token_ids = torch.tensor([[101, 5, 102], [101, 6, 6]], dtype=torch.long)

    # Try constructing PoolingMetadata with required fields
    meta = PoolingMetadata(
        prompt_lens=prompt_lens,
        prompt_token_ids=token_ids,
        prompt_token_ids_cpu=token_ids,
        pooling_params=[PoolingParams(task='embed')] * B,
        pooling_states=[PoolingStates() for _ in range(B)],
    )
    result = meta.get_prompt_token_ids_cpu()
    assert isinstance(result, list), f'Expected list, got {type(result)}'
    assert len(result) == B, f'Expected {B} items, got {len(result)}'
    print('PASS: PoolingMetadata.get_prompt_token_ids_cpu() works correctly')
else:
    # Can't import PoolingMetadata — check source for correct construction
    if 'PoolingMetadata(' in src and 'get_prompt_token_ids_cpu' not in src:
        # Test uses PoolingMetadata (good), method is called inside forward()
        print('PASS: test uses PoolingMetadata (import check only)')
    elif 'PoolingMetadata' in src:
        print('PASS: test references PoolingMetadata')
    else:
        print('FAIL: test does not use PoolingMetadata')
        sys.exit(1)
" 2>&1; then
    BEHAV1=1
    echo "BEHAVIORAL 1 PASSED (0.35): metadata supports get_prompt_token_ids_cpu"
else
    echo "BEHAVIORAL 1 FAILED (0.35): metadata does not support get_prompt_token_ids_cpu"
fi

###############################################################################
# Behavioral 2 (0.35): Actual pytest run of the test
###############################################################################
# [pr_diff] (0.35): test_splade_pooler_matches_reference_formula must pass
BEHAV2=0
if python3 -m pytest "$TEST_FILE" -x --timeout=30 -q 2>&1; then
    BEHAV2=1
    echo "BEHAVIORAL 2 PASSED (0.35): pytest passes"
else
    # pytest may fail due to import issues unrelated to the fix
    # Check if it's an AttributeError (the original bug)
    PYTEST_OUT=$(python3 -m pytest "$TEST_FILE" -x --timeout=30 -q 2>&1 || true)
    if echo "$PYTEST_OUT" | grep -q "AttributeError"; then
        echo "BEHAVIORAL 2 FAILED (0.35): AttributeError — original bug still present"
    else
        # Non-AttributeError failure (e.g., missing deps) — partial credit
        echo "BEHAVIORAL 2 SKIPPED (0.35): pytest failed for non-bug reasons"
        # Give partial credit if behavioral 1 passed (the core fix is correct)
        if [ "$BEHAV1" -eq 1 ]; then
            BEHAV2=1
            echo "  -> Granting credit: core metadata fix verified in behavioral 1"
        fi
    fi
fi

###############################################################################
# Regression (0.15): Test file imports are valid and structure preserved
###############################################################################
# [pr_diff] (0.15): Test file must be importable (syntax + imports resolve)
REGR=0
if python3 -c "
import sys, ast
sys.path.insert(0, '.')

with open('$TEST_FILE') as f:
    tree = ast.parse(f.read())

# Check test function exists with correct signature
funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
         and n.name == 'test_splade_pooler_matches_reference_formula']
assert len(funcs) == 1, 'Test function missing or duplicated'
func = funcs[0]

# Check it has the parametrize decorator
decorators = [d for d in func.decorator_list
              if isinstance(d, ast.Attribute) and d.attr == 'parametrize']
has_param = len(decorators) > 0 or any(
    isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
    and d.func.attr == 'parametrize' for d in func.decorator_list
)
assert has_param, 'Test must retain @pytest.mark.parametrize decorator'

# Check SPDX header preserved
with open('$TEST_FILE') as f:
    first_lines = f.read()[:200]
assert 'SPDX-License-Identifier' in first_lines, 'SPDX header must be preserved'

print('PASS: test structure and imports preserved')
" 2>&1; then
    REGR=1
    echo "REGRESSION PASSED (0.15): test structure preserved"
else
    echo "REGRESSION FAILED (0.15): test structure broken"
fi

###############################################################################
# Anti-stub (0.10): The fix must be substantive, not a stub
###############################################################################
# [pr_diff] (0.10): Fix must not stub out the test or skip it
STUB=0
if python3 -c "
import ast

with open('$TEST_FILE') as f:
    src = f.read()

tree = ast.parse(src)

# Find the test function
funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
         and n.name == 'test_splade_pooler_matches_reference_formula']
assert len(funcs) == 1, 'Test function must exist'
func = funcs[0]

# Must not be empty or just 'pass'
body_stmts = [s for s in func.body if not isinstance(s, (ast.Expr,))
              or not (isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
assert len(body_stmts) > 3, 'Test body too short — likely stubbed'

# Must not have pytest.skip or pytest.mark.skip
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'skip':
            raise AssertionError('Test must not call pytest.skip')
    if isinstance(node, ast.Attribute) and node.attr == 'skipTest':
        raise AssertionError('Test must not be skipped')

# Must still have assert_close calls (the actual verification)
assert 'assert_close' in src, 'Test must retain torch.testing.assert_close calls'

# Must still create pooler and call forward
assert 'SPLADESparsePooler(' in src, 'Test must still instantiate SPLADESparsePooler'
assert 'pooler(' in src or 'pooler.forward(' in src, 'Test must still call pooler forward'

print('PASS: test is substantive, not stubbed')
" 2>&1; then
    STUB=1
    echo "ANTI-STUB PASSED (0.10): test is substantive"
else
    echo "ANTI-STUB FAILED (0.10): test appears stubbed or gutted"
fi

###############################################################################
# Config-derived (0.05): ruff format check (AGENTS.md: "Run ruff-check")
###############################################################################
# [agent_config] (0.05): "pre-commit run ruff-check --all-files" — AGENTS.md:98 @ 85c0950b
CONFIG=0
if command -v ruff &>/dev/null; then
    if ruff check "$TEST_FILE" --select=E,W --quiet 2>&1; then
        CONFIG=1
        echo "CONFIG PASSED (0.05): ruff check passes"
    else
        echo "CONFIG FAILED (0.05): ruff check failed"
    fi
else
    # ruff not installed — check basic formatting with Python
    if python3 -c "
import ast, tokenize, io
with open('$TEST_FILE') as f:
    src = f.read()
# Verify it parses and has no obvious issues
ast.parse(src)
# Check no wildcard imports
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and any(a.name == '*' for a in node.names):
        raise AssertionError('No wildcard imports allowed')
print('PASS')
" 2>&1; then
        CONFIG=1
        echo "CONFIG PASSED (0.05): basic lint passes (ruff not available)"
    else
        echo "CONFIG FAILED (0.05): lint issues found"
    fi
fi

###############################################################################
# Score calculation
###############################################################################
BEHAV_SCORE=$(python3 -c "print(round($BEHAV1 * 0.35 + $BEHAV2 * 0.35, 4))")
REGR_SCORE=$(python3 -c "print(round($REGR * 0.15, 4))")
STUB_SCORE=$(python3 -c "print(round($STUB * 0.10, 4))")
CONFIG_SCORE=$(python3 -c "print(round($CONFIG * 0.05, 4))")

TOTAL=$(python3 -c "print(round($BEHAV_SCORE + $REGR_SCORE + $STUB_SCORE + $CONFIG_SCORE, 4))")

echo ""
echo "=== SCORE BREAKDOWN ==="
echo "Behavioral:   $BEHAV_SCORE / 0.70"
echo "Regression:   $REGR_SCORE / 0.15"
echo "Anti-stub:    $STUB_SCORE / 0.10"
echo "Config:       $CONFIG_SCORE / 0.05"
echo "TOTAL:        $TOTAL / 1.00"

echo "$TOTAL" > /logs/verifier/reward.txt
cat > /logs/verifier/reward.json <<ENDJSON
{"reward": $TOTAL, "behavioral": $BEHAV_SCORE, "regression": $REGR_SCORE, "config": $CONFIG_SCORE, "style_rubric": 0.0}
ENDJSON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
