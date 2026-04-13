"""
Task: transformers-check-model-inputs-bc-alias
Repo: huggingface/transformers @ 2620c4ddd41afcc8d3b1d1134803bd418ffa45a7
PR:   44990

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/transformers"

sys.path.insert(0, f"{REPO}/src")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """generic.py must parse without syntax errors."""
    import ast

    src = Path(f"{REPO}/src/transformers/utils/generic.py").read_text()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_decorator_delegates_to_merge_with_config_defaults():
    """check_model_inputs as decorator produces identical results to merge_with_config_defaults.

    merge_with_config_defaults only handles a hardcoded set of args (use_cache,
    vision_feature_layer, etc.), so we test with use_cache which is the most common.
    """
    from transformers.utils.generic import check_model_inputs, merge_with_config_defaults

    class FakeConfig:
        use_cache = True

    class Model1:
        def __init__(self):
            self.config = FakeConfig()
            self.training = False

        @check_model_inputs
        def forward(self, use_cache=None):
            return {"use_cache": use_cache}

    class Model2:
        def __init__(self):
            self.config = FakeConfig()
            self.training = False

        @merge_with_config_defaults
        def forward(self, use_cache=None):
            return {"use_cache": use_cache}

    m1 = Model1()
    m2 = Model2()

    # No kwargs — should pull use_cache from config
    r1 = m1.forward()
    r2 = m2.forward()
    assert r1 == r2, f"No-args results differ: {r1} vs {r2}"
    assert r1["use_cache"] is True

    # Explicit kwarg overrides config
    r1 = m1.forward(use_cache=False)
    r2 = m2.forward(use_cache=False)
    assert r1 == r2, f"Explicit kwarg results differ: {r1} vs {r2}"
    assert r1["use_cache"] is False

    # Different config value
    FakeConfig.use_cache = False
    m3 = Model1()
    m4 = Model2()
    r3 = m3.forward()
    r4 = m4.forward()
    assert r3 == r4, f"Config=False results differ: {r3} vs {r4}"
    assert r3["use_cache"] is False


# [pr_diff] fail_to_pass
def test_decorator_returns_functional_wrapper():
    """check_model_inputs returns a working wrapper that handles use_cache defaults."""
    from transformers.utils.generic import check_model_inputs

    class Cfg:
        use_cache = True

    class M:
        def __init__(self):
            self.config = Cfg()
            self.training = False

        @check_model_inputs
        def forward(self, use_cache=None):
            return use_cache

    m = M()
    # Must pull config default when no arg passed
    assert m.forward() is True, "Expected config default True"
    # Explicit override must take precedence
    assert m.forward(use_cache=False) is False, "Expected explicit override False"

    # Test with different config value
    m.config.use_cache = True
    assert m.forward() is True, "Expected updated config default"
    assert m.forward(use_cache=False) is False, "Explicit override still works"


# [pr_diff] fail_to_pass
def test_deprecation_warning_emitted():
    """check_model_inputs emits a deprecation/rename warning when called.

    Uses subprocess for isolation: warning_once caches on the logger object,
    so running in-process after other tests would suppress the warning even
    if the alias is present. A fresh process guarantees a clean cache.
    """
    script = """import sys, logging, io
sys.path.insert(0, '/workspace/transformers/src')

import transformers.utils.generic as gen_mod

# Capture output from the module's own logger (transformers custom logger)
buf = io.StringIO()
handler = logging.StreamHandler(buf)
handler.setLevel(logging.DEBUG)

# gen_mod.logger is the transformers HfLogger, not stdlib getLogger()
tlogger = gen_mod.logger
tlogger.addHandler(handler)
tlogger.setLevel(logging.DEBUG)

import warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    from transformers.utils.generic import check_model_inputs

    def dummy(self, x=None):
        return x

    check_model_inputs(dummy)

log_out = buf.getvalue().lower()
warn_out = " ".join(str(x.message).lower() for x in w)
combined = log_out + " " + warn_out

keywords = ["deprecat", "rename", "merge_with_config_defaults", "check_model_inputs"]
assert any(kw in combined for kw in keywords), (
    f"Expected deprecation/rename warning; got log={log_out!r} warnings={warn_out!r}"
)
print("OK")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Deprecation warning test failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_merge_with_config_defaults_unaffected():
    """merge_with_config_defaults still works correctly after alias addition."""
    from transformers.utils.generic import merge_with_config_defaults

    class FakeConfig:
        use_cache = False

    class FakeModel:
        def __init__(self):
            self.config = FakeConfig()
            self.training = False

        @merge_with_config_defaults
        def forward(self, use_cache=None):
            return {"use_cache": use_cache}

    m = FakeModel()
    assert m.forward(use_cache=True)["use_cache"] is True
    assert m.forward()["use_cache"] is False


# [repo_tests] pass_to_pass
def test_generic_utilities_intact():
    """Existing utilities in generic.py still work."""
    from transformers.utils.generic import ExplicitEnum, PaddingStrategy

    assert PaddingStrategy("longest") == PaddingStrategy.LONGEST


# [repo_tests] pass_to_pass
def test_generic_module_imports():
    """All public utilities from generic.py can be imported (pass_to_pass)."""
    script = """import sys
sys.path.insert(0, '/workspace/transformers/src')
from transformers.utils.generic import (
    ExplicitEnum, PaddingStrategy, ModelOutput,
    flatten_dict, expand_dims, transpose, reshape, squeeze, to_py_obj,
    merge_with_config_defaults
)
print("All imports successful")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Import test failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_lint_full():
    """Repo's full ruff lint check passes on the codebase (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "ruff_check"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"ruff_check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_full():
    """Repo's full ruff format check passes on the codebase (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "ruff_format"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"ruff_format failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_generic_flatten_dict():
    """flatten_dict utility function works correctly (pass_to_pass)."""
    script = """import sys
sys.path.insert(0, '/workspace/transformers/src')
from transformers.utils.generic import flatten_dict
d = {"a": {"b": 1, "c": 2}, "d": 3}
result = flatten_dict(d)
expected = {"a.b": 1, "a.c": 2, "d": 3}
assert result == expected, f"flatten_dict failed: {result} != {expected}"
print("flatten_dict test OK")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"flatten_dict test failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_generic_explicit_enum():
    """ExplicitEnum utility class works correctly (pass_to_pass)."""
    script = """import sys
sys.path.insert(0, '/workspace/transformers/src')
from transformers.utils.generic import ExplicitEnum

class TestEnum(ExplicitEnum):
    A = "alpha"
    B = "beta"

assert TestEnum("alpha") == TestEnum.A
assert TestEnum("beta") == TestEnum.B
print("ExplicitEnum test OK")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"ExplicitEnum test failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:17 @ 2620c4ddd41afcc8d3b1d1134803bd418ffa45a7
def test_style_ruff_passes():
    """Code style is enforced in the CI — ruff must pass on the modified file."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "src/transformers/utils/generic.py"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_format_ruff_passes():
    """Code formatting is enforced in the CI — ruff format must pass on the modified file."""
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", "src/transformers/utils/generic.py"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_types_check():
    """Type annotations checker passes on src/transformers/utils (covers generic.py)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "types"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"types check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_init_isort():
    """Import ordering in __init__.py files is correct (CI check)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "init_isort"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"init_isort check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_inits_check():
    """Init file structure check passes (CI consistency check)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "inits"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"inits check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
