# Remove fragile multi-inference state from TypeInferenceBuilder

## Problem

The `TypeInferenceBuilder` in `crates/ty_python_semantic/src/types/infer/builder.rs` has two internal fields — `multi_inference_state` and `inner_expression_inference_state` — that control behavior when expressions are inferred speculatively (e.g., during overload resolution or TypedDict union narrowing). These fields create several problems:

1. **Manual save/restore is fragile**: Every call site that needs speculative inference must manually call `set_multi_inference_state()` and `context.set_multi_inference()`, save the old values, and restore them afterward. Missing a restore corrupts the builder's state for subsequent inference.

2. **`speculate()` doesn't propagate context**: The `speculate()` method creates a fresh `TypeInferenceBuilder` via `::new()`, but this means the speculative builder doesn't inherit the parent's `cycle_recovery`, `deferred_state`, `typevar_binding_context`, `inference_flags`, or other contextual state. This can lead to incorrect inference in speculative paths.

3. **`InferContext` has a parallel flag**: The `InferContext` struct in `crates/ty_python_semantic/src/types/context.rs` also has a `multi_inference: bool` field with `is_in_multi_inference()` and `set_multi_inference()` methods. This is used to suppress diagnostics and skip extending diagnostics during multi-inference, duplicating the control mechanism across two structs.

4. **`inner_expression_inference_state` adds a second mode**: The `InnerExpressionInferenceState` enum (with `Infer` and `Get` variants) adds yet another mode that causes `infer_expression` and `infer_type_expression` to short-circuit and return previously stored types instead of re-inferring. This is used in type expression subscription for unions but is another piece of mutable state that must be manually toggled.

5. **`discard()` is a footgun**: Speculative builders require calling `discard()` when their results should be thrown away, or the `DebugDropBomb` will panic. Every early-return path must remember to call `discard()`.

## Goal

Replace the flag-based multi-inference approach with a more ergonomic design that:
- Makes `speculate()` properly propagate the parent builder's inference context
- Eliminates the need for manual save/restore of multi-inference state
- Removes the `multi_inference` flag from `InferContext`
- Removes the `inner_expression_inference_state` field
- Makes speculative builders safe to drop without explicit cleanup

## Affected Files

- `crates/ty_python_semantic/src/types/context.rs` — `InferContext` multi-inference flag and diagnostic suppression
- `crates/ty_python_semantic/src/types/infer/builder.rs` — `TypeInferenceBuilder` fields, `speculate()`, `extend()`, `discard()`, `VecMap`/`FxOrderSet` helper traits
- `crates/ty_python_semantic/src/types/infer/builder/binary_expressions.rs` — TypedDict update inference
- `crates/ty_python_semantic/src/types/infer/builder/class.rs` — deferred class definition insert
- `crates/ty_python_semantic/src/types/infer/builder/function.rs` — function decorator/deferred inference
- `crates/ty_python_semantic/src/types/infer/builder/named_tuple.rs` — NamedTuple deferred inference
- `crates/ty_python_semantic/src/types/infer/builder/type_expression.rs` — PEP 604 union and subscript handling
- `crates/ty_python_semantic/src/types/infer/builder/typevar.rs` — TypeVar deferred inference
