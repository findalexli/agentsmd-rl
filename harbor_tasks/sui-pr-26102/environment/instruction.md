# Task: Add Feature Flag Gating for Coin Reservation Object References

## Problem

The `suix_getCoins` JSON-RPC endpoint currently injects a synthetic object reference pointing to an address's SUI balance unconditionally. However, this feature should only be enabled when the protocol supports it.

The protocol configuration includes a feature flag called `enable_coin_reservation_obj_refs` that controls whether this functionality should be active. The endpoint needs to check this flag from the database before including the synthetic coin reference in its response.

## Files to Modify

1. **`crates/sui-indexer-alt-jsonrpc/src/data/address_balance_coins.rs`**
   - The `load_address_balance_coin` function needs to check if the `enable_coin_reservation_obj_refs` feature flag is enabled
   - If the flag is not enabled, return `Ok(None)` early
   - Currently uses `super::current_epoch()` - should use a function from the new system_state module

2. **`crates/sui-indexer-alt-jsonrpc/src/data/mod.rs`**
   - The `current_epoch` function implementation should be moved to a new module
   - Should export functions from the new system_state module instead

3. **`crates/sui-indexer-alt-jsonrpc/src/data/system_state.rs`** (new file)
   - Create this module to hold system state query functions
   - Must include:
     - `latest_epoch`: Query the latest epoch from the `kv_epoch_starts` table (moved from mod.rs)
     - `latest_feature_flag`: Query the latest value for a feature flag from the `kv_feature_flags` table
   - `latest_feature_flag` should:
     - Take a feature flag name string parameter
     - Query the `kv_feature_flags` table filtered by flag name
     - Order by `protocol_version` descending to get the latest value
     - Return `false` as default if the flag is not found
     - Return `Result<bool, anyhow::Error>`

## Requirements

- All new files must include the license header:
  ```
  // Copyright (c) Mysten Labs, Inc.
  // SPDX-License-Identifier: Apache-2.0
  ```
- Follow existing code style in the crate
- The crate must compile successfully
- Clippy linting must pass

## Testing

The relevant tests for this functionality are in the `sui-indexer-alt-e2e-tests` crate. However, for this task focus on:

1. Ensuring the code compiles: `cargo check -p sui-indexer-alt-jsonrpc`
2. Ensuring clippy passes: `cargo xclippy -p sui-indexer-alt-jsonrpc`

The key behavioral change is that when `enable_coin_reservation_obj_refs` is not enabled in the protocol config, the `load_address_balance_coin` function should return `None` (not include the synthetic coin), effectively gating the feature.
