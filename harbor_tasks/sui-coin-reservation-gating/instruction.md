# Gate Coin Reservation JSON-RPC Responses on Protocol Config

## Problem

The JSON-RPC API is returning fake coin objects (coin reservations) even when the `enable_coin_reservation_obj_refs` protocol config flag is disabled. This happens in two scenarios:

1. **Object retrieval**: When querying for a masked object ID (a coin reservation), the API returns a fake coin even when coin reservations are disabled in the protocol configuration. Instead, it should return a "not found" response when the feature is disabled.

2. **Coin listing**: When listing coins for an address, the API includes fake coins built from address balances even when coin reservations are disabled. Instead, it should return no fake coins when the feature is disabled.

The gRPC path already properly gates these responses, but the JSON-RPC path is missing these checks.

## Required Implementation

Your fix must implement the following patterns:

1. **Variable naming**: Define a boolean variable named `coin_reservations_enabled` that stores the result of calling `enable_coin_reservation_obj_refs()` on the protocol configuration.

2. **Early return pattern**: Use the pattern `if !coin_reservations_enabled { HashMap::new() }` to return an empty map when coin reservations are disabled.

3. **Protocol config access**: Access the protocol configuration via the epoch store's `protocol_config()` method.

4. **Object retrieval condition**: When an object is not found (represented by `ObjectRead::NotExists`), only proceed to check for a masked/coin-reservation object ID when `enable_coin_reservation_obj_refs()` returns true. The check should use the `&&` operator to combine these conditions.

## Verification

After your fix:
- When `enable_coin_reservation_obj_refs()` returns false, object reads should NOT return fake coins for masked object IDs
- When `enable_coin_reservation_obj_refs()` returns false, owned coin queries should NOT include fake coins
- When `enable_coin_reservation_obj_refs()` returns true, both operations should continue to work as before (returning fake coins)

Run these commands to verify:
- `cargo check -p sui-json-rpc` - must compile
- `cargo clippy --package sui-json-rpc -- -D warnings` - must pass
