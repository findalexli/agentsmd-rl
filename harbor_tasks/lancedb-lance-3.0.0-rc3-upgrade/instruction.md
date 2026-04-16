# Task: Fix Compilation Errors After Lance Upgrade

## Problem

The repository fails to compile after upgrading the Lance dependency from version 3.0.0-rc.2 to 3.0.0-rc.3. The `cargo check` command produces errors related to breaking API changes in the `lance_core::Error` type.

## Your Task

1. Update `Cargo.toml` to use Lance version 3.0.0-rc.3 instead of 3.0.0-rc.2
2. Fix all compilation errors by adapting the code to the new Lance error API
3. Run `cargo check` to verify the fixes

## Compilation Errors to Address

When you run `cargo check`, you will see errors indicating that:
- `lance_core::Error::io` is being called with incorrect arguments
- `lance_core::Error::IO` struct variant no longer exists
- `lance_core::Error::InvalidInput` struct variant no longer exists
- `snafu::location!()` macro is no longer available

## Expected Outcome

After your changes, `cargo check` should pass without errors.

## Notes

- Focus on making the minimal changes needed for compilation to succeed
- The Lance crate's error handling patterns have changed between rc.2 and rc.3
- Consult the Lance documentation or source code for the correct new API patterns
