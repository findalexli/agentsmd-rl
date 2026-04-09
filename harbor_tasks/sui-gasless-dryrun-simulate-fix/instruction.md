# Fix Gasless Transaction Dryrun and Simulate

## Problem

The `dry_exec_transaction` and `simulate_transaction` functions in the Sui core authority are incorrectly injecting mock gas coins into **gasless transactions**. This causes the gasless allowlist check to fail with the error: "only support allowlisted types for Coin inputs".

## Background

Gasless transactions are a protocol feature that allows certain transaction types to execute without requiring SUI coins for gas payment. When a transaction is gasless:
- It should NOT have any gas coins injected
- It should pass through the validation without gas-related checks

## The Bug

Both `dry_exec_transaction` and `simulate_transaction` in `crates/sui-core/src/authority.rs` have a check like:

```rust
if transaction.gas().is_empty() {
    // inject mock gas coin
}
```

This is problematic because gasless transactions also have empty gas, but they should NOT receive mock gas injection.

## What You Need to Fix

1. In `dry_exec_transaction`: Add a check for gasless transactions BEFORE the mock gas injection. Gasless transactions should skip the mock gas injection and call `check_transaction_input` directly.

2. In `simulate_transaction`: Add a similar check for gasless transactions and skip mock gas injection when the transaction is gasless.

## Hint

A transaction is gasless when both:
- `protocol_config.enable_gasless()` returns true
- `transaction.is_gasless_transaction()` returns true

Store this in a variable like `is_gasless` and use it to conditionally skip mock gas injection.

## Files to Modify

- `crates/sui-core/src/authority.rs` - Add gasless checks in two functions

## Testing Guidelines

Per CLAUDE.md requirements:
- Run `cargo check -p sui-core` to verify compilation
- Run `cargo clippy -p sui-core` to verify linting (no `#[allow(...)]` suppressions allowed)
- Set appropriate timeouts (at least 10 minutes for this large codebase)
