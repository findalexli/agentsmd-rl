"""
Task: areal-rtensor-session-retry
Repo: inclusionAI/AReaL @ 9639749e700ea278e0617589391cc3dda6ec3a5c
PR:   1075

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import asyncio
import importlib
import logging
import subprocess
import sys
import time
import types
from pathlib import Path

REPO = "/repo"

# ---------------------------------------------------------------------------
# Mock heavy dependencies to avoid importing the full areal package tree
# ---------------------------------------------------------------------------

# Mock ray (used by RayRTensorBackend which we don't test)
_ray_mock = types.ModuleType("ray")
_ray_mock.ObjectRef = object
_ray_mock.is_initialized = lambda: False
_ray_mock.put = lambda x: x
_ray_mock.get = lambda x: x
_ray_mock.internal = types.ModuleType("ray.internal")
_ray_mock.internal.free = lambda x: None
sys.modules["ray"] = _ray_mock
sys.modules["ray.internal"] = _ray_mock.internal

# Pre-populate areal package hierarchy to prevent __init__.py from importing
# the entire dependency tree (flask, controllers, etc.)
for _pkg, _path in [
    ("areal", "/repo/areal"),
    ("areal.infra", "/repo/areal/infra"),
    ("areal.infra.rpc", "/repo/areal/infra/rpc"),
    ("areal.infra.utils", "/repo/areal/infra/utils"),
    ("areal.utils", "/repo/areal/utils"),
]:
    _m = types.ModuleType(_pkg)
    _m.__path__ = [_path]
    _m.__package__ = _pkg
    sys.modules[_pkg] = _m

# Load only the submodules rtensor actually needs
for _mod in ["areal.utils.logging", "areal.infra.utils.concurrent", "areal.infra.utils.http"]:
    sys.modules[_mod] = importlib.import_module(_mod)

# Mock serialization module (needs pydantic which may not be installed)
_ser_mock = types.ModuleType("areal.infra.rpc.serialization")
_ser_mock.deserialize_value = lambda x: x  # identity stub
sys.modules["areal.infra.rpc.serialization"] = _ser_mock

import aiohttp


# ---------------------------------------------------------------------------
# Helper: load rtensor module (fresh import each time is fine since it's cached)
# ---------------------------------------------------------------------------

def _load_rtensor():
    """Import rtensor module, handling both base and patched versions."""
    # Force reimport to pick up any patches applied during test
    if "areal.infra.rpc.rtensor" in sys.modules:
        return sys.modules["areal.infra.rpc.rtensor"]
    return importlib.import_module("areal.infra.rpc.rtensor")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        py_compile.compile(f, doraise=True)


# [repo_tests] pass_to_pass
def test_ruff_lint_check():
    """Modified files must pass ruff linting (repo CI standard)."""
    r = subprocess.run(
        ["ruff", "check", "areal/infra/rpc/rtensor.py", "areal/utils/logging.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_format_check():
    """Modified files must be formatted according to ruff (repo CI standard)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/infra/rpc/rtensor.py", "areal/utils/logging.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_create_session_method_exists():
    """HttpRTensorBackend has a _create_session method."""
    mod = _load_rtensor()
    backend = mod.HttpRTensorBackend()
    assert hasattr(backend, "_create_session"), (
        "HttpRTensorBackend must have a _create_session method"
    )
    assert callable(backend._create_session), "_create_session must be callable"


# [pr_diff] fail_to_pass
def test_create_session_configuration():
    """_create_session configures timeout, read buffer, and TCPConnector."""
    async def _run():
        mod = _load_rtensor()
        from areal.infra.utils.http import DEFAULT_REQUEST_TIMEOUT

        backend = mod.HttpRTensorBackend()
        session = backend._create_session()
        try:
            # Verify timeout is set to the shared default
            assert session.timeout.total == DEFAULT_REQUEST_TIMEOUT, (
                f"timeout.total={session.timeout.total}, expected {DEFAULT_REQUEST_TIMEOUT}"
            )
            # Verify large read buffer (>= 10MB)
            assert session._read_bufsize >= 10 * 1024 * 1024, (
                f"read_bufsize={session._read_bufsize}, expected >= 10MB"
            )
            # Verify TCPConnector is used (not default connector)
            assert isinstance(session.connector, aiohttp.TCPConnector), (
                f"connector type={type(session.connector).__name__}, expected TCPConnector"
            )
        finally:
            await session.close()

    asyncio.run(_run())


# [pr_diff] fail_to_pass
def test_fetch_tensor_retries_on_transient_failure():
    """_fetch_tensor retries transient errors with delays between attempts."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session = backend._create_session()
        try:
            delay = 0.05

            # 1 retry → immediate failure, no sleep
            t0 = time.monotonic()
            try:
                await backend._fetch_tensor(
                    session, "shard-a", "127.0.0.1:1",
                    max_retries=1, retry_delay=delay,
                )
            except Exception:
                pass
            t1 = time.monotonic() - t0

            # 3 retries → should sleep 2 times (between attempts)
            t0 = time.monotonic()
            try:
                await backend._fetch_tensor(
                    session, "shard-b", "127.0.0.1:1",
                    max_retries=3, retry_delay=delay,
                )
            except Exception:
                pass
            t3 = time.monotonic() - t0

            # 5 retries → should sleep 4 times
            t0 = time.monotonic()
            try:
                await backend._fetch_tensor(
                    session, "shard-c", "127.0.0.1:1",
                    max_retries=5, retry_delay=delay,
                )
            except Exception:
                pass
            t5 = time.monotonic() - t0

            # More retries must take proportionally longer
            assert t3 > t1 + delay, (
                f"3-retry ({t3:.3f}s) not slower than 1-retry ({t1:.3f}s) + delay"
            )
            assert t5 > t3 + delay, (
                f"5-retry ({t5:.3f}s) not slower than 3-retry ({t3:.3f}s) + delay"
            )
        finally:
            await session.close()

    asyncio.run(_run())


# [pr_diff] fail_to_pass
def test_fetch_tensor_error_message_after_retries():
    """After exhausting retries, error includes attempt count and last error."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session = backend._create_session()
        try:
            import pytest

            # Test with different retry counts to ensure the message is dynamic
            for retries in [2, 3, 5]:
                try:
                    await backend._fetch_tensor(
                        session, "fake-shard", "127.0.0.1:1",
                        max_retries=retries, retry_delay=0.01,
                    )
                    raise AssertionError("Should have raised RuntimeError")
                except RuntimeError as e:
                    msg = str(e)
                    assert str(retries) in msg, (
                        f"Error should mention retry count {retries}: {msg}"
                    )
                    lower = msg.lower()
                    assert any(w in lower for w in ["error", "fail", "attempt"]), (
                        f"Error should include failure context: {msg}"
                    )
        finally:
            await session.close()

    asyncio.run(_run())


# [pr_diff] fail_to_pass
def test_fetch_uses_create_session():
    """fetch() uses _create_session instead of bare aiohttp.ClientSession()."""
    import ast

    # AST-only because: need to check method body of fetch() for specific call patterns
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)

    # Find the HttpRTensorBackend class and its fetch method
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
            # Get the source lines for the fetch method and everything nested in it
            fetch_src = None
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "fetch":
                    fetch_src = ast.get_source_segment(src, item)
                    break

            assert fetch_src is not None, "fetch() method not found in HttpRTensorBackend"
            assert "_create_session" in fetch_src, (
                "fetch() should use self._create_session()"
            )
            assert "aiohttp.ClientSession()" not in fetch_src, (
                "fetch() should not use bare aiohttp.ClientSession()"
            )
            return

    raise AssertionError("HttpRTensorBackend class not found")


# [pr_diff] fail_to_pass
def test_delete_uses_create_session():
    """delete() uses _create_session instead of bare aiohttp.ClientSession()."""
    import ast

    # AST-only because: need to check method body of delete() for specific call patterns
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
            delete_src = None
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "delete":
                    delete_src = ast.get_source_segment(src, item)
                    break

            assert delete_src is not None, "delete() method not found in HttpRTensorBackend"
            assert "_create_session" in delete_src, (
                "delete() should use self._create_session()"
            )
            assert "aiohttp.ClientSession()" not in delete_src, (
                "delete() should not use bare aiohttp.ClientSession()"
            )
            return

    raise AssertionError("HttpRTensorBackend class not found")


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_fetch_empty_returns_empty():
    """fetch([]) returns an empty list without creating a session."""
    mod = _load_rtensor()
    backend = mod.HttpRTensorBackend()
    result = backend.fetch([])
    assert result == [], f"Expected [], got {result}"


# [pr_diff] fail_to_pass
def test_create_session_returns_real_session():
    """_create_session returns a ClientSession with non-default timeout."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session = backend._create_session()
        try:
            assert isinstance(session, aiohttp.ClientSession), (
                f"Expected ClientSession, got {type(session)}"
            )
            # Default aiohttp timeout.total is 300; configured should differ
            assert session.timeout.total != 300, (
                "Timeout is still default (300) — session not properly configured"
            )
        finally:
            await session.close()

    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ 9639749e
def test_no_wildcard_imports():
    """No wildcard imports in modified files."""
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        content = Path(f).read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("from ") and "import *" in stripped:
                raise AssertionError(f"Wildcard import at {f}:{i}: {stripped}")


# [agent_config] fail_to_pass — AGENTS.md:89-91 @ 9639749e
def test_logger_registered_in_color_map():
    """HttpRTensor logger is registered in areal/utils/logging.py color map."""
    content = Path("/repo/areal/utils/logging.py").read_text()
    assert '"HttpRTensor"' in content or "'HttpRTensor'" in content, (
        "HttpRTensor not registered in logging.py color map"
    )


# [agent_config] fail_to_pass — AGENTS.md:89-91 @ 9639749e
def test_module_has_logger():
    """rtensor module defines a module-level Logger instance via areal.utils.logging."""
    mod = _load_rtensor()
    found = any(isinstance(obj, logging.Logger) for obj in vars(mod).values())
    assert found, "No module-level Logger found in rtensor module"


# [agent_config] pass_to_pass — AGENTS.md:89-91 @ 9639749e
def test_no_print_in_rtensor():
    """No print() calls in rtensor.py (must use logger instead)."""
    import ast

    # AST-only because: need to distinguish print() calls from string occurrences of "print"
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                raise AssertionError(
                    f"print() call at line {node.lineno} — use logger instead"
                )


# [agent_config] fail_to_pass — AGENTS.md:99 @ 9639749e
def test_create_session_has_return_type_annotation():
    """_create_session has an explicit return type annotation (explicit type hints required)."""
    import ast

    # AST-only because: return type annotations are not visible at runtime via inspect
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "_create_session":
                    assert item.returns is not None, (
                        "_create_session must have a return type annotation — "
                        "AGENTS.md requires explicit type hints"
                    )
                    return
    raise AssertionError("_create_session method not found in HttpRTensorBackend")


# [agent_config] pass_to_pass — AGENTS.md:31 @ 9639749e
def test_no_hardcoded_endpoints():
    """No hardcoded IP addresses or URLs in rtensor.py (must use parameters)."""
    import re

    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    # Look for hardcoded http:// URLs with literal IPs (not f-string interpolations)
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Match literal http://IP:port patterns (not in f-strings using {})
        matches = re.findall(r'http://\d+\.\d+\.\d+\.\d+', stripped)
        for m in matches:
            # Allow if it's inside an f-string interpolation context
            if "{" not in stripped:
                raise AssertionError(
                    f"Hardcoded endpoint at line {i}: {m}"
                )
