# Optimize place_from_declarations for lazy reachability evaluation

## Problem

The `place_from_declarations_impl` function in ty's type checker performs expensive reachability constraint evaluations eagerly, even when the results may not be needed. This causes measurable slowdowns (2-3%) on large codebases like sympy, pydantic, and pandas during type checking.

Two specific locations are affected:

1. In `place_from_bindings_impl`, the `deleted_reachability` value is accumulated using the `Truthiness::or` method each time a deleted binding is encountered. The `Truthiness` type does not currently provide a lazy alternative to `or` — that method only accepts an already-evaluated value, not a closure.

2. In `place_from_declarations_impl`, boundness analysis is always performed upfront even when it may not be needed. The logic for deciding whether to assume a place is bound (versus deriving boundness from unbound visibility) is mixed into the main function flow rather than being encapsulated separately.

## Required Changes

### 1. Add `or_else` to `Truthiness` in `types.rs`

Add a method `or_else` on `Truthiness` that accepts a closure (lazy fallback). The method should behave as follows:

- If `self` is `Truthiness::AlwaysTrue`, return `self` without calling the closure.
- Otherwise, call the closure and use the result according to the same combining logic as `or`, but with `Truthiness::AlwaysFalse` treating the closure result as the outcome.

Specifically: when `self` is `AlwaysFalse`, return the closure's result. When `self` is `Ambiguous`, return `AlwaysFalse` if the closure returns `AlwaysFalse`, otherwise return `Ambiguous`.

### 2. Use `or_else` in `place_from_bindings_impl` in `place.rs`

Update the accumulation of `deleted_reachability` inside `place_from_bindings_impl` to use `or_else` (the lazy variant) instead of `or` (the eager variant), so that the reachability constraint is only evaluated when actually needed.

### 3. Introduce `DeclarationsBoundnessEvaluator` enum in `place.rs`

Create an enum named `DeclarationsBoundnessEvaluator` in `place.rs` with the following two variants:

- `AssumeBound` — indicates the place should be treated as definitely bound
- `BasedOnUnboundVisibility` — indicates boundness should be computed from the reachability of the unbound path

The enum must have an `evaluate()` method that performs the actual boundness computation. This evaluator should be constructed and stored in `place_from_declarations_impl`, deferring the reachability evaluation until `evaluate()` is called.

### 4. Extract `is_non_exported` as a standalone function in `place.rs`

Extract the logic that determines whether a declaration is non-exported into a standalone (module-level) function named `is_non_exported`. The function must accept these parameters (in order): `db`, `declaration`, and `requires_explicit_reexport`. It must be called from within `place_from_declarations_impl`.

## Files to Modify

- `crates/ty_python_semantic/src/types.rs` — add `or_else` method to `Truthiness`
- `crates/ty_python_semantic/src/place.rs` — contains `place_from_declarations_impl` and `place_from_bindings_impl`; add `DeclarationsBoundnessEvaluator` enum, extract `is_non_exported`, use `or_else`
- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — contains `DeclarationWithConstraint` used by the declarations iterator
- `crates/ty_python_semantic/src/semantic_index.rs` — re-exports for semantic index types

## Coding Guidelines

Per AGENTS.md: Rust `use` imports must go at the top of the file, never inside function bodies.
