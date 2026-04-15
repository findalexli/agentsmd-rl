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
3. Add an address to the coin deny list using the `deny_list_v2_add` function from the SUI framework `coin` module
4. Advance the epoch by calling `trigger_reconfiguration` so the deny list change takes effect
5. Build a programmable transaction block (PTB) that:
   - Splits a regulated coin
   - Creates a party object for the recipient address using `single_owner` from the SUI framework `party` module
   - Transfers the split coin via `public_party_transfer` from the SUI framework `transfer` module
6. Execute the transaction and verify it fails with the `AddressDeniedForCoin` error

**Symptom**: Currently, there is no test coverage for the deny list enforcement when coins are transferred via party transfer.

**Expected behavior**: A regulated coin transfer to a denied address via party transfer should fail with `AddressDeniedForCoin`.

## Imports Required

The new test requires the following imports in `per_epoch_config_stress_tests.rs`:

1. `StructTag` from `move_core_types::language_storage` (alongside the existing `TypeTag` import, in a grouped import: `use move_core_types::language_storage::{StructTag, TypeTag};`)

2. `ExecutionErrorKind` from `sui_types::execution_status` (grouped with existing imports where `TransactionEffectsAPI` is imported)

3. `SUI_FRAMEWORK_ADDRESS` alongside `SUI_DENY_LIST_OBJECT_ID` and `SUI_FRAMEWORK_PACKAGE_ID` from `sui_types` (update the existing grouped import to: `use sui_types::{SUI_DENY_LIST_OBJECT_ID, SUI_FRAMEWORK_ADDRESS, SUI_FRAMEWORK_PACKAGE_ID};`)

## Verification

After making changes:
1. The code should compile: `cargo check -p sui-e2e-tests`
2. The code should be properly formatted: `cargo fmt --all`
3. License headers and lints should pass: `cargo xlint`
4. Clippy should pass: `cargo clippy -p sui-e2e-tests`

## Expected Test Structure

The new test should call these functions/methods as part of its implementation:
- `deny_list_v2_add` (SUI framework coin module)
- `trigger_reconfiguration` (on test cluster)
- `single_owner` (SUI framework party module)
- `public_party_transfer` (SUI framework transfer module)
- `execute_transaction_may_fail` (wallet API)
- `effects.status().is_err()` (to verify transaction failure)
- `ExecutionErrorKind::AddressDeniedForCoin` (to verify the specific error)

The test should reference `DENY_ADDRESS` and verify the `AddressDeniedForCoin` error includes the denied address.
