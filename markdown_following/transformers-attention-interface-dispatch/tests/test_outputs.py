"""Tests for PR #45598: Align latest model attention function dispatch."""

import os
import subprocess
import sys
import tempfile

REPO = "/workspace/transformers"

AFFECTED_FILES = [
    "src/transformers/models/gemma4/modeling_gemma4.py",
    "src/transformers/models/gemma4/modular_gemma4.py",
    "src/transformers/models/modernbert/modeling_modernbert.py",
    "src/transformers/models/modernbert/modular_modernbert.py",
    "src/transformers/models/moonshine_streaming/modeling_moonshine_streaming.py",
    "src/transformers/models/moonshine_streaming/modular_moonshine_streaming.py",
]

ATTENTION_CLASSES = [
    ("transformers.models.gemma4.modeling_gemma4", "Gemma4TextAttention"),
    ("transformers.models.modernbert.modeling_modernbert", "ModernBertAttention"),
    ("transformers.models.moonshine_streaming.modeling_moonshine_streaming", "MoonshineStreamingEncoderAttention"),
]


def _import_forward_source(module_name, class_name):
    import importlib
    import inspect
    mod = importlib.import_module(module_name)
    cls = getattr(mod, class_name)
    return inspect.getsource(cls.forward)


def test_get_interface_used_in_forward():
    """Each affected attention forward method uses ALL_ATTENTION_FUNCTIONS.get_interface()."""
    sys.path.insert(0, os.path.join(REPO, "src"))
    for mod_name, cls_name in ATTENTION_CLASSES:
        src = _import_forward_source(mod_name, cls_name)
        assert "get_interface(" in src, f"{cls_name}.forward: get_interface() call not found"


def test_old_dispatch_removed_from_forward():
    """No affected attention forward method uses the old manual dispatch pattern."""
    sys.path.insert(0, os.path.join(REPO, "src"))
    for mod_name, cls_name in ATTENTION_CLASSES:
        src = _import_forward_source(mod_name, cls_name)
        assert '_attn_implementation != "eager"' not in src, (
            f"{cls_name}.forward: old dispatch pattern still present"
        )


def test_get_interface_behavior():
    """ALL_ATTENTION_FUNCTIONS.get_interface() dispatches correctly and validates keys."""
    sys.path.insert(0, os.path.join(REPO, "src"))
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS

    def my_default():
        return 42

    # "eager" returns the default callable
    assert ALL_ATTENTION_FUNCTIONS.get_interface("eager", my_default) is my_default

    # None returns the default with a warning (no KeyError)
    assert ALL_ATTENTION_FUNCTIONS.get_interface(None, my_default) is my_default

    # Valid registered implementation like "sdpa" returns the real function
    result = ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", my_default)
    assert result is not my_default
    assert callable(result)

    # Invalid/unregistered implementation raises KeyError
    try:
        ALL_ATTENTION_FUNCTIONS.get_interface("nonexistent_impl_xyz_test", my_default)
        assert False, "Should have raised KeyError for invalid implementation"
    except KeyError:
        pass


def test_ruff_check():
    """Changed files pass ruff style checks (ignoring pre-existing UP038 violations)."""
    r = subprocess.run(
        ["ruff", "check", "--ignore", "UP038"] + [os.path.join(REPO, f) for f in AFFECTED_FILES],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_model_attention_via_pytest():
    """Run attention dispatch behavioral tests under a real pytest runner."""
    pytest_script = '''import os, sys
sys.path.insert(0, "/workspace/transformers/src")

import importlib, inspect

ATTENTION_CLASSES = [
    ("transformers.models.gemma4.modeling_gemma4", "Gemma4TextAttention"),
    ("transformers.models.modernbert.modeling_modernbert", "ModernBertAttention"),
    ("transformers.models.moonshine_streaming.modeling_moonshine_streaming", "MoonshineStreamingEncoderAttention"),
]

def test_all_attention_functions_exists():
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    assert callable(ALL_ATTENTION_FUNCTIONS.get_interface)

def test_eager_returns_default():
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    def d(): return 99
    assert ALL_ATTENTION_FUNCTIONS.get_interface("eager", d) is d

def test_none_returns_default():
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    def d(): return 99
    assert ALL_ATTENTION_FUNCTIONS.get_interface(None, d) is d

def test_sdpa_is_registered():
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    result = ALL_ATTENTION_FUNCTIONS.get_interface("sdpa", lambda: None)
    assert result is not None
    assert callable(result)

def test_invalid_raises_keyerror():
    from transformers.modeling_utils import ALL_ATTENTION_FUNCTIONS
    try:
        ALL_ATTENTION_FUNCTIONS.get_interface("nonexistent_impl_xyz_test", lambda: None)
        assert False, "Expected KeyError"
    except KeyError:
        pass

def test_attention_modules_importable():
    for mod_name, cls_name in ATTENTION_CLASSES:
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        assert hasattr(cls, "forward"), f"{cls_name} missing forward method"
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(pytest_script)
        tmp_path = f.name
    try:
        r = subprocess.run(
            ["bash", "-lc", f"cd /workspace/transformers && python -m pytest {tmp_path} -v --tb=short"],
            capture_output=True, text=True, timeout=120,
        )
        assert r.returncode == 0, f"pytest dispatch tests failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    finally:
        os.unlink(tmp_path)

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_timestamps_verify_merge_commit_timestamp_is_older_t():
    """pass_to_pass | CI job 'Check timestamps' → step 'Verify `merge_commit` timestamp is older than the issue comment timestamp'"""
    r = subprocess.run(
        ["bash", "-lc", 'COMMENT_TIMESTAMP=$(date -d "${COMMENT_DATE}" +"%s")\necho "COMMENT_DATE: $COMMENT_DATE"\necho "COMMENT_TIMESTAMP: $COMMENT_TIMESTAMP"\nif [ $COMMENT_TIMESTAMP -le $PR_MERGE_COMMIT_TIMESTAMP ]; then\n  echo "Last commit on the pull request is newer than the issue comment triggering this run! Abort!";\n  exit -1;\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify `merge_commit` timestamp is older than the issue comment timestamp' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")