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
import os
import re
import subprocess
import sys
import time
import types
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

REPO = "/repo"

_ray_mock = types.ModuleType("ray")
_ray_mock.ObjectRef = object
_ray_mock.is_initialized = lambda: False
_ray_mock.put = lambda x: x
_ray_mock.get = lambda x: x
_ray_mock.internal = types.ModuleType("ray.internal")
_ray_mock.internal.free = lambda x: None
sys.modules["ray"] = _ray_mock
sys.modules["ray.internal"] = _ray_mock.internal

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

for _mod in ["areal.utils.logging", "areal.infra.utils.concurrent", "areal.infra.utils.http"]:
    sys.modules[_mod] = importlib.import_module(_mod)

_ser_mock = types.ModuleType("areal.infra.rpc.serialization")
_ser_mock.deserialize_value = lambda x: x
sys.modules["areal.infra.rpc.serialization"] = _ser_mock

import aiohttp


def _load_rtensor():
    if "areal.infra.rpc.rtensor" in sys.modules:
        return sys.modules["areal.infra.rpc.rtensor"]
    return importlib.import_module("areal.infra.rpc.rtensor")


def _find_session_method(backend):
    """Find any session creation method - returns a bound method."""
    for name, method in vars(backend.__class__).items():
        if callable(method) and not name.startswith("__") and "session" in name.lower():
            return method.__get__(backend, backend.__class__)
    return None


# ---------------------------------------------------------------------------
# Pass-to-pass (static / repo_tests)
# ---------------------------------------------------------------------------

def test_syntax_check():
    import py_compile
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        py_compile.compile(f, doraise=True)


def test_ruff_lint_check():
    r = subprocess.run(
        ["ruff", "check", "areal/infra/rpc/rtensor.py", "areal/utils/logging.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stdout}\n{r.stderr}"


def test_ruff_format_check():
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/infra/rpc/rtensor.py", "areal/utils/logging.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_no_large_files():
    max_size_kb = 1000
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        size_kb = os.path.getsize(f) / 1024
        assert size_kb <= max_size_kb, f"File {f} is too large ({size_kb:.1f}KB > {max_size_kb}KB)"


def test_no_private_keys():
    key_patterns = [
        r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
        r'-----BEGIN RSA PRIVATE KEY-----',
        r'-----BEGIN DSA PRIVATE KEY-----',
        r'-----BEGIN EC PRIVATE KEY-----',
        r'-----BEGIN OPENSSH PRIVATE KEY-----',
        r'-----BEGIN PRIVATE KEY-----',
        r'-----BEGIN ENCRYPTED PRIVATE KEY-----',
        r'PuTTY-User-Key-File-',
        r'BEGIN SSH2 ENCRYPTED PRIVATE KEY',
    ]
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        content = Path(f).read_text()
        for pattern in key_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            assert not matches, f"Potential private key detected in {f}: {pattern}"


def test_no_trailing_whitespace():
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        content = Path(f).read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if line.rstrip() != line:
                raise AssertionError(f"Trailing whitespace at {f}:{i}")


def test_files_end_with_newline():
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        content = Path(f).read_bytes()
        if content and not content.endswith(b'\n'):
            raise AssertionError(f"File {f} does not end with a newline")


def test_python_ast_valid():
    r = subprocess.run(
        ["python", "-c",
         "import ast; ast.parse(open('/repo/areal/infra/rpc/rtensor.py').read()); "
         "ast.parse(open('/repo/areal/utils/logging.py').read()); print('AST OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST validation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_session_method_exists():
    """HttpRTensorBackend has a session creation method (any name with 'session' in it)."""
    mod = _load_rtensor()
    backend = mod.HttpRTensorBackend()
    session_method = _find_session_method(backend)
    assert session_method is not None, (
        "HttpRTensorBackend must have a callable method with 'session' in the name "
        "that produces a configured aiohttp.ClientSession"
    )
    assert callable(session_method), "Session creation method must be callable"


def test_session_configuration_timeout():
    """Created session has non-default timeout (not 300s)."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        assert session_method is not None, "No session creation method found on HttpRTensorBackend"
        session = session_method()
        try:
            assert session.timeout.total != 300, (
                f"timeout.total is {session.timeout.total}, expected non-default (not 300)"
            )
        finally:
            await session.close()
    asyncio.run(_run())


def test_session_configuration_read_buffer():
    """Created session has large read buffer (>= 10MB)."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        assert session_method is not None, "No session creation method found"
        session = session_method()
        try:
            assert session._read_bufsize >= 10 * 1024 * 1024, (
                f"read_bufsize={session._read_bufsize}, expected >= 10MB"
            )
        finally:
            await session.close()
    asyncio.run(_run())


def test_session_configuration_connector():
    """Created session uses TCPConnector (not default None)."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        assert session_method is not None, "No session creation method found"
        session = session_method()
        try:
            assert isinstance(session.connector, aiohttp.TCPConnector), (
                f"connector type={type(session.connector).__name__}, expected TCPConnector"
            )
        finally:
            await session.close()
    asyncio.run(_run())


def test_fetch_tensor_retries_on_transient_failure():
    """_fetch_tensor retries on aiohttp.ClientError with configurable delay."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        session = session_method()
        try:
            attempt_number = [0]

            class MockCtx:
                def __init__(self, fail_count):
                    self._fail_count = fail_count
                    self.status = 200
                async def __aenter__(self):
                    return self
                async def __aexit__(self, *args):
                    pass
                async def read(self):
                    n = attempt_number[0]
                    attempt_number[0] += 1
                    if n < self._fail_count:
                        raise aiohttp.ClientError(f"Connection reset (attempt {n})")
                    return b'{}'

            class MockGet:
                def __init__(self, fail_count):
                    self._fail_count = fail_count
                def __call__(self, url, **kwargs):
                    return MockCtx(self._fail_count)

            mock_get = MockGet(fail_count=2)
            session.get = mock_get

            delay = 0.15
            t0 = time.monotonic()
            result = await backend._fetch_tensor(
                session, "test-shard", "127.0.0.1:1",
                max_retries=3, retry_delay=delay,
            )
            elapsed = time.monotonic() - t0

            assert elapsed >= 2 * delay - 0.01, (
                f"Elapsed {elapsed:.3f}s < {2*delay - 0.01}s expected for 2 retry delays. "
                f"Attempt count was {attempt_number[0]}"
            )
            assert attempt_number[0] == 3, f"Expected 3 attempts, got {attempt_number[0]}"
        finally:
            await session.close()
    asyncio.run(_run())


def test_fetch_tensor_error_message_after_retries():
    """After exhausting retries, error message includes the attempt count."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        session = session_method()
        try:
            class MockCtx:
                def __init__(self):
                    self.status = 200
                async def __aenter__(self):
                    return self
                async def __aexit__(self, *args):
                    pass
                async def read(self):
                    raise aiohttp.ClientError("Connection refused")

            class MockGet:
                def __call__(self, url, **kwargs):
                    return MockCtx()

            session.get = MockGet()

            for retries in [2, 3, 5]:
                try:
                    await backend._fetch_tensor(
                        session, "fake-shard", "127.0.0.1:1",
                        max_retries=retries, retry_delay=0.01,
                    )
                    raise AssertionError(f"Should have raised for {retries} retries")
                except RuntimeError as e:
                    msg = str(e)
                    assert str(retries) in msg, (
                        f"Error message should mention retry count {retries}: {msg}"
                    )
        finally:
            await session.close()
    asyncio.run(_run())


def test_fetch_and_delete_use_session_method():
    """fetch() and delete() both use the session creation method - not bare aiohttp.ClientSession()."""
    import ast

    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
            # Check fetch method
            fetch_src = None
            delete_src = None
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == "fetch":
                        fetch_src = ast.get_source_segment(src, item)
                    elif item.name == "delete":
                        delete_src = ast.get_source_segment(src, item)

            # Verify fetch does not use bare aiohttp.ClientSession()
            if fetch_src:
                assert "aiohttp.ClientSession()" not in fetch_src, (
                    "fetch() should use a session creation method, not bare aiohttp.ClientSession()"
                )
            # Verify delete does not use bare aiohttp.ClientSession()
            if delete_src:
                assert "aiohttp.ClientSession()" not in delete_src, (
                    "delete() should use a session creation method, not bare aiohttp.ClientSession()"
                )
            return

    raise AssertionError("HttpRTensorBackend class not found")


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

def test_fetch_empty_returns_empty():
    """fetch([]) returns an empty list without creating a session."""
    mod = _load_rtensor()
    backend = mod.HttpRTensorBackend()
    result = backend.fetch([])
    if asyncio.iscoroutine(result):
        result = asyncio.run(result)
    assert result == [], f"Expected [], got {result}"


def test_create_session_returns_real_session():
    """Session creation method returns a ClientSession with non-default config."""
    async def _run():
        mod = _load_rtensor()
        backend = mod.HttpRTensorBackend()
        session_method = _find_session_method(backend)
        assert session_method is not None, "No session creation method found"
        session = session_method()
        try:
            assert isinstance(session, aiohttp.ClientSession), (
                f"Expected ClientSession, got {type(session)}"
            )
            assert session.timeout.total != 300, (
                "Timeout is still default (300) — session not properly configured"
            )
        finally:
            await session.close()
    asyncio.run(_run())


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_no_wildcard_imports():
    """No wildcard imports in modified files."""
    for f in ["/repo/areal/infra/rpc/rtensor.py", "/repo/areal/utils/logging.py"]:
        content = Path(f).read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("from ") and "import *" in stripped:
                raise AssertionError(f"Wildcard import at {f}:{i}: {stripped}")


def test_logger_registered_in_color_map():
    """HttpRTensor logger is registered in areal/utils/logging.py color map."""
    content = Path("/repo/areal/utils/logging.py").read_text()
    assert '"HttpRTensor"' in content or "'HttpRTensor'" in content, (
        "HttpRTensor not registered in logging.py color map"
    )


def test_module_has_logger():
    """rtensor module defines a module-level Logger instance via areal.utils.logging."""
    mod = _load_rtensor()
    found = any(isinstance(obj, logging.Logger) for obj in vars(mod).values())
    assert found, "No module-level Logger found in rtensor module"


def test_no_print_in_rtensor():
    """No print() calls in rtensor.py (must use logger instead)."""
    import ast
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                raise AssertionError(
                    f"print() call at line {node.lineno} — use logger instead"
                )


def test_session_creation_method_has_return_annotation():
    """Session creation method has an explicit return type annotation."""
    import ast
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "HttpRTensorBackend":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ("_create_session", "create_session", "_make_session", "make_session"):
                    assert item.returns is not None, (
                        f"{item.name} must have a return type annotation — "
                        "AGENTS.md requires explicit type hints"
                    )
                    return
    raise AssertionError("Session creation method not found in HttpRTensorBackend")


def test_no_hardcoded_endpoints():
    """No hardcoded IP addresses or URLs in rtensor.py."""
    import re
    src = Path("/repo/areal/infra/rpc/rtensor.py").read_text()
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        matches = re.findall(r'http://\d+\.\d+\.\d+\.\d+', stripped)
        for m in matches:
            if "{" not in stripped:
                raise AssertionError(f"Hardcoded endpoint at line {i}: {m}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_install_test_verify_package_import():
    """pass_to_pass | CI job 'Install test' → step 'Verify package import'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run python -c "import areal; print(f\'areal version: {areal.__version__}\')"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify package import' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_verify_core_modules_are_importable():
    """pass_to_pass | CI job 'Install test' → step 'Verify core modules are importable'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run python -c "'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify core modules are importable' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_build_wheel():
    """pass_to_pass | CI job 'Install test' → step 'Build wheel'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv build --wheel'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_install_test_verify_wheel_artifact():
    """pass_to_pass | CI job 'Install test' → step 'Verify wheel artifact'"""
    r = subprocess.run(
        ["bash", "-lc", 'python -m zipfile -l dist/*.whl | head -20'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify wheel artifact' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_the_book():
    """pass_to_pass | CI job 'build' → step 'Build the book'"""
    r = subprocess.run(
        ["bash", "-lc", './build_all.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build the book' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")