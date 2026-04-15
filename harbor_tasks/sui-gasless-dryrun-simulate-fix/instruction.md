# Fix Gasless Transaction Dryrun and Simulate

## Problem

The `dry_exec_transaction` and `simulate_transaction` functions in the Sui core authority are incorrectly injecting mock gas coins into **gasless transactions**. This causes the gasless allowlist check to fail with the error: "only support allowlisted types for Coin inputs".

## Background

Gasless transactions are a protocol feature that allows certain transaction types to execute without requiring SUI coins for gas payment. When a transaction is gasless:
- It should NOT have any gas coins injected
- It should pass through the validation without gas-related checks

## The Bug

Both `dry_exec_transaction` and `simulate_transaction` in `crates/sui-core/src/authority.rs` check if `transaction.gas().is_empty()` to decide whether to inject mock gas. This is incorrect because gasless transactions also have empty gas, but they should NOT receive mock gas injection.

A transaction is gasless when both:
- `protocol_config.enable_gasless()` returns true
- `transaction.is_gasless_transaction()` returns true

## Required Behavior

Your fix must ensure:

1. **Gasless detection**: Both functions must determine whether the transaction is gasless using the protocol configuration and transaction state.

2. **Skip mock gas for gasless**: When a transaction is gasless, mock gas injection must be skipped entirely.

3. **Use direct validation for gasless**: For gasless transactions in `dry_exec_transaction`, use `sui_transaction_checks::check_transaction_input` directly instead of the mock gas path.

4. **Preserve existing behavior**: Non-gasless transactions with empty gas should continue to work as before (mock gas injection).

## Files to Modify

- `crates/sui-core/src/authority.rs` - Modify `dry_exec_transaction` and `simulate_transaction`

## Implementation Notes

- You will need to add gasless checks in two separate functions
- The gasless validation path should call `sui_transaction_checks::check_transaction_input` with the appropriate parameters
- For `simulate_transaction`, ensure the mock gas injection is skipped when the transaction is gasless

## Testing Guidelines

Per CLAUDE.md requirements:
- Run `cargo check -p sui-core` to verify compilation
- Run `cargo clippy -p sui-core` to verify linting (no `#[allow(...)]` suppressions allowed)
- Set appropriate timeouts (at least 10 minutes for this large codebase)
