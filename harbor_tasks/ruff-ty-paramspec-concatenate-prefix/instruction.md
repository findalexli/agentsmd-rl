# [ty] Bare ParamSpec incorrectly accepted in invalid contexts

## Problem

The ty type checker fails to reject bare `ParamSpec` type variables in positions where they are not valid. For example, a bare `ParamSpec` like `P` or `Q` should only be allowed as the first argument to `Callable` (e.g., `Callable[P, R]`) or as the last argument to `Concatenate` (e.g., `Concatenate[int, P]`). However, ty incorrectly accepts bare `ParamSpec` in several other positions:

- Inside a list literal in a subscript specialization: `SomeClass[[Q]]` or `SomeClass[Q,]`
- In the prefix (non-last) arguments of `Concatenate` when nested inside another subscript: `Foo[Concatenate[P, ...]]` where `P` is in the prefix, not the tail
- In the default list of another `ParamSpec`: `ParamSpec("P5", default=[Q])`
- In `Concatenate` non-last positions inside generic aliases: `Alias[Concatenate[P2, P3]]`

This is a type checker soundness issue — invalid type expressions silently pass validation instead of being flagged with `invalid-type-form` diagnostics.

## Expected Behavior

ty should report `invalid-type-form` errors with a message like "Bare ParamSpec `Q` is not valid in this context" when a bare `ParamSpec` appears in any position other than:
- The first argument to `Callable`
- The last argument to `Concatenate`
- Stringified annotations in those same positions

## Files to Look At

- `crates/ty_python_semantic/src/types/infer/builder/type_expression.rs` — handles type expression inference including `Concatenate` and subscript argument validation
- `crates/ty_python_semantic/src/types/infer/builder/subscript.rs` — handles subscript type argument inference
- `crates/ty_python_semantic/src/types/infer/builder/typevar.rs` — handles `ParamSpec` default value inference
