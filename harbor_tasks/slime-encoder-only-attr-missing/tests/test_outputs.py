"""
Task: slime-encoder-only-attr-missing
Repo: THUDM/slime @ 6f70479966749e258ba0b20341e2c4b88ea094f1
PR:   1741

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/sglang_utils/sglang_engine.py"

# ---------------------------------------------------------------------------
# Mock external dependencies so we can import the target module.
# The sglang, ray, requests, etc. packages are not installed in the test
# container — only the slime source tree is present.
# ---------------------------------------------------------------------------
for _mod_name in [
    "requests", "sglang", "sglang.srt", "sglang.srt.server_args",
    "sglang.srt.utils", "sglang_router", "packaging", "packaging.version",
    "urllib3", "urllib3.exceptions", "ray",
    "slime.ray", "slime.ray.ray_actor",
    "slime.utils", "slime.utils.http_utils",
    "sglang.srt.disaggregation",
    "sglang.srt.entrypoints",
]:
    sys.modules.setdefault(_mod_name, MagicMock())

# Distinguishable mock modules for the two conditional import paths
_encode_mod = types.ModuleType("sglang.srt.disaggregation.encode_server")
_http_mod = types.ModuleType("sglang.srt.entrypoints.http_server")


def _encode_launch_server(*a, **kw):
    pass


_encode_launch_server._path = "encode"


def _http_launch_server(*a, **kw):
    pass


_http_launch_server._path = "http"

_encode_mod.launch_server = _encode_launch_server
_http_mod.launch_server = _http_launch_server

sys.modules["sglang.srt.disaggregation.encode_server"] = _encode_mod
sys.modules["sglang.srt.entrypoints.http_server"] = _http_mod

# Patch multiprocessing.Process to track target without spawning
import multiprocessing as _mp


class _TrackingProcess:
    """Records the target function passed to Process() without actually spawning."""

    last_target = None

    def __init__(self, target=None, args=(), kwargs=None):
        _TrackingProcess.last_target = target

    def start(self):
        pass

    def is_alive(self):
        return True


_mp.Process = _TrackingProcess
_mp.set_start_method = lambda *a, **kw: None

from slime.backends.sglang_utils.sglang_engine import launch_server_process


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_crash_missing_encoder_only():
    """launch_server_process must not raise AttributeError when encoder_only is absent."""

    class Args:
        host = "127.0.0.1"
        node_rank = 1
        api_key = None

    # Args has no encoder_only attribute — must not crash
    launch_server_process(Args())


# [pr_diff] fail_to_pass
def test_missing_attr_defaults_to_http():
    """When encoder_only is absent, must fall back to http_server import path."""

    class Args:
        host = "127.0.0.1"
        node_rank = 1
        api_key = None

    _TrackingProcess.last_target = None
    launch_server_process(Args())
    assert _TrackingProcess.last_target is not None, "No process target was set"
    assert getattr(_TrackingProcess.last_target, "_path", None) == "http", (
        f"Expected http_server path when encoder_only is missing, "
        f"got {getattr(_TrackingProcess.last_target, '_path', 'unknown')}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_encoder_only_true_uses_encode_server():
    """When encoder_only=True, must use encode_server import path."""

    class Args:
        host = "127.0.0.1"
        node_rank = 1
        api_key = None
        encoder_only = True

    _TrackingProcess.last_target = None
    launch_server_process(Args())
    assert _TrackingProcess.last_target is not None, "No process target was set"
    assert getattr(_TrackingProcess.last_target, "_path", None) == "encode", (
        f"Expected encode_server path when encoder_only=True, "
        f"got {getattr(_TrackingProcess.last_target, '_path', 'unknown')}"
    )


# [pr_diff] pass_to_pass
def test_encoder_only_false_uses_http_server():
    """When encoder_only=False, must use http_server import path."""

    class Args:
        host = "127.0.0.1"
        node_rank = 1
        api_key = None
        encoder_only = False

    _TrackingProcess.last_target = None
    launch_server_process(Args())
    assert _TrackingProcess.last_target is not None, "No process target was set"
    assert getattr(_TrackingProcess.last_target, "_path", None) == "http", (
        f"Expected http_server path when encoder_only=False, "
        f"got {getattr(_TrackingProcess.last_target, '_path', 'unknown')}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """launch_server_process must create a process with a real callable target."""

    class Args:
        host = "127.0.0.1"
        node_rank = 1
        api_key = None

    _TrackingProcess.last_target = None
    launch_server_process(Args())
    assert _TrackingProcess.last_target is not None, "Function is a stub — no process created"
    assert callable(_TrackingProcess.last_target), "Process target must be callable"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base commit
# ---------------------------------------------------------------------------


def _ensure_ruff():
    """Install ruff if not already available."""
    try:
        import ruff  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff", "-q"],
            capture_output=True,
            timeout=60,
        )


# [repo_tests] pass_to_pass
def test_repo_ruff():
    """Repo's ruff linting passes (pass_to_pass)."""
    _ensure_ruff()
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "slime", "slime_plugins"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff linting failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def _ensure_isort():
    """Install isort if not already available."""
    try:
        import isort  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "isort", "-q"],
            capture_output=True,
            timeout=60,
        )


# [repo_tests] pass_to_pass
def test_repo_isort():
    """Repo's isort import sorting check passes (pass_to_pass)."""
    _ensure_isort()
    r = subprocess.run(
        [sys.executable, "-m", "isort", "--check-only", "--profile=black", "slime", "slime_plugins"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_py_compile():
    """All Python files in the repo compile without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c",
         "import py_compile; import sys; import os; \n"
         "errors = []\n"
         "for root, dirs, files in os.walk('slime'):\n"
         "    for f in files:\n"
         "        if f.endswith('.py'):\n"
         "            path = os.path.join(root, f)\n"
         "            try:\n"
         "                py_compile.compile(path, doraise=True)\n"
         "            except Exception as e:\n"
         "                errors.append(f'{path}: {e}')\n"
         "if errors:\n"
         "    print('\\n'.join(errors))\n"
         "    sys.exit(1)\n"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_package_imports():
    """The slime package can be imported without errors (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c", "import slime; print('slime imported successfully')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )


    assert r.returncode == 0, f"Package import failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

def _ensure_precommit():
    """Install pre-commit if not already available."""
    try:
        import precommit  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit", "-q"],
            capture_output=True,
            timeout=60,
        )


# [repo_tests] pass_to_pass
def test_repo_precommit_check_yaml():
    """Repo's YAML files are valid (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "check-yaml", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-yaml failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_check_added_large_files():
    """Repo has no unexpectedly large files (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "check-added-large-files", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-added-large-files failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_detect_private_key():
    """Repo has no private keys committed (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "detect-private-key", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"detect-private-key failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_isort():
    """Repo's isort import ordering passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "isort", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"isort pre-commit failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_autoflake():
    """Repo's autoflake unused import check passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "autoflake", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"autoflake pre-commit failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_precommit_black():
    """Repo's black formatting passes (pass_to_pass)."""
    _ensure_precommit()
    r = subprocess.run(
        [sys.executable, "-m", "pre_commit", "run", "black", "--all-files"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"black pre-commit failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def _ensure_pytest_deps():
    """Install pytest and dependencies if not already available."""
    try:
        import pytest  # noqa: F401
        import yaml  # noqa: F401
        import omegaconf  # noqa: F401
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pytest", "pyyaml", "omegaconf", "-q"],
            capture_output=True,
            timeout=60,
        )


# [repo_tests] pass_to_pass
def test_repo_sglang_config_update_weights_explicit():
    """SglangConfig correctly parses explicit update_weights values (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/utils/test_sglang_config.py::TestSglangConfigUpdateWeights::test_update_weights_explicit_false", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SglangConfig explicit weights test failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_sglang_config_multi_model_gpus():
    """SglangConfig correctly sums GPUs across multiple models (pass_to_pass)."""
    _ensure_pytest_deps()
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/utils/test_sglang_config.py::TestSglangConfigUpdateWeights::test_multi_model_total_gpus", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SglangConfig multi-model GPUs test failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
