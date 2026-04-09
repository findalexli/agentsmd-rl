# Task: Cleanup Unused Fields and No-Op Flag in Sui Consensus

## Problem

The Sui consensus layer has accumulated some unused fields and a feature flag that is now always true (making it a no-op). This cleanup PR removes:

1. **The `always_accept_system_transactions` field** from `ConsensusProtocolConfig` - this feature flag is now always enabled, making it unnecessary
2. **The `always_accept_system_transactions` field** from `CommittedSubDag` struct - same reasoning
3. **The unused `events` column family** from `AuthorityPerpetualTables` - deprecated and replaced by `events_2`
4. **Unused imports** in several files (`Event` from authority.rs, `Context` from commit.rs, `TransactionEventsDigest` from authority_store_tables.rs)

5. **The `context` parameter** from `load_committed_subdag_from_store()` - no longer needed since the protocol config field was removed

## Key Behavioral Change

The most important change is in `parse_block_transactions()` in `consensus_output_api.rs`. The old logic was:

```rust
let rejected = rejected_transaction_indices.contains(&index) &&
    (transaction.is_user_transaction() || !always_accept_system_transactions);
```

Since `always_accept_system_transactions` was always `true`, this simplifies to:

```rust
// System transactions are always accepted; only user transactions can be rejected.
let rejected = transaction.is_user_transaction() && rejected_transaction_indices.contains(&index);
```

## Files to Modify

1. `consensus/config/src/consensus_protocol_config.rs` - Remove field from struct, default, constructor, and getter
2. `consensus/core/src/commit.rs` - Remove field from `CommittedSubDag`, remove `Context` import, update `load_committed_subdag_from_store`
3. `consensus/core/src/commit_observer.rs` - Remove context parameter from function call
4. `consensus/core/src/dag_state.rs` - Remove context parameter from function call
5. `consensus/core/src/leader_schedule.rs` - Update test code to not pass the removed parameter
6. `consensus/core/src/linearizer.rs` - Remove context/protocol_config reference when creating CommittedSubDag
7. `consensus/core/src/test_dag_builder.rs` - Update test code
8. `crates/sui-core/src/authority.rs` - Clean up imports (remove unused `Event`)
9. `crates/sui-core/src/authority/authority_store_tables.rs` - Remove deprecated `events` field, clean up imports
10. `crates/sui-core/src/consensus_handler.rs` - Update test code
11. `crates/sui-core/src/consensus_manager/mod.rs` - Remove parameter from `to_consensus_protocol_config`
12. `crates/sui-core/src/consensus_types/consensus_output_api.rs` - Simplify `parse_block_transactions` logic, remove parameter

## Requirements

- Code must compile with `cargo check`
- The `parse_block_transactions` function should reject only user transactions that are in the rejected set
- System transactions should always be accepted (not rejected)
- All unused fields and imports must be removed
- Function signatures should be updated to remove the `context` parameter where no longer needed
