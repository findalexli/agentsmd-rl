# Task: Fix Compilation Errors After Lance Upgrade

## Problem

The repository fails to compile after upgrading the Lance dependency from version 3.0.0-rc.2 to 3.0.0-rc.3. The `cargo check` command produces errors related to breaking API changes in the `lance_core::Error` type.

## Your Task

1. Update `Cargo.toml` to use Lance version 3.0.0-rc.3 instead of 3.0.0-rc.2
2. Fix all compilation errors by adapting the code to the new Lance error API
3. Run `cargo check` to verify the fixes

## Files Requiring Changes

The following files contain code that must be updated to use the new Lance error API:

1. **`python/src/namespace.rs`** - Contains multiple calls to `lance_core::Error::io()` that use the old two-argument pattern with `Default::default()` as the second argument. These must be converted to the new single-argument pattern.

2. **`python/src/storage_options.rs`** - Contains:
   - Uses of the struct variant `lance_core::Error::IO { source: ..., location: ... }` which no longer exists
   - Uses of the struct variant `lance_core::Error::InvalidInput { source: ..., location: ... }` which no longer exists
   - Calls to `snafu::location!()` macro which is no longer available in the new snafu version

3. **`rust/lancedb/src/database/namespace.rs`** - Contains error handling code that explicitly wraps errors with `.map_err()` when calling `.declare_table(declare_request).await`. The error propagation should be simplified to use the `?` operator directly.

## Compilation Errors to Address

When you run `cargo check`, you will see errors indicating that:
- `lance_core::Error::io` is being called with two arguments (a format string and `Default::default()`), but the new API accepts only one argument (just the format string)
- `lance_core::Error::IO` struct variant no longer exists; use `Error::io_source()` instead
- `lance_core::Error::InvalidInput` struct variant no longer exists; use `Error::invalid_input()` instead
- `snafu::location!()` macro is no longer available and should be removed from error constructions

## Expected Patterns After Fix

The fixed code should show these patterns:
- In `python/src/namespace.rs`: `lance_core::Error::io(format!("...", ...))` without `Default::default()`
- In `python/src/storage_options.rs`: `lance_core::Error::io_source(...)` and `lance_core::Error::invalid_input(...)` without struct variant syntax or `snafu::location!()`
- In `rust/lancedb/src/database/namespace.rs`: `.declare_table(declare_request).await?` without explicit `.map_err()` wrapping

## Expected Outcome

After your changes, `cargo check` should pass without errors.

## Notes

- Focus on making the minimal changes needed for compilation to succeed
- The Lance crate's error handling patterns have changed between rc.2 and rc.3
- Consult the Lance documentation or source code for the correct new API patterns
