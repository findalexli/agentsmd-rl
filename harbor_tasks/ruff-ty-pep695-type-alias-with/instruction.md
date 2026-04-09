# [ty] PEP 695 type aliases fail in with statements

## Problem

When using PEP 695 type aliases (the `type X = A | B` syntax) as the type annotation for a variable used in a `with` statement, the type checker fails to resolve the context manager's `__enter__` and `__exit__` dunder methods. This affects all forms of type alias declarations: `TypeAlias` annotation, PEP 695 `type` statement, and `TypeAliasType` runtime constructor.

For example, this code should type-check correctly but doesn't:

```python
type UnionAB = A | B

def f(x: UnionAB) -> None:
    with x as y:
        ...
```

The type checker cannot find `__enter__`/`__exit__` on the aliased union type.

## Expected Behavior

All three forms of type alias (`TypeAlias`, `type` statement, `TypeAliasType`) should correctly resolve context manager protocol methods when used in `with` statements. The `__enter__` return type should be inferred as the union of the constituent types.

## Files to Look At

- `crates/ty_python_semantic/src/types.rs` — the `member_lookup_with_policy` method on `Type` handles member lookup dispatch; the order of match arms matters for dunder method resolution
- `crates/ty_python_semantic/resources/mdtest/with/sync.md` — existing tests for `with` statement type checking
