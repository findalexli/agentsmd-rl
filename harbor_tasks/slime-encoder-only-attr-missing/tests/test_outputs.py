"""
Task: slime-encoder-only-attr-missing
Repo: THUDM/slime @ 6f70479966749e258ba0b20341e2c4b88ea094f1
PR:   1741

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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
