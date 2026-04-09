# Protocol Gate Coin Reservation in gRPC

## Problem

The Sui blockchain recently introduced a feature called "coin reservations" for gas payment in transactions. However, this feature needs to be gated by a protocol configuration flag to ensure it's only enabled when the network supports it.

Currently, the gRPC transaction execution service's `simulate_transaction` function in the RPC API does not properly gate the use of coin reservations behind the `enable_coin_reservation_obj_refs()` protocol configuration check. This means:

1. The `select_gas` function creates coin reservations even when the protocol version doesn't support them
2. There's no validation in the authority to reject transactions with coin reservation digests when the feature is disabled

## Files to Modify

1. **`crates/sui-core/src/authority.rs`** - Add validation to reject transactions that use coin reservations in gas payment when the protocol config doesn't support them (around line 2500, in the transaction validation path)

2. **`crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs`** - Update the `select_gas` function to:
   - Accept `protocol_config: &ProtocolConfig` parameter instead of just `max_gas_payment_objects: u32`
   - Check `protocol_config.enable_coin_reservation_obj_refs()` before prepending coin reservations
   - Use `protocol_config.max_gas_payment_objects()` where needed

## Key Details

- The protocol config flag is: `enable_coin_reservation_obj_refs()`
- Coin reservation digests can be identified using `ParsedDigest::is_coin_reservation_digest(&digest)`
- When the feature is disabled and a transaction contains coin reservation digests in gas payment, return an `UnsupportedFeatureError` with message: "coin reservations in gas payment are not supported at this protocol version"
- The coin reservation logic in `select_gas` should only execute when both:
  - `protocol_config.enable_coin_reservation_obj_refs()` returns true
  - `gas_coin_used` is true
  - There's address balance available (`ab_value > 0`)

## Testing

The code should compile with `cargo check -p sui-rpc-api -p sui-core`. The E2E tests in the repository have been updated to handle both mainnet protocol config override scenarios and normal scenarios.
