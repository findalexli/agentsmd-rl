# [ty] TypedDict Constructor Values Lack Field Type Context

## Problem

The `ty` type checker does not use field type context when inferring TypedDict constructor values. When constructing a TypedDict whose fields are themselves TypedDicts, the values passed to the constructor are inferred without knowing the expected field type. This causes false positive errors in several scenarios:

1. **Nested TypedDict keyword construction**: Constructing a TypedDict with keyword arguments where values are nested TypedDict constructors (e.g., `Outer(inner=Inner(x=1, y="hello"))`) may be incorrectly rejected.

2. **`dict()` as TypedDict positional argument**: Using `dict(...)` as a positional argument (e.g., `Outer(dict(field1=..., field2=...))`) is inferred as a generic dict rather than the target TypedDict, because no type context is provided.

3. **Missing key detection through `dict()`**: When `dict()` is used as a keyword value for a TypedDict field, missing required keys in the inner dict are not properly detected as `missing-typed-dict-key` diagnostics because the value isn't inferred with the field's TypedDict type context.

## Expected Behavior

- TypedDict constructor validation should re-infer keyword argument values and positional dict arguments using the destination field's declared type as context
- Nested TypedDict constructions (both via class constructors and `dict()`) should be accepted when all fields are correctly provided
- Missing keys in nested `dict()` calls should produce `missing-typed-dict-key` diagnostics (not generic type incompatibility errors)

## Files to Look At

- `crates/ty_python_semantic/src/types/typed_dict.rs` — `validate_typed_dict_constructor`, `validate_from_keywords`, and `validate_from_dict_literal` functions that validate TypedDict constructor calls
- `crates/ty_python_semantic/src/types/infer/builder.rs` — Call site where `validate_typed_dict_constructor` is invoked during type inference for call expressions
- `crates/ty_python_semantic/src/types/infer/builder/dict.rs` — Dict literal inference path that also calls `validate_typed_dict_constructor`
