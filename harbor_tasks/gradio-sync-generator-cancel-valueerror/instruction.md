# Fix sync generator cancel ValueError

## Bug Description

When cancelling a sync generator in `ChatInterface` (e.g., stopping an LLM streaming response), a `ValueError: generator already executing` is raised and not properly handled. This is a regression introduced by a recent change that wrapped generator iteration in `async with aclosing(generator):` to ensure proper cleanup.

The problem is that `aclosing.__aexit__` calls `aclose()` directly on `SyncToAsyncIterator`, which calls `self.iterator.close()` without any retry logic. When the sync generator is blocked mid-iteration in the thread pool (the common case for LLM streaming), `close()` raises `ValueError: generator already executing`.

Retry logic for this exact scenario already exists in `safe_aclose_iterator()`, but it is not reachable from the `aclosing` code path. The `aclosing` context manager calls `aclose()` directly on the iterator, bypassing `safe_aclose_iterator()` entirely.

## What to Fix

In `gradio/utils.py`, modify the `SyncToAsyncIterator.aclose()` method to handle the "generator already executing" race condition by retrying `close()` with a brief sleep interval and a timeout. This ensures that both the `aclosing` path and the `safe_aclose_iterator` path handle the race condition correctly.

After moving the retry logic into `SyncToAsyncIterator.aclose()`, the `safe_aclose_iterator()` function can be simplified since it no longer needs to contain `SyncToAsyncIterator`-specific retry logic.

## Affected Code

- `gradio/utils.py`: `SyncToAsyncIterator.aclose()` method and `safe_aclose_iterator()` function

## Acceptance Criteria

- `SyncToAsyncIterator.aclose()` retries on `ValueError("generator already executing")` with backoff and timeout
- `safe_aclose_iterator()` delegates to `aclose()` without duplicating retry logic
- The file remains syntactically valid Python
- Cancelling sync generators no longer raises unhandled `ValueError`
