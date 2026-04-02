# Bug: `get_type_hints` crashes on TYPE_CHECKING-only imports

## Description

The `get_type_hints` utility function in `gradio/utils.py` crashes with a `NameError` when a user-defined callback has type annotations that reference names only available under `TYPE_CHECKING` (i.e., forward references that can't be resolved at runtime).

For example, if a user writes a function like:

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeType

def my_fn(x: str) -> SomeType:
    return x
```

When Gradio tries to introspect this function's type hints (e.g., during input validation or parameter inspection), `typing.get_type_hints()` raises a `NameError` because `SomeType` is not actually defined at runtime.

This causes the entire Gradio app to crash instead of gracefully degrading. The callers of `get_type_hints` (like `check_function_inputs_match` and `get_function_params`) already handle missing type hints — they just skip type-based validation when hints are unavailable.

## Reproduction

1. Define a function with a forward-reference return type that doesn't exist at runtime
2. Pass it to any Gradio component that inspects type hints (e.g., `gr.Interface`)
3. Observe the `NameError` crash

## Expected Behavior

The function should return an empty dict when type hints can't be resolved, allowing callers to gracefully skip type-based validation.

## Relevant Files

- `gradio/utils.py` — the `get_type_hints` function (around line 1136)
