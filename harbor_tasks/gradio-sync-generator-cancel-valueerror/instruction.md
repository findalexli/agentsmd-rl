# Fix sync generator cancel ValueError

## Bug Description

When cancelling a sync generator during async iteration (e.g., stopping an LLM streaming response), a `ValueError: generator already executing` is raised and not properly handled. This causes unhandled exceptions during cleanup when the generator is blocked mid-iteration in a thread pool.

## Expected Behavior

After the fix:

- `from gradio.utils import SyncToAsyncIterator, safe_aclose_iterator` must succeed
- `SyncToAsyncIterator.aclose(retry_interval=0.01, timeout=5.0)` should handle sync iterators whose `close()` temporarily raises `ValueError("generator already executing")` by eventually succeeding
- `SyncToAsyncIterator.aclose(timeout=0.1, retry_interval=0.02)` should raise `ValueError` matching "already executing" when the close keeps failing beyond the timeout
- Non-matching `ValueError` messages (e.g., `ValueError("some other error")`) must be propagated immediately without any retry
- `safe_aclose_iterator()` must continue to work correctly with native async generators
- `gradio/utils.py` must pass syntax checks and ruff check/format
