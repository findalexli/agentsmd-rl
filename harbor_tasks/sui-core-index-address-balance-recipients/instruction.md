# Task: Fix Address Balance Indexing in JSON-RPC

## Problem

The `transactions_to_addr` index in `crates/sui-core/src/jsonrpc_index.rs` is incomplete. When querying transactions using `queryTransactionBlocks` with the `ToAddress` filter, transactions that transfer funds to an address via **accumulator events** (address balance transfers) are not being returned.

Currently, the index only tracks addresses that receive objects through `mutated_objects`. However, with the introduction of address balances, a recipient can receive funds through accumulator events without any object ownership change. These addresses need to be included in the `transactions_to_addr` index.

## Expected Behavior

When a transaction transfers SUI to an address via accumulator events (address balance mechanism), that transaction should appear in `queryTransactionBlocks` results when filtering by `ToAddress` with the recipient's address.

## Files to Modify

- `crates/sui-core/src/jsonrpc_index.rs` - The `index_new_transaction_digest` method in `IndexStore`

## Key Areas

Look for the code that populates `self.tables.transactions_to_addr`. The current implementation only considers `mutated_objects` but should also include addresses from `accumulator_events`.

## Testing

The fix should ensure:
1. Accumulator event recipient addresses are indexed in `transactions_to_addr`
2. The code compiles without errors (`cargo check -p sui-core`)
3. The existing JSON-RPC test crate compiles (`cargo check -p sui-json-rpc-tests`)

Consult the root `CLAUDE.md` for development commands and conventions.
