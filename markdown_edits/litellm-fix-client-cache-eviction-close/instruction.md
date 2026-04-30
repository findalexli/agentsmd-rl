# Fix: HTTP/SDK clients closed on cache eviction crash streaming requests

## Problem

Streaming requests crash with `RuntimeError: Cannot send a request, as the client has been closed.` after approximately 1 hour of uptime in production. The crash happens when `LLMClientCache` evicts expired entries — the evicted client is still held by an in-flight streaming request.

The root cause is in `litellm/caching/llm_caching_handler.py`: the `LLMClientCache._remove_key()` method eagerly closes HTTP/SDK clients (calling `close()` or `aclose()`) when they are evicted from the in-memory cache after the TTL expires. If a streaming request still holds a reference to that client, it crashes.

## Expected Behavior

Evicted clients should NOT be closed. They should be garbage-collected naturally when no more references exist. Explicit client cleanup should happen only at shutdown via `close_litellm_async_clients()`, not during cache eviction.

## Files to Look At

- `litellm/caching/llm_caching_handler.py` — the `LLMClientCache` class with the `_remove_key` override that closes clients on eviction
- `litellm/caching/in_memory_cache.py` — parent `InMemoryCache` class with the default `_remove_key` behavior

## Documentation Update

After fixing the code, update the project's agent instruction files to document this behavior as a rule:

- `AGENTS.md` — Add a rule in the "COMMON PITFALLS TO AVOID" section explaining why clients must never be closed on cache eviction, referencing the specific error and the correct shutdown cleanup path
- `CLAUDE.md` — Add a section documenting HTTP Client Cache Safety, explaining that `_remove_key` must not close evicted clients and pointing to `close_litellm_async_clients()` for cleanup
