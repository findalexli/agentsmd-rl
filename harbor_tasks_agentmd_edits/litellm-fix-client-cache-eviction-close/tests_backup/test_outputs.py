"""
Task: litellm-fix-client-cache-eviction-close
Repo: BerriAI/litellm @ bf9c96b91205d17e13d9c7ea54d396005db5bc63
PR:   22925

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/litellm"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo context."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _run_shell(cmd: list, timeout: int = 60, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Execute a shell command in the repo context."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified Python files parse without errors."""
    handler = Path(f"{REPO}/litellm/caching/llm_caching_handler.py")
    tree = ast.parse(handler.read_text())
    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    assert "LLMClientCache" in class_names


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD tests that pass on base and after fix
# ---------------------------------------------------------------------------


def test_repo_ruff_caching():
    """Ruff linting passes on litellm/caching/ directory (pass_to_pass)."""
    # Skip if ruff is not installed
    if shutil.which("ruff") is None:
        pytest.skip("ruff not installed")

    r = _run_shell(
        ["ruff", "check", "litellm/caching/", "--output-format=concise"],
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_caching_handler_tests():
    """Repo's caching handler unit tests pass (pass_to_pass)."""
    # Skip if pytest is not available
    if shutil.which("pytest") is None:
        pytest.skip("pytest not installed")

    r = _run_shell(
        ["pytest", "tests/test_litellm/caching/test_llm_caching_handler.py", "-v", "--tb=short"],
        timeout=120,
    )
    assert r.returncode == 0, f"Caching handler tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_import_caching():
    """Caching module imports work correctly (pass_to_pass)."""
    r = _run_py("""
from litellm.caching import llm_caching_handler
from litellm.caching.llm_caching_handler import LLMClientCache
print("All caching imports OK")
""")
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "All caching imports OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_remove_key_does_not_close_async_client():
    """Evicting an async client from LLMClientCache must NOT close it.

    On the base commit, _remove_key schedules aclose() via create_task(),
    which closes the client. The fix removes the override entirely.
    """
    r = _run_py("""
import sys, asyncio
sys.path.insert(0, '/workspace/litellm')
from litellm.caching.llm_caching_handler import LLMClientCache

async def main():
    cache = LLMClientCache(max_size_in_memory=10)

    class MockAsyncClient:
        def __init__(self):
            self.closed = False
        async def aclose(self):
            self.closed = True

    mock_client = MockAsyncClient()
    cache.cache_dict["test-key"] = mock_client
    cache.ttl_dict["test-key"] = 0

    cache._remove_key("test-key")
    # Let the event loop drain any background close tasks
    await asyncio.sleep(0.1)

    assert not mock_client.closed, (
        "Async client was closed on eviction — causes "
        "'Cannot send a request, as the client has been closed' in production"
    )
    assert "test-key" not in cache.cache_dict
    assert "test-key" not in cache.ttl_dict
    print("PASS")

asyncio.run(main())
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}\nstdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_remove_key_does_not_close_sync_client():
    """Evicting a sync client from LLMClientCache must NOT close it.

    On the base commit, _remove_key calls close() directly on sync clients.
    The fix removes the override so the parent class just removes the key.
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/workspace/litellm')
from litellm.caching.llm_caching_handler import LLMClientCache

cache = LLMClientCache(max_size_in_memory=10)

class MockSyncClient:
    def __init__(self):
        self.closed = False
    def close(self):
        self.closed = True

mock_client = MockSyncClient()
cache.cache_dict["test-key"] = mock_client
cache.ttl_dict["test-key"] = 0

cache._remove_key("test-key")

assert not mock_client.closed, "Sync client was closed on eviction"
assert "test-key" not in cache.cache_dict
print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}\nstdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_eviction_does_not_close_async_clients():
    """When the cache is full and entries are evicted, clients stay open.

    Uses multiple clients and fills the cache beyond capacity to trigger
    LRU eviction. All evicted clients must remain open.
    """
    r = _run_py("""
import sys, asyncio
sys.path.insert(0, '/workspace/litellm')
from litellm.caching.llm_caching_handler import LLMClientCache

async def main():
    cache = LLMClientCache(max_size_in_memory=2, default_ttl=600)

    class MockAsyncClient:
        def __init__(self, name):
            self.name = name
            self.closed = False
        async def aclose(self):
            self.closed = True

    clients = []
    for i in range(5):
        c = MockAsyncClient(f"client-{i}")
        cache.set_cache(f"key-{i}", c)
        clients.append(c)

    # Only the last 2 should remain in cache (max_size=2)
    # But ALL clients (including evicted ones) must not be closed
    await asyncio.sleep(0.1)

    for c in clients:
        assert not c.closed, f"{c.name} was closed on eviction"
    print("PASS")

asyncio.run(main())
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}\nstdout: {r.stdout}"
    assert "PASS" in r.stdout


def test_remove_key_handles_plain_values():
    """_remove_key works correctly for non-client values (strings, dicts).

    Regression check: removing the override shouldn't break eviction of
    plain values that have no close()/aclose() methods.
    """
    r = _run_py("""
import sys
sys.path.insert(0, '/workspace/litellm')
from litellm.caching.llm_caching_handler import LLMClientCache

cache = LLMClientCache(max_size_in_memory=5)

cache.cache_dict["str-key"] = "hello"
cache.ttl_dict["str-key"] = 0
cache.cache_dict["dict-key"] = {"foo": "bar"}
cache.ttl_dict["dict-key"] = 0

cache._remove_key("str-key")
cache._remove_key("dict-key")

assert "str-key" not in cache.cache_dict
assert "dict-key" not in cache.cache_dict
print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}\nstdout: {r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------


def test_agents_md_no_close_on_eviction_rule():
    """AGENTS.md must document the rule about never closing clients on cache eviction."""
    agents_md = Path(f"{REPO}/AGENTS.md")
    content = agents_md.read_text()

    assert "cache eviction" in content.lower() or "evict" in content.lower(), \
        "AGENTS.md should mention cache eviction"
    assert "close" in content.lower() and "client" in content.lower(), \
        "AGENTS.md should reference closing clients"
    assert "in-flight" in content.lower() or "inflight" in content.lower() or "RuntimeError" in content, \
        "AGENTS.md should explain the danger of closing evicted clients"


def test_claude_md_client_cache_safety():
    """CLAUDE.md must document HTTP Client Cache Safety section."""
    claude_md = Path(f"{REPO}/CLAUDE.md")
    content = claude_md.read_text()

    assert "client cache" in content.lower() or "cache safety" in content.lower(), \
        "CLAUDE.md should have a section about client cache safety"
    assert "_remove_key" in content, \
        "CLAUDE.md should reference the _remove_key method"
    assert "close" in content.lower() and ("aclose" in content or "evict" in content.lower()), \
        "CLAUDE.md should explain not to close/evict clients"
