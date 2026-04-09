# Optimize declaration reachability evaluation in ty type checker

## Problem

In the ty type checker's use-def analysis, the `DeclarationsIterator` has a method that checks whether declarations satisfy a predicate while filtering out unreachable ones. The current implementation evaluates reachability for **every** declaration first (expensive), then checks the predicate (cheap). This is wasteful — the predicate check is much cheaper than the reachability constraint evaluation, and in many cases declarations fail the predicate and never need their reachability checked.

The method is used in two places:
1. Class field filtering in `StaticClassLiteral` — determining whether a symbol has a non-annotation declaration
2. Enum member classification in `enum_metadata` — deciding whether a symbol is an enum member vs. annotated assignment

Both call sites use the pattern `!iter.method(|d| d.is_undefined_or(...))`, which is semantically equivalent to asking "does any declaration satisfy the negated predicate?" — a transformation that enables short-circuit evaluation.

## Expected Behavior

The method should evaluate the cheap predicate **before** the expensive reachability constraint, and short-circuit as soon as a match is found. The semantics at call sites must be preserved (same filtering behavior, just faster). The method name and signature should reflect the new "any" semantics rather than the old "all" semantics.

## Files to Look At

- `crates/ty_python_semantic/src/semantic_index/use_def.rs` — the `DeclarationsIterator` impl with the method to optimize
- `crates/ty_python_semantic/src/types/class/static_literal.rs` — call site for class field filtering
- `crates/ty_python_semantic/src/types/enums.rs` — call site for enum member classification
