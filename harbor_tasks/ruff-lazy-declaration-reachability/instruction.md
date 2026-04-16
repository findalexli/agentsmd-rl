# Optimize declaration reachability evaluation in ty type checker

## Problem

In the ty type checker's use-def analysis, the `DeclarationsIterator` has a method that checks whether declarations satisfy a predicate while filtering out unreachable ones. The current implementation evaluates reachability for **every** declaration first (expensive), then checks the predicate (cheap). This is wasteful — the predicate check is much cheaper than the reachability constraint evaluation, and in many cases declarations fail the predicate and never need their reachability checked.

The method is used in two places:
1. Class field filtering in `StaticClassLiteral` — determining whether a symbol has a non-annotation declaration
2. Enum member classification in `enum_metadata` — deciding whether a symbol is an enum member vs. annotated assignment

Both call sites currently use the pattern `!iter.method(|d| d.is_undefined_or(...))`, which is semantically equivalent to asking "does any declaration satisfy the negated predicate?" — but the current implementation does not take advantage of this to short-circuit.

## Files to Modify

- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — the `DeclarationsIterator` implementation
- `crates/ty_python_semantic/src/types/class/static_literal.rs` — call site for class field filtering
- `crates/ty_python_semantic/src/types/enums.rs` — call site for enum member classification

## Expected Behavior

1. The method should evaluate the cheap predicate **before** the expensive reachability constraint, and short-circuit as soon as a match is found (lazy evaluation)
2. The method name should be changed to reflect that it returns true when ANY declaration matches (not ALL)
3. Call sites must preserve their current semantics — the De Morgan transformation (`!all(!x)` → `any(x)`) should be applied correctly
4. The crate compiles without errors (`cargo check -p ty_python_semantic`)
5. No calls to the old method name remain in the crate source
6. All repo tests pass (cargo test, cargo clippy, cargo fmt)
