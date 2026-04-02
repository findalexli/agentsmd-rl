# Bug: ty ignores `Required`, `NotRequired`, and `ReadOnly` qualifiers in functional TypedDict syntax

## Summary

When defining a `TypedDict` using the functional syntax (`TypedDict("Name", {"field": Type})`), `ty` does not preserve type qualifiers like `Required`, `NotRequired`, and `ReadOnly`. This means:

1. `ReadOnly[T]` fields in functional TypedDicts are not enforced as read-only — assignments that should be rejected are silently accepted.
2. `NotRequired[T]` fields are treated as required when `total=True` (the default), so omitting them incorrectly produces a `missing-typed-dict-key` error.
3. `Required[T]` fields are treated as optional when `total=False`, so omitting them does NOT produce the expected `missing-typed-dict-key` error.
4. String forward references wrapping qualifiers (e.g., `"NotRequired[int]"`) are also not handled.

The class-based TypedDict syntax correctly handles all these qualifiers — only the functional form is broken.

## Reproduction

```python
from typing_extensions import TypedDict, ReadOnly, NotRequired, Required

# ReadOnly is ignored in functional form:
TD1 = TypedDict("TD1", {"id": ReadOnly[int]})
d1 = TD1(id=1)
d1["id"] = 2  # should error with invalid-assignment, but ty accepts it

# NotRequired is ignored in functional form:
TD2 = TypedDict("TD2", {"name": str, "year": NotRequired[int]})
TD2(name="x")  # should be valid, but ty reports missing-typed-dict-key for "year"

# Required is ignored in functional form with total=False:
TD3 = TypedDict("TD3", {"name": Required[str], "year": int}, total=False)
TD3()  # should error for missing "name", but ty accepts it
```

## Relevant Code

The functional TypedDict field construction logic is in:

- `crates/ty_python_semantic/src/types/typed_dict.rs` — the `functional_typed_dict_field` function constructs a `TypedDictField` from a declared type and the `total` flag. It currently uses only `total` to determine requiredness and does not look at type qualifiers at all.

- `crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs` — where functional TypedDict fields are assembled during type inference. The field annotations are inferred but qualifiers are not extracted or passed through.

- `crates/ty_python_semantic/src/types/infer/builder.rs` and `crates/ty_python_semantic/src/types/infer.rs` — the inference builder and its result type. Qualifiers from annotation expressions need to be stored and made available when constructing deferred functional TypedDict schemas.

- `crates/ty_python_semantic/src/types/infer/builder/annotation_expression.rs` — where annotation expressions are inferred. Qualifiers are computed here but not currently stored for later retrieval.

## Expected Behavior

Functional TypedDict syntax should respect `Required`, `NotRequired`, and `ReadOnly` qualifiers exactly as the class-based syntax does.
