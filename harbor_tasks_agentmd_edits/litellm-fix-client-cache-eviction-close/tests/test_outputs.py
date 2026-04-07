"""
Task: litellm-fix-client-cache-eviction-close
Repo: BerriAI/litellm @ bf9c96b91205d17e13d9c7ea54d396005db5bc63
PR:   22925

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import asyncio
import sys
import os
from pathlib import Path

import pytest

REPO = "/workspace/litellm"
sys.path.insert(0, REPO)

from litellm.caching.llm_caching_handler import LLMClientCache


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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_key_does_not_close_async_client():
    """Evicting an async client from LLMClientCache must NOT close it.

    On the base commit, _remove_key schedules aclose() via create_task(),
    which closes the client. The fix removes the override entirely.
    """
    cache = LLMClientCache(max_size_in_memory=10)

    class MockAsyncClient:
        def __init__(self):
            self.closed = False

        async def aclose(self):
            self.closed = True

    mock_client = MockAsyncClient()
    cache.cache_dict["test-key"] = mock_client
    cache.ttl_dict["test-key"] = 0  # expired

    cache._remove_key("test-key")
    # Let the event loop drain any background close tasks
    await asyncio.sleep(0.1)

    assert not mock_client.closed, (
        "Async client was closed on eviction — causes "
        "'Cannot send a request, as the client has been closed' in production"
    )
    assert "test-key" not in cache.cache_dict
    assert "test-key" not in cache.ttl_dict


def test_remove_key_does_not_close_sync_client():
    """Evicting a sync client from LLMClientCache must NOT close it.

    On the base commit, _remove_key calls close() directly on sync clients.
    The fix removes the override so the parent class just removes the key.
    """
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

    assert not mock_client.closed, (
        "Sync client was closed on eviction"
    )
    assert "test-key" not in cache.cache_dict


@pytest.mark.asyncio
async def test_eviction_does_not_close_async_clients():
    """When the cache is full and entries are evicted, clients stay open.

    Uses multiple clients and fills the cache beyond capacity to trigger
    LRU eviction. All evicted clients must remain open.
    """
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


def test_remove_key_handles_plain_values():
    """_remove_key works correctly for non-client values (strings, dicts).

    Regression check: removing the override shouldn't break eviction of
    plain values that have no close()/aclose() methods.
    """
    cache = LLMClientCache(max_size_in_memory=5)

    cache.cache_dict["str-key"] = "hello"
    cache.ttl_dict["str-key"] = 0
    cache.cache_dict["dict-key"] = {"foo": "bar"}
    cache.ttl_dict["dict-key"] = 0

    cache._remove_key("str-key")
    cache._remove_key("dict-key")

    assert "str-key" not in cache.cache_dict
    assert "dict-key" not in cache.cache_dict


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------


def test_agents_md_no_close_on_eviction_rule():
    """AGENTS.md must document the rule about never closing clients on cache eviction.

    The PR adds rule #9 to AGENTS.md explaining why evicted clients must not
    be closed and pointing to close_litellm_async_clients() for cleanup.
    """
    agents_md = Path(f"{REPO}/AGENTS.md")
    content = agents_md.read_text()

    # Check for key concepts from the config update
    assert "cache eviction" in content.lower() or "evict" in content.lower(), \
        "AGENTS.md should mention cache eviction"
    assert "close" in content.lower() and "client" in content.lower(), \
        "AGENTS.md should reference closing clients"
    assert "in-flight" in content.lower() or "inflight" in content.lower() or "RuntimeError" in content, \
        "AGENTS.md should explain the danger of closing evicted clients"


def test_claude_md_client_cache_safety():
    """CLAUDE.md must document HTTP Client Cache Safety section.

    The PR adds a section explaining that _remove_key must not close
    evicted clients, referencing close_litellm_async_clients() for cleanup.
    """
    claude_md = Path(f"{REPO}/CLAUDE.md")
    content = claude_md.read_text()

    assert "client cache" in content.lower() or "cache safety" in content.lower(), \
        "CLAUDE.md should have a section about client cache safety"
    assert "_remove_key" in content, \
        "CLAUDE.md should reference the _remove_key method"
    assert "close" in content.lower() and ("aclose" in content or "evict" in content.lower()), \
        "CLAUDE.md should explain not to close/evict clients"
