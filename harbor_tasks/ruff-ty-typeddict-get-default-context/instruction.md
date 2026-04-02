# Bug: ty infers wrong type for TypedDict `get()` with default on non-required fields

## Summary

The `ty` type checker does not use the field type as bidirectional inference context when calling `.get()` on a TypedDict with a non-required field and supplying a default value. This causes the default to be inferred independently (e.g., `{}` becomes `dict[str, int]`), which then unions with the field type instead of collapsing to just the field type.

## Reproduction

```python
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

def _(payload: Payload) -> None:
    result = payload.get("resolved", {})
    # Expected: ResolvedData
    # Actual: ResolvedData | dict[str, int]
```

The issue is that `td.get("resolved", {})` matches the generic overload `get(key, default: T) -> ResolvedData | T`, where `T` is inferred from `{}` without any context from the field type. So `T` becomes `dict[str, int]` and the return type becomes `ResolvedData | dict[str, int]` instead of just `ResolvedData`.

This also affects union TypedDicts:

```python
class Payload2(TypedDict, total=False):
    resolved: ResolvedData

def _(payload: Payload | Payload2) -> None:
    result = payload.get("resolved", {})
    # Also wrong: should be ResolvedData, not ResolvedData | dict[str, int]
```

## Relevant Code

The synthesized method overloads for TypedDict `get()` are generated in:

- `crates/ty_python_semantic/src/types/class/typed_dict.rs`

Look at the function that synthesizes the `get` signatures for each known key. Currently, for each field it generates two overloads: one without a default (returns `FieldType | None`) and one with a generic default (returns `FieldType | T`). The problem is that when the field is non-required, the generic `T` default overload doesn't give the type checker enough context to infer `{}` as the field type.

The mdtest for TypedDict `get()` behavior is in:

- `crates/ty_python_semantic/resources/mdtest/typed_dict.md`

## Expected Behavior

For non-required fields, the field type should be usable as bidirectional inference context for the default argument, so that `td.get("key", {})` resolves to just the field type (e.g., `ResolvedData`) rather than a union with the inferred type of the literal default.
