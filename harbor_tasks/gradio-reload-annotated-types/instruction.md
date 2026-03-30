# Fix: Reload Mode When Annotated Types Are Used

## Problem

When using Gradio's reload/hot-reload mode, applications that use `typing.Annotated` types (common in libraries like LangGraph) crash with errors about unresolvable `ForwardRef` strings. For example, a user defining a class with `Annotated[str, "description"]` type hints will get errors when `get_type_hints()` is called on their code during reload.

## Root Cause

The file `gradio/utils.py` contains `from __future__ import annotations` at the top. When the `watchfn` function in this module calls `exec()` to re-execute user code during hot reload, Python propagates the `CO_FUTURE_ANNOTATIONS` compiler flag into the exec'd code. This causes all annotations in the user's code to be stringified (turned into `ForwardRef` strings), which breaks libraries that call `get_type_hints()` and expect real type objects.

## Expected Behavior

- Gradio reload mode should work correctly with user code that uses `Annotated` types
- The `watchfn` function should not carry the `CO_FUTURE_ANNOTATIONS` flag
- Removing `from __future__ import annotations` from `gradio/utils.py` requires converting all bare type annotations in that file to string annotations (e.g., `App` -> `"App"`, `Blocks` -> `"Blocks"`)

## Files to Investigate

- `gradio/utils.py` -- remove `from __future__ import annotations` and convert type annotations to strings
- `gradio/cli/commands/skills.py` -- may need `cast()` import for type safety after the change
