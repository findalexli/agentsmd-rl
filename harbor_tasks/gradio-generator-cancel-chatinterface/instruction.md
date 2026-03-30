# Fix generator cancel close in ChatInterface

## Bug Description

When pressing the stop button during streaming in `ChatInterface`, sync generators are not properly closed. The `close()` method is never called on the generator, which means `GeneratorExit` is never raised, and apps cannot clean up resources (e.g., close database connections, cancel API calls).

There are two issues:

1. **In `chat_interface.py`**: The `_stream_fn` and `_examples_stream_fn` methods iterate over the generator but do not use a `finally` block or context manager to ensure the generator is closed when cancellation or any other exit occurs. The generator is simply abandoned.

2. **In `utils.py`**: The `SyncToAsyncIterator.aclose()` method is not declared as `async`, which means `await iterator.aclose()` fails. Similarly, the `safe_aclose_iterator()` helper calls `iterator.aclose()` without `await`, so the close operation does not actually execute.

## What to Fix

### `gradio/chat_interface.py`:
1. In `_stream_fn`, wrap the generator iteration with `async with aclosing(generator):` (from `contextlib`) to ensure the generator is closed on cancellation or normal exit.
2. In `_examples_stream_fn`, similarly wrap with `async with aclosing(generator):`.
3. Add `from contextlib import aclosing` to the imports.

### `gradio/utils.py`:
1. Make `SyncToAsyncIterator.aclose()` an async method by adding `async` to its definition.
2. In `safe_aclose_iterator()`, add `await` to the `iterator.aclose()` calls (both for `SyncToAsyncIterator` and the general case).

## Affected Code

- `gradio/chat_interface.py` — `_stream_fn` and `_examples_stream_fn` methods
- `gradio/utils.py` — `SyncToAsyncIterator.aclose()` and `safe_aclose_iterator()`

## Acceptance Criteria

- Generator iteration in `_stream_fn` and `_examples_stream_fn` is wrapped with `aclosing()`
- `SyncToAsyncIterator.aclose()` is an async method
- `safe_aclose_iterator()` properly awaits the aclose calls
- Both files remain syntactically valid Python
