# ty type checker: Literal[-3.14] not flagged as invalid and PEP-613 type alias validation is incomplete

## Problem

The `ty` type checker has two related issues with type expression validation:

1. **`Literal[-3.14]` is silently accepted**: Writing `x: Literal[-3.14]` or `x: Literal[-3j]` does not produce an `invalid-type-form` diagnostic, even though only integer literals are valid inside `Literal[]` with unary operators. Both of these should be flagged:
   ```python
   x: Literal[-3.14]
   y: Literal[-2.718]
   z: Literal[-3j]
   w: Literal[-1.5j]
   ```
   However, integer literals with unary operators should remain valid:
   ```python
   a: Literal[-3]
   b: Literal[-42]
   c: Literal[+7]
   ```

2. **PEP-613 type alias right-hand sides are under-validated**: The current validation for `TypeAlias` assignment values is incomplete. For example:
   ```python
   var1 = 3
   Bad: TypeAlias = var1
   ```
   This should produce an `invalid-type-form` diagnostic but currently doesn't. Valid type aliases must continue to work without errors:
   ```python
   Good1: TypeAlias = int
   Good2: TypeAlias = int | str
   Good3: TypeAlias = list[int]
   Good4: TypeAlias = tuple[int, str]
   ```

## New Module

The PEP-613 alias validation must be implemented as a new Rust module at:

`crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs`

This module must:
- Be registered in the parent directory's `mod.rs`
- Not contain `panic!()`, `.unwrap()`, or `unreachable!()` on non-comment lines
- Have all `use` imports only at the top of the file (no imports inside function bodies)

## Codebase

The repo is at `/workspace/ruff`. After changes, the codebase must:
- Compile (`cargo check -p ty_python_semantic`)
- Pass formatting (`cargo fmt --all --check`)
- Pass clippy (`cargo clippy -p ty_python_semantic`)
- Pass all mdtest suites (including `literal` and `pep613` tests)
- Pass library unit tests (`cargo test -p ty_python_semantic --lib`)
- Build docs without errors (`cargo doc --no-deps -p ty_python_semantic`)
