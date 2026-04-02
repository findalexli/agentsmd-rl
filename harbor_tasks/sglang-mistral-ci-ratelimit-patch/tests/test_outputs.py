"""
Task: sglang-mistral-ci-ratelimit-patch
Repo: sgl-project/sglang @ 33cca495ae75e745be62b5b009f4c87fb40dd044
PR:   21729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import sys
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/python/sglang/srt/utils/hf_transformers_utils.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """hf_transformers_utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff / static) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_patches_is_base_mistral():
    """In CI mode, get_tokenizer patches is_base_mistral to return False."""
    env = os.environ.copy()
    env["SGLANG_IS_IN_CI"] = "true"
    import subprocess

    r = subprocess.run(
        [
            sys.executable, "-c", """
import os
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers.tokenization_utils_tokenizers as tut

if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

result = tut.is_base_mistral('any-model-id')
assert result == False, f'Expected False in CI, got {result}'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**env, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"CI patch test failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_idempotent_multiple_calls():
    """Calling get_tokenizer multiple times in CI doesn't break the patch."""
    import subprocess

    env = os.environ.copy()
    env["SGLANG_IS_IN_CI"] = "true"

    r = subprocess.run(
        [
            sys.executable, "-c", """
import os
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers.tokenization_utils_tokenizers as tut

if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

for i in range(3):
    try:
        get_tokenizer('__nonexistent_ci_patch_test_model__')
    except Exception:
        pass

result = tut.is_base_mistral('test')
assert result == False, f'Expected False after repeated calls, got {result}'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**env, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"Idempotency test failed:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_patch_before_from_pretrained():
    """Patch is applied BEFORE AutoTokenizer.from_pretrained is called."""
    import subprocess

    env = os.environ.copy()
    env["SGLANG_IS_IN_CI"] = "true"

    r = subprocess.run(
        [
            sys.executable, "-c", """
import os
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers
from transformers import AutoTokenizer
import transformers.tokenization_utils_tokenizers as tut

if not hasattr(tut, 'is_base_mistral'):
    tut.is_base_mistral = lambda model_id: True

was_patched_before_call = [None]
_orig = AutoTokenizer.from_pretrained

def hooked(*args, **kwargs):
    was_patched_before_call[0] = (tut.is_base_mistral('test') == False)
    raise RuntimeError('hooked: stop')

AutoTokenizer.from_pretrained = staticmethod(hooked)

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

assert was_patched_before_call[0] is not None, 'from_pretrained was never called'
assert was_patched_before_call[0] == True, 'is_base_mistral not patched before from_pretrained'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**env, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"Ordering test failed:\n{r.stderr.decode()}"


# [static] fail_to_pass
def test_not_stub():
    """File has non-trivial CI patching logic (not a stub)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    assert "is_base_mistral" in source, "File does not reference is_base_mistral"

    func_defs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    found_patch_logic = False
    for fn in func_defs:
        body_types = set()
        for n in ast.walk(fn):
            body_types.add(type(n).__name__)

        has_conditional = "If" in body_types
        has_import = "Import" in body_types or "ImportFrom" in body_types
        has_assign_or_global = "Global" in body_types or "Assign" in body_types
        stmt_count = sum(1 for n in ast.walk(fn) if isinstance(n, ast.stmt))

        if has_conditional and has_import and has_assign_or_global and stmt_count >= 6:
            found_patch_logic = True
            break

    assert found_patch_logic, (
        "No function with CI patching logic found "
        "(need conditionals + imports + assignments, 6+ statements)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_patch_without_ci_env():
    """Without SGLANG_IS_IN_CI, is_base_mistral is NOT replaced."""
    import subprocess

    env = os.environ.copy()
    env.pop("SGLANG_IS_IN_CI", None)

    r = subprocess.run(
        [
            sys.executable, "-c", """
import os
os.environ.pop('SGLANG_IS_IN_CI', None)

import transformers.tokenization_utils_tokenizers as tut

sentinel = '__sentinel_no_ci__'
tut.is_base_mistral = lambda model_id: sentinel

from sglang.srt.utils.hf_transformers_utils import get_tokenizer

try:
    get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

result = tut.is_base_mistral('test')
assert result == sentinel, f'Expected sentinel (no patch without CI), got {result}'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**env, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"No-CI test failed:\n{r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_version_guard_skips_on_mismatch():
    """With a mismatched transformers version constant, patch is skipped."""
    import subprocess

    env = os.environ.copy()
    env["SGLANG_IS_IN_CI"] = "true"

    r = subprocess.run(
        [
            sys.executable, "-c", """
import os
os.environ['SGLANG_IS_IN_CI'] = 'true'

import transformers.tokenization_utils_tokenizers as tut

sentinel = '__sentinel_version_guard__'
tut.is_base_mistral = lambda model_id: sentinel

import sglang.srt.utils.hf_transformers_utils as mod

if hasattr(mod, '_TRANSFORMERS_PATCHED_VERSION'):
    mod._TRANSFORMERS_PATCHED_VERSION = '0.0.0-never-match'

# Reset patch state so it re-evaluates
if hasattr(mod, '_is_base_mistral_patched'):
    mod._is_base_mistral_patched = False

try:
    mod.get_tokenizer('__nonexistent_ci_patch_test_model__')
except Exception:
    pass

result = tut.is_base_mistral('test')
assert result == sentinel, f'Expected sentinel (version guard), got {result}'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**env, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"Version guard test failed:\n{r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_get_tokenizer_signature():
    """get_tokenizer function exists with expected signature."""
    import subprocess

    r = subprocess.run(
        [
            sys.executable, "-c", """
import inspect
from sglang.srt.utils.hf_transformers_utils import get_tokenizer

sig = inspect.signature(get_tokenizer)
params = list(sig.parameters.keys())
assert 'tokenizer_name' in params, f'tokenizer_name not in params: {params}'
assert 'tokenizer_mode' in params, f'tokenizer_mode not in params: {params}'
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"Signature test failed:\n{r.stderr.decode()}"


# [pr_diff] pass_to_pass
def test_tokenizer_warnings_filter_exists():
    """TokenizerWarningsFilter still exists as a logging.Filter."""
    import subprocess

    r = subprocess.run(
        [
            sys.executable, "-c", """
import logging
from sglang.srt.utils.hf_transformers_utils import TokenizerWarningsFilter
assert issubclass(TokenizerWarningsFilter, logging.Filter)
""",
        ],
        capture_output=True,
        timeout=30,
        cwd=REPO,
        env={**os.environ, "PYTHONPATH": f"{REPO}/python"},
    )
    assert r.returncode == 0, f"Filter test failed:\n{r.stderr.decode()}"
