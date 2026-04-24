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

The `get_type_hints` function must handle all of the following cases:

1. **Unresolvable annotations**: When a function has annotations referencing names that don't exist at runtime (e.g., `"NonExistentType"`, `"MissingModule.Cls"`, or multiple unresolvable annotations across parameters and return type), the function should return an empty dict `{}` instead of raising an error.

2. **Normal annotated functions**: For functions with standard resolvable annotations (e.g., `x: str, y: int -> float` or `name: bytes -> list`), the function should return the correct type hints dict mapping parameter names to their types, including a `"return"` key for the return annotation.

3. **Callable objects**: Objects that implement `__call__` with annotated parameters (e.g., a class with `def __call__(self, x: str, y: int) -> bool`) should have their type hints resolved correctly, returning a dict mapping parameter names to types.

4. **Non-callable inputs**: When passed a non-callable value (such as a string like `"not_callable"`, an integer like `42`, or `None`), the function should return an empty dict `{}`.

5. **Unannotated functions**: Functions with no type annotations at all should return an empty dict `{}`.

The implementation must contain substantive logic — it should not be a trivial stub (e.g., a function body that simply returns `{}` unconditionally).

## Relevant Files

- `gradio/utils.py` — contains the `get_type_hints` function

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
