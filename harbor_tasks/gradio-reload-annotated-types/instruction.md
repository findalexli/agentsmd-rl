# Fix: Reload Mode When Annotated Types Are Used

## Problem

When using Gradio's reload/hot-reload mode, applications that use `typing.Annotated` types (common in libraries like LangGraph) crash with errors about unresolvable `ForwardRef` strings. For example, a user defining a class with `Annotated[str, "description"]` type hints will get errors when `get_type_hints()` is called on their code during reload.

## Symptoms

- The `watchfn` function in `gradio/utils.py` carries the `CO_FUTURE_ANNOTATIONS` compiler flag, which propagates into user code executed during reload
- When this flag is present, all annotations in user code become stringified `ForwardRef` objects
- After any fix, forward-reference annotations to types like `App`, `Blocks`, `Component`, `BlockContext`, `Request`, `SessionState`, and `Button` must remain quoted string literals (not bare names) to avoid NameError at import time

## Expected Behavior

- Gradio reload mode should work correctly with user code that uses `Annotated` types
- User code executed during reload should have real type objects in `__annotations__`, not strings
- The repository's ruff checks, reload tests, and type hint tests should continue to pass
- All modules should import cleanly without errors

## Files to Investigate

- `gradio/utils.py` -- contains the `watchfn` function that handles hot-reload
- `gradio/cli/commands/skills.py` -- related module that may need adjustments
