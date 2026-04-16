# Optimize place_from_declarations for lazy reachability evaluation

## Problem

The `place_from_declarations_impl` function in the type checker performs expensive reachability constraint evaluations eagerly, even when the results may not be needed. This causes measurable slowdowns (2-3%) on large codebases during type checking.

Two specific patterns cause this problem:

1. **Eager `or` evaluation in `place_from_bindings_impl`**: The code accumulates reachability state using `Truthiness::or`, which always evaluates its right-hand argument even when not needed. For a lazy `Truthiness` type, an `or_else` variant that accepts a closure would allow short-circuiting when the left side is already `AlwaysTrue`.

2. **Upfront boundness analysis in `place_from_declarations_impl`**: Reachability constraints for boundness analysis are evaluated immediately, even when the result may not be used. The logic mixes the decision of whether to assume a place is bound (versus deriving boundness from visibility analysis) with the actual evaluation of those constraints.

## Required Outcomes

After optimization, the code must satisfy these behavioral requirements:

### 1. Lazy reachability in binding handling

When `place_from_bindings_impl` accumulates `deleted_reachability`, the reachability constraint evaluation must only occur when the current value is not already `AlwaysTrue`. The `Truthiness` type in `types.rs` needs a method that accepts a closure for lazy fallback evaluation, preserving the same combining semantics as the existing `or` method:
- When the current value is `AlwaysTrue`, the closure must not be called
- When the current value is `AlwaysFalse`, the closure result becomes the outcome
- When the current value is `Ambiguous`, combine with closure result: return `AlwaysFalse` if closure returns `AlwaysFalse`, otherwise stay `Ambiguous`

### 2. Deferred boundness evaluation

The `place_from_declarations_impl` function must defer reachability evaluation for boundness analysis until the result is actually needed. This requires:
- An enum in `place.rs` with two variants representing the boundness evaluation strategy: one for when a place should be treated as definitely bound, and one for when boundness should be computed from the reachability of the unbound visibility path
- An `evaluate()` method on this enum that performs the deferred reachability computation
- The enum must be constructed in `place_from_declarations_impl` with evaluation deferred until needed

### 3. Extracted non-exported check

The logic determining whether a declaration is non-exported (currently inline) must be extracted into a standalone, module-level function in `place.rs`. This function must be called from within `place_from_declarations_impl` and accept the database reference, the declaration, and the explicit reexport requirement flag.

## Performance Constraints

- Reachability constraints must not be evaluated when `Truthiness::or` short-circuiting would make the result irrelevant
- Boundness analysis reachability must be deferred until the `evaluate()` method is invoked

## Files to Modify

- `crates/ty_python_semantic/src/types.rs` — `Truthiness` type
- `crates/ty_python_semantic/src/place.rs` — `place_from_declarations_impl` and related functions
- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — `DeclarationWithConstraint` type
- `crates/ty_python_semantic/src/semantic_index.rs` — semantic index re-exports

## Coding Guidelines

Per AGENTS.md: Rust `use` imports must go at the top of the file, never inside function bodies.
