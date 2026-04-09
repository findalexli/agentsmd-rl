# sui-indexer-alt: Start Indexing at Network Tip

## Problem

The Sui indexer framework currently defaults all new pipelines to start indexing from checkpoint 0 (genesis), even when those pipelines have a pruner configured with a retention period. This causes:

1. **Unnecessary backfilling**: Pipelines with pruners waste time indexing old data that will immediately be pruned
2. **Inefficient resource usage**: Large retention periods mean processing months of historical data that isn't needed

The indexer needs a way to discover the network's current tip and use that to calculate an appropriate starting point for new pipelines with pruning enabled.

## What You Need to Do

Add support for discovering the latest checkpoint number and using it to calculate smart start points for new pipelines.

### Key Files to Modify

**Primary changes:**
- `crates/sui-indexer-alt-framework/src/ingestion/ingestion_client.rs` - Add `latest_checkpoint_number()` to `IngestionClientTrait`
- `crates/sui-indexer-alt-framework/src/ingestion/rpc_client.rs` - Implement for RPC client (use `GetServiceInfo`)
- `crates/sui-indexer-alt-framework/src/ingestion/store_client.rs` - Implement for object store client (read `_metadata/watermark/checkpoint_blob.json`)
- `crates/sui-indexer-alt-framework/src/ingestion/mod.rs` - Add fallback strategy and retry logic
- `crates/sui-indexer-alt-framework/src/lib.rs` - Update `Indexer` to use smart start logic
- `crates/sui-indexer-alt-framework/src/metrics.rs` - Add latency histogram for latest checkpoint queries

**Secondary changes:**
- `crates/sui-indexer-alt-framework/src/ingestion/error.rs` - Add error variant
- `crates/sui-indexer-alt-framework/src/ingestion/broadcaster.rs` - Update mock implementations
- `crates/sui-indexer-alt-framework/src/ingestion/streaming_client.rs` - Derive Clone for GrpcStreamingClient
- `crates/sui-indexer-alt-framework/src/pipeline/concurrent/mod.rs` - Fix flaky pruning test

### Requirements

1. **New trait method**: Add `async fn latest_checkpoint_number(&self) -> anyhow::Result<u64>` to `IngestionClientTrait`

2. **RPC implementation**: Use the existing `GetServiceInfo` RPC and extract `checkpoint_height` from the response

3. **Object store implementation**: Read the watermark file at `_metadata/watermark/checkpoint_blob.json`, parse the `checkpoint_hi_inclusive` field. Return 0 if the file doesn't exist.

4. **Fallback strategy**: In `IngestionService`, try the streaming client first (by peeking the stream), fall back to the ingestion client if streaming fails or is unavailable. Use exponential backoff for retries.

5. **Smart start logic**: In `add_pipeline()`, when there's no existing watermark and no `first_checkpoint`:
   - If the pipeline has a pruner with retention: start at `latest_checkpoint - retention` (clamped to 0)
   - Without a pruner: start at 0 (existing behavior)

6. **Priority order**: Existing watermark > first_checkpoint argument > pruner calculation

7. **Metrics**: Add an `ingested_latest_checkpoint_latency` histogram to track query performance

### Testing

The PR includes comprehensive unit tests. Verify your implementation by running:

```bash
cargo test -p sui-indexer-alt-framework --lib
```

Key test cases to verify:
- `latest_checkpoint_number_from_stream` - Gets checkpoint from streaming client
- `latest_checkpoint_number_stream_error_falls_back` - Falls back on stream error
- `test_latest_checkpoint_from_watermark` - Reads from watermark file
- `test_next_checkpoint_with_pruner_uses_retention` - Smart start with pruner
- `test_next_checkpoint_without_pruner_falls_back_to_genesis` - Falls back to 0
- `test_next_checkpoint_watermark_takes_priority_over_pruner` - Priority ordering
- `test_next_checkpoint_retention_exceeds_latest_checkpoint` - Handles overflow

### Tips

- Look at the existing `chain_id()` implementations in `rpc_client.rs` and `store_client.rs` for patterns
- The `ingestion_client.rs` has helper functions `retry_transient_with_slow_monitor()` and `transient_backoff()` for retry logic
- You'll need to make `GrpcStreamingClient` derive `Clone` to support the fallback strategy
- The `Indexer` struct needs a new `latest_checkpoint: u64` field to store the value read at startup
