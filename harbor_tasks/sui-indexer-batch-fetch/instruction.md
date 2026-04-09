# Optimize Indexer RPC Fetching with Concurrent Batch Operations

## Problem

The `sui-indexer-alt-reader` crate makes inefficient sequential RPC calls when fetching data:

1. **Checkpoint fetching** (`crates/sui-indexer-alt-reader/src/checkpoints.rs`): The `LedgerGrpcReader` implementation processes checkpoint keys one-by-one in a sequential `for` loop, issuing individual `get_checkpoint` RPC calls. This is slow when multiple checkpoints are requested.

2. **Transaction event fetching** (`crates/sui-indexer-alt-reader/src/events.rs`): Similarly, the `TransactionEventsKey` loader makes sequential `get_transaction` RPC calls for each key, rather than batching them.

## What Needs to Change

### Checkpoints Module

Refactor the checkpoint fetching to use concurrent futures:

- Replace the sequential `for key in keys` loop with `futures::future::try_join_all`
- Transform keys into async futures that each make an individual RPC call
- Collect results concurrently and handle `NotFound` errors by returning `Ok(None)` for those items
- Flatten the results to build the final HashMap

### Events Module

Refactor the event fetching to use batch RPC:

- Replace sequential `get_transaction` calls with a single `batch_get_transactions` RPC
- Collect all transaction digests upfront into a request
- Use `BatchGetTransactionsRequest` with appropriate read mask fields (`digest`, `events.bcs`, `timestamp`)
- Process the batch response by iterating through `transactions`, extracting events and timestamps
- Handle missing transactions gracefully (filter them out)

## Verification

After your changes:

1. `cargo check -p sui-indexer-alt-reader` should pass
2. The code should compile without warnings
3. The checkpoint loader should use `try_join_all` for concurrent fetching
4. The events loader should use `batch_get_transactions` instead of sequential calls

## Files to Modify

- `crates/sui-indexer-alt-reader/src/checkpoints.rs` - Checkpoints `Loader` implementation
- `crates/sui-indexer-alt-reader/src/events.rs` - Transaction events `Loader` implementation

## Context

This is a performance optimization for the Sui blockchain indexer. The dataloader pattern (from `async_graphql::dataloader`) is used to batch and cache data fetches for GraphQL queries. Making these operations concurrent/batched significantly improves query performance when multiple items are requested.

The existing pattern uses sequential loops which causes N round-trip RPC calls. The optimized pattern should:
- For checkpoints: Fire all RPCs concurrently and await all results
- For events: Use the batch API which accepts multiple digests in a single call

Both loaders are in the `LedgerGrpcReader` struct and implement the `Loader` trait from async-graphql.
