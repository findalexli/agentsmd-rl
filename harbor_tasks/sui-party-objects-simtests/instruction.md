# Enable Party Object Simtests Under Mainnet Config and Add Deny List Test

## Problem Description

The party object simulation tests in the Sui e2e test suite are currently being skipped when running under mainnet protocol configuration. The tests execute an early-return guard that checks for mainnet protocol config overrides and exits before running the test body. These guards prevent test coverage under mainnet configuration.

Additionally, there is no test verifying that the coin deny list is properly enforced when transferring coins via `party_transfer` to a denied address.

## Tasks

### Task 1: Enable Party Object Tests Under Mainnet Config

The following test functions in `crates/sui-e2e-tests/tests/party_objects_tests.rs` have early-return guards that skip them when running under mainnet protocol configuration:

- `party_object_deletion`
- `party_object_deletion_multiple_times`
- `party_object_deletion_multiple_times_cert_racing`
- `party_object_transfer`
- `party_object_transfer_multiple_times`
- `party_object_transfer_multi_certs`
- `party_object_read`
- `party_object_grpc`
- `party_coin_grpc`
- `party_object_jsonrpc`

Each of these functions contains a guard pattern similar to:
```rust
if sui_simulator::has_mainnet_protocol_config_override() {
    return;
}
```

**Symptom**: When the test suite runs under mainnet protocol config, these tests skip without running any assertions.

**Expected behavior**: These tests should execute their full body under mainnet configuration.

### Task 2: Add Coin Deny List Verification Test

A new test function must be added to `crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs` that verifies the coin deny list is enforced when transferring regulated coins via party transfer to a denied address.

The new test must:

1. Use the `#[sim_test]` attribute
2. Create a test environment using `create_test_env().await`
3. Add an address to the coin deny list using the deny list management function from the SUI framework `coin` module
4. Advance the epoch by calling `trigger_reconfiguration` so the deny list change takes effect
5. Build a programmable transaction block (PTB) that:
   - Splits a regulated coin
   - Creates a party object for the recipient address using `single_owner` from the SUI framework `party` module
   - Transfers the split coin via `public_party_transfer` from the SUI framework `transfer` module
6. Execute the transaction and verify it fails with the `AddressDeniedForCoin` error

**Symptom**: Currently, there is no test coverage for the deny list enforcement when coins are transferred via party transfer.

**Expected behavior**: A regulated coin transfer to a denied address via party transfer should fail with `AddressDeniedForCoin`.

## Imports Required

The new test requires additional imports in `per_epoch_config_stress_tests.rs`:

1. `StructTag` type alongside `TypeTag` (both from `move_core_types::language_storage`)
2. `ExecutionErrorKind` from `sui_types::execution_status` 
3. `SUI_FRAMEWORK_ADDRESS` constant alongside existing SUI types constants

## Verification

After making changes:
1. The code should compile: `cargo check -p sui-e2e-tests`
2. The code should be properly formatted: `cargo fmt --all`
3. License headers and lints should pass: `cargo xlint`
4. Clippy should pass: `cargo clippy -p sui-e2e-tests`

## Expected Test Behavior

The new test should:
- Use `deny_list_v2_add` from the SUI framework coin module to add an address to the deny list
- Call `trigger_reconfiguration` on the test cluster to advance the epoch
- Use `single_owner` from the SUI framework party module to create a party object
- Use `public_party_transfer` from the SUI framework transfer module for the transfer
- Use `execute_transaction_may_fail` to execute the transaction
- Verify the transaction failed with `effects.status().is_err()`
- Verify the error is `ExecutionErrorKind::AddressDeniedForCoin` for the denied address
- Reference `DENY_ADDRESS` to identify the denied address