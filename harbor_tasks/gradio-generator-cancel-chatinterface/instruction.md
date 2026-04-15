# Fix generator cleanup on cancel in ChatInterface

## Bug Description

When the stop button is pressed during streaming in `ChatInterface`, synchronous generators are not properly closed. This prevents `GeneratorExit` from being raised, meaning applications cannot clean up resources like database connections or API calls when streaming is cancelled.

There are two related issues:

1. **In `gradio/chat_interface.py`**: The `_stream_fn` and `_examples_stream_fn` methods iterate over generators but do not ensure the generators are closed when cancellation occurs. The generators are abandoned without proper cleanup.

2. **In `gradio/utils.py`**: The `SyncToAsyncIterator` class has an `aclose()` method that is not awaitable, preventing it from being used in async contexts where `await` is required. Additionally, the `safe_aclose_iterator()` helper function calls `aclose()` without awaiting it, so the close operation may not actually execute.

## Requirements

### `gradio/chat_interface.py`:
- `_stream_fn` must wrap its generator iteration with proper cleanup handling that ensures the generator is closed on cancellation or normal exit. The `aclosing` context manager from `contextlib` must be used.
- `_examples_stream_fn` must similarly wrap its generator iteration with `aclosing`.
- The file must import `aclosing` from `contextlib`.

### `gradio/utils.py`:
- `SyncToAsyncIterator.aclose()` must be an async method that returns a coroutine (can be awaited).
- `safe_aclose_iterator()` must await the `aclose()` calls for both `SyncToAsyncIterator` and generic async iterators.

## Affected Code

- `gradio/chat_interface.py` — `_stream_fn` and `_examples_stream_fn` methods
- `gradio/utils.py` — `SyncToAsyncIterator.aclose()` and `safe_aclose_iterator()`

## Acceptance Criteria

- Generator iteration in `_stream_fn` and `_examples_stream_fn` is wrapped with `aclosing()` context manager
- `SyncToAsyncIterator.aclose()` returns a coroutine when called
- `safe_aclose_iterator()` properly awaits the aclose calls
- Both files remain syntactically valid Python
