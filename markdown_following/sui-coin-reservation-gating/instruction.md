# Gate Coin Reservation JSON-RPC Responses on Protocol Config

## Problem

The JSON-RPC API is returning fake coin objects (coin reservations) even when the `enable_coin_reservation_obj_refs` protocol config flag is disabled. This happens in two scenarios:

1. **Object retrieval**: When querying for a masked object ID (a coin reservation), the API returns a fake coin even when coin reservations are disabled in the protocol configuration. Instead, it should return a "not found" response when the feature is disabled.

2. **Coin listing**: When listing coins for an address, the API includes fake coins built from address balances even when coin reservations are disabled. Instead, it should return no fake coins when the feature is disabled.

The gRPC path already properly gates these responses, but the JSON-RPC path is missing these checks.

## Required Behavior

The `enable_coin_reservation_obj_refs()` method on the protocol configuration determines whether coin reservation features are active. Your fix must read this protocol config flag and use it to gate the coin reservation logic in the JSON-RPC path, similar to how the gRPC path already does.

For object reads: when the lookup result is `ObjectRead::NotExists`, the code must check whether `enable_coin_reservation_obj_refs()` returns true before attempting to unmask the object ID as a coin reservation. The `ObjectRead::NotExists` condition and the `enable_coin_reservation_obj_refs()` check should be evaluated together.

For coin listing: the function must determine whether `enable_coin_reservation_obj_refs()` returns true before constructing fake coins. When the feature is not enabled (`!coin_reservations_enabled`), the result should be an empty coin map (`HashMap::new()`). Fake coins should only be constructed when `enable_coin_reservation_obj_refs()` returns true.

## Verification

After your fix:
- When `enable_coin_reservation_obj_refs()` returns false, object reads should NOT return fake coins for masked object IDs
- When `enable_coin_reservation_obj_refs()` returns false, owned coin queries should NOT include fake coins
- When `enable_coin_reservation_obj_refs()` returns true, both operations should continue to work as before (returning fake coins)

Run these commands to verify:
- `cargo check -p sui-json-rpc` - must compile
- `cargo clippy --package sui-json-rpc -- -D warnings` - must pass

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt` (Rust formatter)
