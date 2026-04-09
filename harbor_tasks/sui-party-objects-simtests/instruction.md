# Enable Party Objects Simtests Under Mainnet Config and Add Deny List Test

## Problem Description

The party object simulation tests in the Sui e2e test suite are currently being skipped when running under mainnet protocol configuration. This is caused by early-return guards that check for mainnet protocol config overrides and skip the tests entirely. These guards need to be removed to enable proper test coverage under mainnet configuration.

Additionally, a new test needs to be added to verify that the coin deny list is properly enforced when transferring coins via `party_transfer` to a denied address.

## Files to Modify

1. **`crates/sui-e2e-tests/tests/party_objects_tests.rs`** - Remove the mainnet protocol config override guards from the following test functions:
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

2. **`crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs`** - Add a new test function `coin_deny_list_v2_party_owner_test` that:
   - Adds an address to the coin deny list
   - Advances the epoch to make the deny list change take effect
   - Attempts to transfer a regulated coin to the denied address via party transfer
   - Verifies the transaction fails with the `AddressDeniedForCoin` error

## New Test Requirements

The new test should follow the existing patterns in the file and:

1. Use the `#[sim_test]` attribute
2. Create a test environment using `create_test_env().await`
3. Add `DENY_ADDRESS` to the deny list using `deny_list_v2_add`
4. Trigger reconfiguration to advance the epoch
5. Build a PTB (Programmable Transaction Block) that:
   - Splits a regulated coin
   - Creates a party object using `single_owner`
   - Calls `public_party_transfer` with the split coin and party
6. Execute the transaction and verify it fails with the correct error

## Imports Needed

You may need to add or update imports for:
- `move_core_types::language_storage::StructTag`
- `sui_types::execution_status::ExecutionErrorKind`
- `sui_types::SUI_FRAMEWORK_ADDRESS`

## Testing

After making changes:
1. Ensure the code compiles with `cargo check -p sui-e2e-tests`
2. Ensure the code is properly formatted with `cargo fmt --all`
3. Run the repo's lint script if available

## Notes

- The test functions are marked with `#[sim_test]` which means they run under the Sui simulator
- Look at existing tests in the files for patterns on how to structure transactions and assertions
- The deny list test should specifically verify the `AddressDeniedForCoin` error kind with the correct address
