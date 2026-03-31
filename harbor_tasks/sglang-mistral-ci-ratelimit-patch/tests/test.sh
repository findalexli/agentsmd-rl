#!/usr/bin/env bash
set +e

TOTAL=0
EARNED=0

add_score() {
    local weight=$1 pass=$2 label=$3
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        EARNED=$(python3 -c "print($EARNED + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

cd /repo

TARGET="python/sglang/srt/utils/hf_transformers_utils.py"

########################################
# GATE: Syntax check
########################################
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null; then
    echo "GATE FAIL: hf_transformers_utils.py has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: syntax check"

########################################
# Behavioral fail-to-pass tests (0.75)
########################################

# [pr_diff] (0.35): In CI mode, calling get_tokenizer patches is_base_mistral to return False
# Tests the END EFFECT through the public API — no reference to internal function names.
PASS=0
python3 << 'PYEOF'
import os, sys
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers
import transformers.tokenization_utils_tokenizers as tut

# Ensure is_base_mistral exists with API-calling behavior (returns True)
if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

# Call get_tokenizer — it will fail on the nonexistent model, but the
# CI patch should already be applied before AutoTokenizer.from_pretrained
try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass  # Expected: model doesn't exist

# The key behavioral effect: is_base_mistral must now return False
result = tut.is_base_mistral('any-model-id')
assert result == False, f'Expected is_base_mistral to return False in CI after get_tokenizer, got {result}'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.35 $PASS "[pr_diff] (0.35): In CI, get_tokenizer patches is_base_mistral to return False"

# [pr_diff] (0.15): Without CI env, is_base_mistral is NOT replaced
PASS=0
python3 << 'PYEOF'
import os, sys
os.environ.pop('SGLANG_IS_IN_CI', None)

import transformers
import transformers.tokenization_utils_tokenizers as tut

# Set a sentinel function to detect unwanted patching
sentinel_value = '__sentinel_no_ci__'
tut.is_base_mistral = lambda model_id: sentinel_value

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

# Sentinel must still be in place — no patching without CI env
result = tut.is_base_mistral('test')
assert result == sentinel_value, f'Expected sentinel (no patch without CI env), got {result}'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.15 $PASS "[pr_diff] (0.15): Without CI env, is_base_mistral is NOT patched"

# [pr_diff] (0.10): Idempotent — calling get_tokenizer multiple times doesn't break
PASS=0
python3 << 'PYEOF'
import os, sys
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers
import transformers.tokenization_utils_tokenizers as tut

if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

# Call get_tokenizer three times to verify idempotency
for i in range(3):
    try:
        get_tokenizer('__nonexistent_ci_patch_test_model__')
    except Exception:
        pass

result = tut.is_base_mistral('test')
assert result == False, f'Expected False after repeated get_tokenizer calls, got {result}'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): Calling get_tokenizer multiple times is idempotent"

# [pr_diff] (0.10): Patch is applied BEFORE AutoTokenizer.from_pretrained
# We hook AutoTokenizer.from_pretrained to verify is_base_mistral is already
# patched at the moment the tokenizer load starts.
PASS=0
python3 << 'PYEOF'
import os, sys
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers
from transformers import AutoTokenizer
import transformers.tokenization_utils_tokenizers as tut

if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

# Hook AutoTokenizer.from_pretrained to check is_base_mistral state
was_patched_before_call = [None]

def hooked_from_pretrained(*args, **kwargs):
    was_patched_before_call[0] = (tut.is_base_mistral('test') == False)
    raise RuntimeError('hooked_from_pretrained: test stop')

AutoTokenizer.from_pretrained = staticmethod(hooked_from_pretrained)

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

assert was_patched_before_call[0] is not None, 'AutoTokenizer.from_pretrained was never called'
assert was_patched_before_call[0] == True, 'is_base_mistral was NOT patched before AutoTokenizer.from_pretrained was called'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): Patch applied before AutoTokenizer.from_pretrained"

# [pr_diff] (0.05): Version guard — with a mismatched version, patch does NOT apply
PASS=0
python3 << 'PYEOF'
import os, sys
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers.tokenization_utils_tokenizers as tut

sentinel_value = '__sentinel_version_guard__'
tut.is_base_mistral = lambda model_id: sentinel_value

import sglang.srt.utils.hf_transformers_utils as mod

# Sabotage the version constant so it won't match the real transformers version
if hasattr(mod, '_TRANSFORMERS_PATCHED_VERSION'):
    mod._TRANSFORMERS_PATCHED_VERSION = '0.0.0-never-match'

try:
    mod.get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

# With mismatched version constant, the sentinel should still be in place (patch skipped)
result = tut.is_base_mistral('test')
assert result == sentinel_value, f'Expected sentinel (version guard should prevent patch when version mismatches), got {result}'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): Version guard prevents patch on different transformers version"

########################################
# Pass-to-pass regression tests (0.15)
########################################

# [pr_diff] (0.10): get_tokenizer function exists with expected signature
PASS=0
python3 << 'PYEOF'
import inspect
from sglang.srt.utils.hf_transformers_utils import get_tokenizer

sig = inspect.signature(get_tokenizer)
params = list(sig.parameters.keys())
assert 'tokenizer_name' in params, f'tokenizer_name not in params: {params}'
assert 'tokenizer_mode' in params, f'tokenizer_mode not in params: {params}'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): get_tokenizer function exists with expected signature (regression)"

# [pr_diff] (0.05): TokenizerWarningsFilter still exists as a logging.Filter
PASS=0
python3 << 'PYEOF'
import logging
from sglang.srt.utils.hf_transformers_utils import TokenizerWarningsFilter

assert issubclass(TokenizerWarningsFilter, logging.Filter), 'Not a logging.Filter subclass'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.05 $PASS "[pr_diff] (0.05): TokenizerWarningsFilter still exists (regression)"

########################################
# Anti-stub structural check (0.10)
########################################

# [pr_diff] (0.10): File has non-trivial CI patching logic
# WHY AST: anti-stub guard only — behavioral tests verify actual behavior.
# We check for meaningful additions without requiring specific function names.
PASS=0
python3 << 'PYEOF'
import ast

with open('python/sglang/srt/utils/hf_transformers_utils.py') as f:
    source = f.read()

tree = ast.parse(source)

# The file must reference is_base_mistral (pre-existing transformers API, not gold-patch name)
assert 'is_base_mistral' in source, 'File does not reference is_base_mistral (the function being patched)'

# Look for ANY function that has conditional logic + imports (patching function or inlined in get_tokenizer)
func_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

found_patch_logic = False
for fn in func_defs:
    body_types = set()
    for n in ast.walk(fn):
        body_types.add(type(n).__name__)

    has_conditional = 'If' in body_types
    has_import = 'Import' in body_types or 'ImportFrom' in body_types
    has_assign_or_global = 'Global' in body_types or 'Assign' in body_types
    stmt_count = sum(1 for n in ast.walk(fn) if isinstance(n, ast.stmt))

    # A patching function: conditionals + imports + assignments + non-trivial body
    if has_conditional and has_import and has_assign_or_global and stmt_count >= 6:
        # Could be a standalone patch function or get_tokenizer with inlined logic
        found_patch_logic = True
        break

assert found_patch_logic, 'No function with CI patching logic found (need conditionals + imports + assignments, 6+ statements)'
print('OK')
PYEOF
[ $? -eq 0 ] && PASS=1
add_score 0.10 $PASS "[pr_diff] (0.10): File has non-trivial CI patching logic (anti-stub)"

########################################
# Compute final reward
########################################

REWARD=$(python3 -c "print(round($EARNED, 4))")
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "print(min($EARNED, 0.75))")
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
