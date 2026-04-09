# Refactor Ingestion Client to Use Helper Functions

The `ingestion_client.rs` file in the `sui-indexer-alt-framework` crate contains duplicated code patterns for retry logic with exponential backoff and slow-operation monitoring. This code duplication makes the codebase harder to maintain and extend.

## Task

Refactor the ingestion client to eliminate code duplication by creating reusable helper functions for:
1. Creating the exponential backoff configuration
2. Retrying fallible async operations with slow-operation monitoring and latency tracking

## Files to Modify

- `crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs` - Main refactoring
- `crates/sui-indexer-alt-framework/src/metrics.rs` - Add new latency metric for chain ID operations

## What to Look For

Look for duplicated patterns involving:
- `ExponentialBackoff` configuration with `MAX_TRANSIENT_RETRY_INTERVAL`
- `backoff::future::retry` calls
- `with_slow_future_monitor` usage with similar threshold handling
- Manual latency timer start/stop around retry operations

The `checkpoint()` method and the `get_or_init_chain_id()` method both contain similar patterns that should be extracted.

## Requirements

1. Create a `transient_backoff()` function that returns the standard exponential backoff configuration
2. Create a `retry_transient_with_slow_monitor()` async function that encapsulates:
   - The retry loop with exponential backoff
   - Slow operation monitoring via `with_slow_future_monitor`
   - Latency recording via histogram timers
3. Update the `checkpoint()` method to use these helpers
4. Remove the old `get_or_init_chain_id()` method and inline the chain ID fetching into `checkpoint()` using the new helpers
5. Fetch checkpoint data and chain ID concurrently (e.g., using `tokio::try_join!`)
6. Add a new `ingested_chain_id_latency` histogram metric to `IngestionMetrics` in `metrics.rs`
7. Update imports as needed (you'll need `std::future::Future`, `prometheus::Histogram`, etc.)

## Constraints

- Follow existing code style and patterns in the crate
- All code must compile without warnings
- The refactored code should maintain the same behavior as the original
- Use the existing `IE` alias for `IngestionError` consistently
