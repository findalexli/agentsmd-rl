# [ty] PEP 695 type aliases fail in with statements

## Problem

When using PEP 695 type aliases (the `type X = A | B` syntax) as the type annotation for a variable used in a `with` statement, the type checker fails to resolve the context manager's `__enter__` and `__exit__` dunder methods. This affects all three forms of type alias declarations: `TypeAlias` annotation, PEP 695 `type` statement, and `TypeAliasType` runtime constructor.

For example, this code should type-check correctly but doesn't:

```python
type UnionAB = A | B

def f(x: UnionAB) -> None:
    with x as y:
        ...
```

The type checker cannot find `__enter__`/`__exit__` on the aliased union type because member lookup on `Type::TypeAlias` is being short-circuited by the descriptor protocol fallback (`no_instance_fallback()`) before the alias can be unwrapped.

## Expected Behavior

All three forms of type alias (`TypeAlias`, `type` statement, `TypeAliasType`) should correctly resolve context manager protocol methods when used in `with` statements. The `__enter__` return type should be inferred as the union of the constituent types.

## Required Source Code Changes

The fix must be made in `crates/ty_python_semantic/src/types.rs`. The code must satisfy these structural requirements:

1. Member lookup dispatch for type system variants must handle `Type::TypeAlias(alias)` **before** the descriptor protocol fallback (identified by `no_instance_fallback()`).

2. When processing a `Type::TypeAlias` variant, the implementation must unwrap the alias by accessing its `value_type(db)` and recursively perform member lookup via `member_lookup_with_policy()` on the resulting underlying type.

## Required Test Additions

Add a new test section to `crates/ty_python_semantic/resources/mdtest/with/sync.md` with these exact requirements:

1. Section header must be: `## Type aliases preserve context manager behavior`

2. Must include this environment configuration:
   ```toml
   [environment]
   python-version = "3.12"
   ```

3. Must test all three forms of type alias:
   - `TypeAlias` annotation (e.g., `UnionAB1: TypeAlias = A | B`)
   - PEP 695 `type` statement (e.g., `type UnionAB2 = A | B`)
   - `TypeAliasType` call (e.g., `UnionAB3 = TypeAliasType("UnionAB3", A | B)`)

4. Must include `with x as y:` statement usage for each alias type.

5. Must include `reveal_type(y)` assertions showing the inferred type is `A | B`.

6. Test classes `A` and `B` should be context managers with `__enter__` methods that return `Self`.
