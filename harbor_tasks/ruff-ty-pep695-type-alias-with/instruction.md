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

## Requirements

### Code Requirements in `crates/ty_python_semantic/src/types.rs`

The `member_lookup_with_policy` function must satisfy these behavioral requirements:

1. When performing member lookup dispatch for a `Type::TypeAlias` variant, the implementation must call `value_type(db)` on the alias and recursively invoke `member_lookup_with_policy` on the underlying type to properly unwrap the alias.

2. The match arm for `Type::TypeAlias(alias)` must execute before the descriptor protocol fallback (identified by `policy.no_instance_fallback()`) is invoked. This ensures type aliases are unwrapped before the fallback short-circuits member lookup.

3. The implementation must preserve existing functionality: the `no_instance_fallback` check and `invoke_descriptor_protocol` code path must still exist and be reachable for other type variants.

### Test Requirements in `crates/ty_python_semantic/resources/mdtest/with/sync.md`

Add a new test section with these exact specifications:

1. Section header: `## Type aliases preserve context manager behavior`

2. Environment configuration:
   ```toml
   [environment]
   python-version = "3.12"
   ```

3. Must test all three forms of type alias with context manager classes:
   - `TypeAlias` annotation: `UnionAB1: TypeAlias = A | B`
   - PEP 695 `type` statement: `type UnionAB2 = A | B`
   - `TypeAliasType` call: `UnionAB3 = TypeAliasType("UnionAB3", A | B)`

4. Test classes `A` and `B` must be context managers with `__enter__` methods that return `Self`.

5. Each type alias must be used in a `with x as y:` statement.

6. Must include `reveal_type(y)` assertions showing the inferred type is `A | B`.

## Verification

The implementation must pass:
- `cargo check -p ty_python_semantic`
- `cargo test -p ty_python_semantic --test mdtest with/sync`
- `cargo clippy -p ty_python_semantic -- -D warnings`
