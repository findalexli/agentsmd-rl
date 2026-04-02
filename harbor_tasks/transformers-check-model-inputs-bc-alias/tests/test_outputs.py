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
    """check_model_inputs as decorator produces identical results to merge_with_config_defaults."""
    from transformers.utils.generic import check_model_inputs, merge_with_config_defaults

    class FakeConfig:
        use_cache = True
        output_attentions = False

    class Model1:
        def __init__(self):
            self.config = FakeConfig()
            self.training = False

        @check_model_inputs
        def forward(self, use_cache=None, output_attentions=None):
            return {"use_cache": use_cache, "output_attentions": output_attentions}

    class Model2:
        def __init__(self):
            self.config = FakeConfig()
            self.training = False

        @merge_with_config_defaults
        def forward(self, use_cache=None, output_attentions=None):
            return {"use_cache": use_cache, "output_attentions": output_attentions}

    m1 = Model1()
    m2 = Model2()

    # No kwargs — should pull from config
    r1 = m1.forward()
    r2 = m2.forward()
    assert r1 == r2, f"No-args results differ: {r1} vs {r2}"
    assert r1["use_cache"] is True
    assert r1["output_attentions"] is False

    # Explicit kwargs override config
    r1 = m1.forward(use_cache=False)
    r2 = m2.forward(use_cache=False)
    assert r1 == r2, f"Explicit kwarg results differ: {r1} vs {r2}"
    assert r1["use_cache"] is False

    # Mixed — some explicit, some from config
    r1 = m1.forward(output_attentions=True)
    r2 = m2.forward(output_attentions=True)
    assert r1 == r2, f"Mixed results differ: {r1} vs {r2}"
    assert r1["use_cache"] is True
    assert r1["output_attentions"] is True


# [pr_diff] fail_to_pass
def test_decorator_returns_functional_wrapper():
    """check_model_inputs returns a working wrapper, not None or the original function."""
    from transformers.utils.generic import check_model_inputs

    class Cfg:
        val = 42

    class M:
        def __init__(self):
            self.config = Cfg()
            self.training = False

        @check_model_inputs
        def forward(self, val=None):
            return val

    m = M()
    # Must pull config default when no arg passed
    assert m.forward() == 42, "Expected config default 42"
    # Explicit override must take precedence
    assert m.forward(val=99) == 99, "Expected explicit override 99"
    # Different override value to verify not hardcoded
    assert m.forward(val=0) == 0, "Expected explicit override 0"


# [pr_diff] fail_to_pass
def test_deprecation_warning_emitted():
    """check_model_inputs emits a deprecation/rename warning when called.

    Uses subprocess for isolation: warning_once caches on the logger object,
    so running in-process after other tests would suppress the warning even
    if the alias is present. A fresh process guarantees a clean cache.
    """
    script = """\
import sys, logging, io
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
