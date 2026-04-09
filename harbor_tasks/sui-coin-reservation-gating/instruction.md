# Fix: Gate Coin Reservation JSON-RPC Responses on Protocol Config

## Problem

The JSON-RPC methods in `crates/sui-json-rpc/src/authority_state.rs` are returning fake coins (coin reservations) even when the `enable_coin_reservation_obj_refs` protocol config flag is disabled. This means addresses with address balances enabled but coin reservations disabled are incorrectly receiving fake coin objects through the JSON-RPC API.

Specifically:
1. `get_object_read()` returns fake coins for masked object IDs without checking if coin reservations are enabled
2. `get_owned_coins()` builds fake coins for address balances without checking if coin reservations are enabled

The gRPC simulate path already has proper gating, but the JSON-RPC path is missing these checks.

## What You Need to Do

Modify `crates/sui-json-rpc/src/authority_state.rs` to add protocol config gating to the `get_object_read` and `get_owned_coins` methods so that fake coins are only returned when `enable_coin_reservation_obj_refs()` returns true.

### Key Files
- `crates/sui-json-rpc/src/authority_state.rs` - The main file to modify

### Hints
1. Look for the `get_object_read` method in the `StateRead` trait implementation. It currently checks for `ObjectRead::NotExists` and then tries to unmask the object ID to return a fake coin. This logic needs to be gated on the protocol config.

2. Look for the `get_owned_coins` method. It currently builds a `fake_coins` map unconditionally. This should only happen when coin reservations are enabled.

3. You can access the protocol config via `self.load_epoch_store_one_call_per_task().protocol_config()`.

4. The method to check is `enable_coin_reservation_obj_refs()` on the protocol config.

### Development Guidelines
- Run `cargo check -p sui-json-rpc` to verify your changes compile
- Run `cargo xclippy -p sui-json-rpc` to ensure linting passes
- Follow the existing code style in the file
- Do NOT add new test files - just fix the implementation

## Expected Behavior

After the fix:
- When `enable_coin_reservation_obj_refs()` is false, `get_object_read` should NOT return fake coins for masked object IDs
- When `enable_coin_reservation_obj_refs()` is false, `get_owned_coins` should NOT include fake coins in the response
- When `enable_coin_reservation_obj_refs()` is true, both methods should continue to work as before (returning fake coins)
