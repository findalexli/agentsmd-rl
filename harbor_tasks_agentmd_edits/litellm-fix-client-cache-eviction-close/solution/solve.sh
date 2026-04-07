#!/usr/bin/env bash
set -euo pipefail

cd /workspace/litellm

# Idempotent: skip if already applied
if grep -q 'Cache for LLM HTTP clients' litellm/caching/llm_caching_handler.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/litellm/caching/llm_caching_handler.py b/litellm/caching/llm_caching_handler.py
index 331aa8f51cd..c2274713bb9 100644
--- a/litellm/caching/llm_caching_handler.py
+++ b/litellm/caching/llm_caching_handler.py
@@ -3,36 +3,21 @@
 """

 import asyncio
-from typing import Set

 from .in_memory_cache import InMemoryCache


 class LLMClientCache(InMemoryCache):
-    # Background tasks must be stored to prevent garbage collection, which would
-    # trigger "coroutine was never awaited" warnings. See:
-    # https://docs.python.org/3/library/asyncio-task.html#creating-tasks
-    # Intentionally shared across all instances as a global task registry.
-    _background_tasks: Set[asyncio.Task] = set()
+    """Cache for LLM HTTP clients (OpenAI, Azure, httpx, etc.).

-    def _remove_key(self, key: str) -> None:
-        """Close async clients before evicting them to prevent connection pool leaks."""
-        value = self.cache_dict.get(key)
-        super()._remove_key(key)
-        if value is not None:
-            close_fn = getattr(value, "aclose", None) or getattr(value, "close", None)
-            if close_fn and asyncio.iscoroutinefunction(close_fn):
-                try:
-                    task = asyncio.get_running_loop().create_task(close_fn())
-                    self._background_tasks.add(task)
-                    task.add_done_callback(self._background_tasks.discard)
-                except RuntimeError:
-                    pass
-            elif close_fn and callable(close_fn):
-                try:
-                    close_fn()
-                except Exception:
-                    pass
+    IMPORTANT: This cache intentionally does NOT close clients on eviction.
+    Evicted clients may still be in use by in-flight requests. Closing them
+    eagerly causes ``RuntimeError: Cannot send a request, as the client has
+    been closed.`` errors in production after the TTL (1 hour) expires.
+
+    Clients that are no longer referenced will be garbage-collected normally.
+    For explicit shutdown cleanup, use ``close_litellm_async_clients()``.
+    """

     def update_cache_key_with_event_loop(self, key):
         """

diff --git a/AGENTS.md b/AGENTS.md
index 546f2997bf5..d330961793a 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -212,6 +212,8 @@ When opening issues or pull requests, follow these templates:

    Using helpers like `supports_reasoning` (which read from `model_prices_and_context_window.json` / `get_model_info`) allows future model updates to "just work" without code changes.

+9. **Never close HTTP/SDK clients on cache eviction**: Do not add `close()`, `aclose()`, or `create_task(close_fn())` inside `LLMClientCache._remove_key()` or any cache eviction path. Evicted clients may still be held by in-flight requests; closing them causes `RuntimeError: Cannot send a request, as the client has been closed.` in production after the cache TTL (1 hour) expires. Connection cleanup is handled at shutdown by `close_litellm_async_clients()`. See PR #22247 for the full incident history.
+

 ## HELPFUL RESOURCES

diff --git a/CLAUDE.md b/CLAUDE.md
index 5b36c2be8ac..104a751ecaf 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -116,6 +116,9 @@ LiteLLM is a unified interface for 100+ LLM providers with two main components:
 - Optional features enabled via environment variables
 - Separate licensing and authentication for enterprise features

+### HTTP Client Cache Safety
+- **Never close HTTP/SDK clients on cache eviction.** `LLMClientCache._remove_key()` must not call `close()`/`aclose()` on evicted clients — they may still be used by in-flight requests. Doing so causes `RuntimeError: Cannot send a request, as the client has been closed.` after the 1-hour TTL expires. Cleanup happens at shutdown via `close_litellm_async_clients()`.
+
 ### Troubleshooting: DB schema out of sync after proxy restart
 `litellm-proxy-extras` runs `prisma migrate deploy` on startup using **its own** bundled migration files, which may lag behind schema changes in the current worktree. Symptoms: `Unknown column`, `Invalid prisma invocation`, or missing data on new fields.

PATCH

echo "Patch applied successfully."
