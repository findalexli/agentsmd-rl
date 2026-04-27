# Fix: HTTP/SDK clients are being closed on cache eviction

## Symptom

In production, after the LiteLLM proxy has been running for roughly the
configured cache TTL (1 hour in this codebase), streaming requests start
crashing with:

```
RuntimeError: Cannot send a request, as the client has been closed.
```

The crash comes from inside `httpx`/the OpenAI SDK, when an in-flight
request tries to use an `AsyncClient` whose underlying transport has
already been closed.

## Reproduction

The class responsible for caching HTTP / OpenAI-SDK clients is
`LLMClientCache` in `litellm/caching/llm_caching_handler.py`. It extends
`InMemoryCache` and is used as the global `litellm.in_memory_llm_clients_cache`.

Inserting a second client into a size-1 cache triggers eviction of the
first entry. With the current implementation, the evicted client is closed
even though the caller may still be holding a reference to it (e.g. an
in-flight streaming request). The same happens when an entry expires by
TTL and is evicted via `cache.evict_cache()` or `cache.get_cache()`.

A minimal reproduction:

```python
import asyncio
from litellm.caching.llm_caching_handler import LLMClientCache

class FakeClient:
    def __init__(self):
        self.closed = False
    async def aclose(self):
        self.closed = True

async def main():
    cache = LLMClientCache(max_size_in_memory=2)
    c = FakeClient()
    cache.cache_dict["k"] = c
    cache.ttl_dict["k"] = 0
    cache._remove_key("k")
    await asyncio.sleep(0.15)        # let any background tasks run
    assert c.closed is False         # currently FAILS
```

The same problem reproduces with real `httpx.AsyncClient` instances
obtained through `litellm.llms.custom_httpx.http_handler.get_async_httpx_client`,
and with `openai.AsyncOpenAI` instances stored in the cache directly.

## Required behavior

`LLMClientCache` must **not** close clients when their cache entry is
evicted — neither on capacity-based eviction nor on TTL expiry, and
regardless of whether the client exposes a synchronous `close()` method,
an asynchronous `close()` coroutine, or an `aclose()` coroutine.

Specifically, after evicting an entry whose value is an HTTP/SDK client:

- For mock objects with a `closed` attribute: `client.closed` must remain
  `False`.
- For `httpx.AsyncClient` (and `AsyncHTTPHandler` wrappers around one):
  `client.is_closed` must remain `False`.
- For `openai.AsyncOpenAI`: `client._client.is_closed` must remain
  `False`.
- The key must still be removed from `cache_dict` and `ttl_dict`.
- No "coroutine was never awaited" warnings may be emitted when an async
  client is evicted.
- Calling the eviction path when there is no running event loop must not
  raise.

Connection cleanup at process shutdown is handled separately (by
`close_litellm_async_clients()`) and is not the responsibility of the
cache. Clients that are no longer referenced anywhere will be
garbage-collected normally.

## Hints

- The bug lives in the cache class itself, not in the HTTP handler or in
  the OpenAI SDK.
- The base `InMemoryCache._remove_key` already does the right thing
  (removes the entry from `cache_dict` and `ttl_dict`). Think about what
  the subclass adds on top of that and whether that addition is needed
  at all.
- The unit and end-to-end tests under `tests/test_litellm/caching/`
  describe the behavior the cache should have; the existing
  `test_llm_client_cache_e2e.py` file in particular pins the e2e
  contract.

## Code Style Requirements

The repository uses **ruff** for linting. Your changes must pass:

```
ruff check litellm/caching/llm_caching_handler.py
```

Follow the repository's existing conventions:

- Imports go at the top of the module (no inline imports inside
  methods/functions), as documented in `CLAUDE.md`.
- Keep type hints on public APIs.
