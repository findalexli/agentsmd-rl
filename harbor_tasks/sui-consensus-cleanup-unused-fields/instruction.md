# Task: Remove Unused Consensus Fields and No-op Feature Flag

## Problem Description

The codebase contains unused fields and a feature flag that should be cleaned up:

1. **Unused feature flag**: The `always_accept_system_transactions` field in `ConsensusProtocolConfig` (in `consensus/config/src/consensus_protocol_config.rs`) is now a no-op. All protocol versions use `true` for this setting, and the feature has been fully rolled out. This field and its associated getter method should be removed.

2. **Unused field in CommittedSubDag**: The `CommittedSubDag` struct in `consensus/core/src/commit.rs` has an `always_accept_system_transactions` field that was used to communicate the feature flag value. Since the feature is always enabled, this field is redundant and should be removed, along with updates to:
   - The `CommittedSubDag::new()` constructor
   - The `load_committed_subdag_from_store()` function (which also doesn't need the `Context` parameter anymore)
   - All call sites in `commit_observer.rs`, `dag_state.rs`, `linearizer.rs`, `test_dag_builder.rs`, `leader_schedule.rs`, and `consensus_handler.rs`

3. **Unused column family**: The `events` column family in `AuthorityPerpetualTables` (`crates/sui-core/src/authority/authority_store_tables.rs`) is deprecated and unused. It should be removed along with the now-unused import in `authority.rs`.

4. **Simplified transaction parsing**: In `crates/sui-core/src/consensus_types/consensus_output_api.rs`, the `parse_block_transactions()` function should be simplified to remove the `always_accept_system_transactions` parameter. Since system transactions are always accepted, the rejection logic should only apply to user transactions.

5. **Consensus manager update**: Remove the call to `config.consensus_always_accept_system_transactions()` in `crates/sui-core/src/consensus_manager/mod.rs`.

## Expected Changes

- The `always_accept_system_transactions` field should be removed from `ConsensusProtocolConfig`
- The `ConsensusProtocolConfig::always_accept_system_transactions()` getter method should be removed
- The `ConsensusProtocolConfig::new()` constructor signature should be updated
- The `CommittedSubDag` struct should no longer have the `always_accept_system_transactions` field
- The `load_committed_subdag_from_store()` function should no longer take `context: &Arc<Context>` as first parameter
- The `events` column family should be removed from `AuthorityPerpetualTables`
- The `Event` import should be removed from `authority.rs` (keeping `EventID`)
- The `parse_block_transactions()` function signature and logic should be simplified
- The `consensus_manager/mod.rs` should not pass the flag to the protocol config builder

## Testing

After making these changes:
1. Run `cargo check` to ensure the code compiles
2. Run `cargo xclippy` to ensure no linting errors
3. Run `cargo nextest run --lib -p consensus-config` to ensure tests pass

Note: This is a cleanup PR that removes dead code. The changes are straightforward removal of unused fields and simplification of logic.
