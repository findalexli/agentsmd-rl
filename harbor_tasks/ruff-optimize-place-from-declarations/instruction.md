# Optimize place_from_declarations for lazy reachability evaluation

## Problem

The `place_from_declarations_impl` function in ty's type checker eagerly evaluates reachability constraints even when the result may never be needed. Specifically:

1. In `place_from_bindings_impl`, the `deleted_reachability` value eagerly evaluates `reachability_constraints.evaluate(...)` via `.or()` every time a deleted binding is encountered, even though the result is only useful when combined with other reachability information. This is wasteful because `evaluate()` can be expensive.

2. In `place_from_declarations_impl`, the function unconditionally computes `undeclared_reachability` by peeking at the first declaration and evaluating its reachability constraint — before even knowing whether any real declarations exist that would make this result relevant. The boundness analysis is performed inline rather than being deferred.

This causes measurable slowdowns (2-3%) on large codebases like sympy, pydantic, and pandas during type checking.

## Expected Behavior

Reachability constraint evaluation should be lazy — deferred until the point where the result is actually needed. The `place_from_declarations_impl` function should separate the concern of *what* boundness analysis strategy to use from *when* to evaluate it, so that expensive reachability computations only run when their results will actually be consumed.

Similarly, `place_from_bindings_impl` should use lazy evaluation for deleted reachability accumulation.

## Files to Look At

- `crates/ty_python_semantic/src/place.rs` — contains `place_from_declarations_impl` and `place_from_bindings_impl`, the primary targets for optimization
- `crates/ty_python_semantic/src/types.rs` — contains `Truthiness` type which may need a lazy evaluation variant
- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — contains `DeclarationWithConstraint` used by the declarations iterator
- `crates/ty_python_semantic/src/semantic_index.rs` — re-exports for semantic index types
