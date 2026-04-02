# Intern `InferableTypeVars` for Salsa compatibility

## Problem

The `InferableTypeVars` enum in `crates/ty_python_semantic/src/types/generics.rs` currently uses a recursive reference-based design with two lifetime parameters (`'a` and `'db`). It has three variants:

- `None` — no inferable type variables
- `One(&'a FxHashSet<BoundTypeVarIdentity<'db>>)` — a single set of inferable type variables
- `Two(&'a InferableTypeVars<'a, 'db>, &'a InferableTypeVars<'a, 'db>)` — merges two sets lazily via references

This design has a fundamental limitation: because `InferableTypeVars` contains references (the `'a` lifetime), it cannot implement `salsa::Update`, `Hash`, `Eq`, or `PartialEq`. This means it cannot be used as a parameter to or return value from `#[salsa::tracked]` functions, which is needed for ongoing work on the `SpecializationBuilder`.

The `merge` method currently creates a `Two` variant that just stores references, deferring the actual set union. While this avoids allocation at merge time, it creates a tree of references that must be traversed on every lookup, and the reference-based structure prevents salsa interning.

Additionally, `iter()` and `display()` must recursively walk the `Two` tree, and `BoundTypeVarIdentity::is_inferable` must do the same — all of which adds complexity for what is essentially just a set membership check.

## Goal

Redesign `InferableTypeVars` so that it:

1. Has only a single lifetime parameter (`'db`)
2. Can be used as a salsa-tracked function parameter (implements the necessary traits)
3. Uses salsa interning for the inner set storage
4. Makes `merge` a salsa-tracked method that eagerly computes the union
5. Updates all call sites across the codebase to pass `db` where newly required

## Affected Files

- `crates/ty_python_semantic/src/types/generics.rs` — the `InferableTypeVars` type definition, `merge`, `iter`, `display`, `is_inferable`, `inferable_typevars`
- `crates/ty_python_semantic/src/types.rs` — `filter_union_for_callable_overload` signature
- `crates/ty_python_semantic/src/types/call/bind.rs` — `ArgumentTypeChecker`, `Binding`, `BindingSnapshot` structs and `TypeGuard` handling
- `crates/ty_python_semantic/src/types/constraints.rs` — `is_cyclic_impl`, `satisfied_by_all_typevars`, `solve` signatures
- `crates/ty_python_semantic/src/types/relation.rs` — `TypeRelationChecker`, `DisjointnessChecker`, type relation methods
- `crates/ty_python_semantic/src/types/signatures.rs` — `inferable_typevars`, signature subtyping merge logic
