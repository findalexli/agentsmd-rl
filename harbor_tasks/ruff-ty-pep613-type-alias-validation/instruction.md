# ty type checker: Literal[-3.14] not flagged as invalid and PEP-613 type alias validation is incomplete

## Problem

The `ty` type checker has two related issues with type expression validation:

1. **`Literal[-3.14]` is silently accepted**: Writing `x: Literal[-3.14]` or `x: Literal[-3j]` does not produce an `invalid-type-form` diagnostic, even though only integer literals are valid inside `Literal[]` with unary operators. The issue is in how `infer_type_expression` handles unary operations on number literals — it currently accepts all number types (int, float, complex) instead of restricting to integers only.

2. **PEP-613 type alias right-hand sides use ad-hoc validation**: The validation for `TypeAlias` assignment values uses a hand-written `alias_syntax_validation` function with a `const fn` approach. This is incomplete — for example, `var1 = 3; X: TypeAlias = var1` is incorrectly accepted because the validator treats all `Name` expressions as valid. The proper approach is to reuse the existing `infer_type_expression` infrastructure which already knows how to validate type expressions thoroughly.

## Expected Behavior

- `Literal[-3.14]`, `Literal[-3j]`, and similar non-integer unary expressions in `Literal[]` should emit `invalid-type-form`
- `Literal[-3]` (integer) should continue to be accepted
- PEP-613 type alias right-hand sides should be fully validated using `infer_type_expression`, catching cases like variable references that aren't types

## Files to Look At

- `crates/ty_python_semantic/src/types/infer/builder/type_expression.rs` — handles `infer_type_expression`, specifically the unary-op arm in `Literal[]` subscript inference
- `crates/ty_python_semantic/src/types/infer/builder.rs` — contains the ad-hoc `alias_syntax_validation` function and the post-inference pass dispatch loop
- `crates/ty_python_semantic/src/types/infer/builder/post_inference/` — existing post-inference check modules; a new module for PEP-613 alias validation would fit here
