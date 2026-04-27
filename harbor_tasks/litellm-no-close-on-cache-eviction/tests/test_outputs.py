"""Tests for the LLMClientCache eviction-must-not-close fix."""

import asyncio
import os
import subprocess
import sys
import warnings

import pytest

REPO = "/workspace/litellm"
sys.path.insert(0, REPO)

from litellm.caching.llm_caching_handler import LLMClientCache  # noqa: E402


class _MockAsync:
    def __init__(self) -> None:
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class _MockAsyncWithClose:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class _MockSync:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# Fail-to-pass: evicting a client must NOT close it
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_key_does_not_close_async_client():
    """Evicting an async client (with `aclose`) must not close it."""
    cache = LLMClientCache(max_size_in_memory=2)
    client = _MockAsync()
    cache.cache_dict["k"] = client
    cache.ttl_dict["k"] = 0
    cache._remove_key("k")
    await asyncio.sleep(0.15)
    assert client.closed is False, "async client was closed on eviction"
    assert "k" not in cache.cache_dict
    assert "k" not in cache.ttl_dict


@pytest.mark.asyncio
async def test_remove_key_does_not_close_async_client_with_close_method():
    """Same guarantee when the close coroutine is named `close` (OpenAI SDK style)."""
    cache = LLMClientCache(max_size_in_memory=2)
    client = _MockAsyncWithClose()
    cache.cache_dict["k"] = client
    cache.ttl_dict["k"] = 0
    cache._remove_key("k")
    await asyncio.sleep(0.15)
    assert client.closed is False, "async client (close) was closed on eviction"


def test_remove_key_does_not_close_sync_client():
    """Evicting a sync client must not close it."""
    cache = LLMClientCache(max_size_in_memory=2)
    client = _MockSync()
    cache.cache_dict["k"] = client
    cache.ttl_dict["k"] = 0
    cache._remove_key("k")
    assert client.closed is False, "sync client was closed on eviction"
    assert "k" not in cache.cache_dict


@pytest.mark.asyncio
async def test_full_cache_eviction_does_not_close_clients():
    """Inserting beyond capacity must evict but must not close the evicted clients."""
    cache = LLMClientCache(max_size_in_memory=2, default_ttl=600)
    clients = [_MockAsync() for _ in range(2)]
    for i, c in enumerate(clients):
        cache.set_cache(f"key-{i}", c)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        cache.set_cache("key-new", "filler")
        await asyncio.sleep(0.15)
    coro_warns = [w for w in caught if "coroutine" in str(w.message).lower()]
    assert not coro_warns, f"unawaited coroutine warnings: {coro_warns}"
    for c in clients:
        assert c.closed is False, "evicted client was closed"


@pytest.mark.asyncio
async def test_evicted_httpx_client_remains_open():
    """End-to-end: an httpx client obtained via get_async_httpx_client must remain
    open after its cache entry is evicted. Sleep is required — the regression
    schedules close asynchronously."""
    import litellm
    from litellm.llms.custom_httpx.http_handler import get_async_httpx_client

    cache = LLMClientCache(max_size_in_memory=1, default_ttl=600)
    original = litellm.in_memory_llm_clients_cache
    litellm.in_memory_llm_clients_cache = cache
    try:
        client_a = get_async_httpx_client(llm_provider="provider_a")
        # Inserting a second client evicts the first (capacity=1).
        client_b = get_async_httpx_client(llm_provider="provider_b")
        await asyncio.sleep(0.15)
        assert not client_a.client.is_closed, (
            "Evicted httpx client was closed — production-breaking regression"
        )
        await client_a.client.aclose()
        await client_b.client.aclose()
    finally:
        litellm.in_memory_llm_clients_cache = original


@pytest.mark.asyncio
async def test_ttl_expired_client_remains_open():
    """When a cache entry expires via TTL and is evicted, the underlying client
    must remain open."""
    import litellm
    from litellm.llms.custom_httpx.http_handler import get_async_httpx_client

    cache = LLMClientCache(max_size_in_memory=4, default_ttl=600)
    original = litellm.in_memory_llm_clients_cache
    litellm.in_memory_llm_clients_cache = cache
    try:
        client = get_async_httpx_client(llm_provider="provider_ttl")
        for key in list(cache.ttl_dict.keys()):
            cache.ttl_dict[key] = 0
            cache.expiration_heap = [(0, k) for _, k in cache.expiration_heap]
        cache.evict_cache()
        await asyncio.sleep(0.15)
        assert not client.client.is_closed, (
            "TTL-expired httpx client was closed — production-breaking regression"
        )
        await client.client.aclose()
    finally:
        litellm.in_memory_llm_clients_cache = original


@pytest.mark.asyncio
async def test_evicted_openai_sdk_client_stays_usable():
    """OpenAI SDK clients (the production scenario) must survive cache eviction."""
    from openai import AsyncOpenAI

    cache = LLMClientCache(max_size_in_memory=1, default_ttl=600)
    client = AsyncOpenAI(api_key="sk-test", base_url="https://api.openai.com/v1")
    cache.set_cache("openai-client", client, ttl=600)
    cache.set_cache("filler", "x", ttl=600)
    await asyncio.sleep(0.15)
    assert not client._client.is_closed, (
        "AsyncOpenAI client was closed on cache eviction — this triggers "
        "'Cannot send a request, as the client has been closed' in production"
    )
    await client.close()


# ---------------------------------------------------------------------------
# Pass-to-pass: unrelated cache behavior must keep working
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_remove_key_still_evicts_entry():
    """Removing a key must still actually remove it from cache_dict and ttl_dict."""
    cache = LLMClientCache(max_size_in_memory=4)
    cache.cache_dict["a"] = "value-a"
    cache.ttl_dict["a"] = 0
    cache.cache_dict["b"] = {"foo": "bar"}
    cache.ttl_dict["b"] = 0
    cache._remove_key("a")
    cache._remove_key("b")
    assert "a" not in cache.cache_dict
    assert "b" not in cache.cache_dict
    assert "a" not in cache.ttl_dict
    assert "b" not in cache.ttl_dict


def test_remove_key_no_event_loop():
    """`_remove_key` must not raise when there is no running event loop."""
    cache = LLMClientCache(max_size_in_memory=2)
    client = _MockAsync()
    cache.cache_dict["k"] = client
    cache.ttl_dict["k"] = 0
    cache._remove_key("k")
    assert "k" not in cache.cache_dict


def test_dual_cache_module_p2p():
    """Run an unrelated upstream caching test file as pass-to-pass."""
    r = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_litellm/caching/test_dual_cache.py",
            "-q",
            "--no-header",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"Upstream dual-cache tests failed:\nSTDOUT:\n{r.stdout[-1500:]}\n"
        f"STDERR:\n{r.stderr[-500:]}"
    )


def test_caching_module_ruff():
    """Run ruff on the caching module — code quality must pass after the fix."""
    r = subprocess.run(
        ["ruff", "check", "litellm/caching/llm_caching_handler.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff failed:\n{r.stdout}\n{r.stderr}"
