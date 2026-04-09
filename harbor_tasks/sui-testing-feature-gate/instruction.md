# Task: Replace debug_assertions with testing Feature Gate

## Problem

The codebase currently uses `#[cfg(debug_assertions)]` to gate test-only code in `sui-types` that needs to be callable from other crates. This causes issues because:

1. In release builds, the test-only code is completely excluded, causing compilation failures when other crates try to use it
2. The `sui-transactional-test-runner` crate has test-only code that needs to be available for cross-crate testing
3. Upstream test crates cannot enable this test-only functionality in release test builds

The specific symptoms are:
- `cargo check --release -p sui-transactional-test-runner` may fail because test-only code is unavailable
- Functions like `add_gasless_token_for_testing` and `clear_gasless_tokens_for_testing` in `sui-types` are not accessible in release builds
- The test adapter code has a panic branch for release builds when handling gasless tokens

## Files to Modify

1. **crates/sui-types/Cargo.toml** - Add `testing = []` feature
2. **crates/sui-types/src/transaction.rs** - Replace `#[cfg(debug_assertions)]` with `#[cfg(feature = "testing")]` for gasless token testing functions
3. **crates/sui-transactional-test-runner/Cargo.toml** - Add `testing` feature that depends on `sui-types/testing`, configure binary with `required-features`
4. **crates/sui-transactional-test-runner/src/lib.rs** - Add `#[cfg(feature = "testing")]` gates to test-only modules and imports
5. **crates/sui-transactional-test-runner/src/test_adapter.rs** - Remove `#[cfg(debug_assertions)]` guards around calls to testing functions
6. **crates/sui-adapter-transactional-tests/Cargo.toml** - Enable `testing` feature on `sui-transactional-test-runner` dependency
7. **crates/sui-verifier-transactional-tests/Cargo.toml** - Enable `testing` feature on `sui-transactional-test-runner` dependency
8. **crates/sui-indexer-alt-e2e-tests/Cargo.toml** - Enable `testing` feature on `sui-transactional-test-runner` dependency
9. **CLAUDE.md** - Add guidance on when to use `#[cfg(test)]` vs `#[cfg(feature = "testing")]`

## Expected Behavior

After the fix:
- `cargo check --release -p sui-transactional-test-runner` should pass (test-only code is properly excluded via feature gate)
- Upstream test crates can enable the `testing` feature via their dev-dependencies
- Gasless token testing functions work in both debug and release builds when the feature is enabled

## Key Patterns

- Define `testing = []` in the crate's Cargo.toml
- Use `#[cfg(feature = "testing")]` to gate test-only code that must be callable cross-crate
- Propagate the feature via `features = ["testing"]` in dependency declarations
- Use `#[cfg(test)]` only for test-only code within the same crate
