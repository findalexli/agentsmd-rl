# ty: TypedDict `pop()` doesn't use field type as bidirectional context for default argument

When calling `pop()` on a `TypedDict` with an optional field and providing a default value, ty does not use the declared field type as bidirectional inference context for the default argument.

For example, given:

```python
from typing import TypedDict

class Config(TypedDict, total=False):
    data: dict[str, int]

def f(c: Config) -> None:
    result = c.pop("data", {})
    reveal_type(result)
```

The `reveal_type` should show `dict[str, int]`, because the empty dict `{}` should be inferred as `dict[str, int]` using the field type as context. However, ty currently infers a wider type that includes an unspecialized dict (e.g., a union with a generic default type variable).

This already works correctly for `get()` — the `get()` method on `TypedDict` has an overload that provides the field type as the default parameter type, enabling bidirectional inference. The same pattern needs to be applied to `pop()`.

## Affected code

The synthesized `pop()` method overloads for `TypedDict` are generated in `crates/ty_python_semantic/src/types/class/typed_dict.rs`. Look at how overloads are built for `pop()` and compare to how `get()` handles the same scenario — `get()` already has a non-generic overload that uses the field's declared type for the default parameter.

The relevant mdtest file for TypedDict behavior is at `crates/ty_python_semantic/resources/mdtest/typed_dict.md`.

## What needs to happen

Add a non-generic overload for `pop()` that accepts the field type as the default parameter type (analogous to what already exists for `get()`), enabling bidirectional type inference for the default argument. The new overload should be ordered before the generic fallback overload so it takes priority when the default matches the field type.

Add an appropriate test case to the TypedDict mdtest file.
