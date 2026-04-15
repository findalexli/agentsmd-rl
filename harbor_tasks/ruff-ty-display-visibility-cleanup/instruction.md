# Unnecessary public visibility in ty display types

## Problem

The file `crates/ty_python_semantic/src/types/display.rs` in the ty type checker contains a number of items with `pub` or `pub(crate)` visibility that is broader than necessary. These items are only used within the `types` module and should have module-private visibility instead.

Additionally, some methods are dead code — they are not called anywhere in the codebase and should be removed entirely.

### Structs and enums with unnecessary visibility

The following structs and enums should not have `pub` or `pub(crate)` on their declarations:

- `DisplayTuple`
- `DisplayFunctionType`
- `DisplayGenericContext`
- `DisplaySpecialization`
- `DisplayTypeArray`
- `QualificationLevel` (enum)
- `TupleSpecialization` (enum)

### Methods with unnecessary visibility

The following methods should not have `pub` or `pub(crate)` on their declarations:

- `fn singleline`
- `fn force_signature_name`
- `fn with_active_scopes`

### Fields that should be private

The `DisplaySettings` struct has two fields of type `Rc<FxHashMap<...>>` that should be private (not `pub`):

- `qualified`
- `qualified_type_aliases`

### Dead code to remove

The following methods are unused anywhere in the codebase and must be removed entirely:

- `truncate_long_unions` — a method that is not called anywhere
- `Specialization::display()` — the no-argument `display` method that returns `DisplaySpecialization` (this is distinct from `display_full`, `display_short`, and `display_with`, which should be kept)

## Expected Behavior

After changes, the crate must still compile and pass all quality checks: `cargo check`, `cargo clippy`, `cargo test`, `cargo fmt`, and `cargo doc` for the `ty_python_semantic` package.

## File

- `crates/ty_python_semantic/src/types/display.rs`
