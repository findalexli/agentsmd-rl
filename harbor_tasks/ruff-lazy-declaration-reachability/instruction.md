# Optimize declaration reachability evaluation in ty type checker

## Problem

In the ty type checker's use-def analysis, the `DeclarationsIterator` has a method that checks whether declarations satisfy a predicate while filtering out unreachable ones. The current implementation evaluates reachability for **every** declaration first (expensive), then checks the predicate (cheap). This is wasteful — the predicate check is much cheaper than the reachability constraint evaluation, and in many cases declarations fail the predicate and never need their reachability checked.

The method is called in two places:
1. Class field filtering in `StaticClassLiteral` — determining whether a symbol has a non-annotation declaration
2. Enum member classification in `enum_metadata` — deciding whether a symbol is an enum member vs. annotated assignment

Both call sites currently use the pattern `!iter.method(|d| d.is_undefined_or(...))`, which is semantically equivalent to asking "does any declaration satisfy the negated predicate?" — but the current implementation does not take advantage of this to short-circuit.

## Expected Behavior

The method should evaluate the cheap predicate **before** the expensive reachability constraint, and short-circuit as soon as a match is found. Semantics at call sites must be preserved (same filtering behavior, just faster). The method should be renamed to reflect the "any" (not "all") nature of its short-circuiting behavior.

The new method must be named `any_reachable` and the call sites must use `is_defined_and` (the logical dual of the current `is_undefined_or` pattern).

## Files to Modify

- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — the `DeclarationsIterator` implementation; rename the method and restructure its internal logic
- `crates/ty_python_semantic/src/types/class/static_literal.rs` — call site for class field filtering
- `crates/ty_python_semantic/src/types/enums.rs` — call site for enum member classification

## Acceptance Criteria

1. The crate compiles without errors (`cargo check -p ty_python_semantic`)
2. The `any_reachable` method exists in `DeclarationsIterator` and its body contains the fields `predicates`, `reachability_constraints`, and calls `.evaluate()` and `is_always_false()`
3. The predicate is checked before reachability evaluation (not using a `.filter().all()` chain)
4. Both call sites use `.any_reachable(` with `is_defined_and(` as the predicate
5. No `.all_reachable(` calls remain in the crate source
6. All repo tests pass (cargo test, cargo clippy, cargo fmt)