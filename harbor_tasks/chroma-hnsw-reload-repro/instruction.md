# Task: Add HNSW Index Reload Regression Test

## Problem Description

The HNSW (Hierarchical Navigable Small World) index library used by Chroma has a bug where reloading an index after certain garbage collection operations can trigger an assertion failure. This occurs when:

1. Documents are added to a SPANN index in batches
2. The index is flushed and reloaded between batches
3. Garbage collection removes some head nodes
4. The next reload attempts to access deleted nodes

The bug manifests as an integrity check failure in hnswlib during the reload operation.

## Your Task

Add a regression test that reproduces this HNSW index reload bug. The test should:

1. Be located at `rust/index/tests/hnsw_reload_repro.rs`
2. Use the `SpannIndexWriter` and `SpannIndexReader` APIs
3. Implement batch document processing with parallel workers
4. Use child process isolation to detect assertion failures (since the bug causes a crash)
5. Run multiple seeds to find failing cases

## Key Requirements

- Use `tokio::runtime::Builder` with `new_multi_thread()` for async operations
- Set appropriate thread stack size (8MB recommended)
- Use `SpannIndexWriter::from_id()` to reopen existing indices between batches
- Process documents in parallel using tokio tasks
- Flush the index after each batch and reopen for the next batch
- The test should attempt to load the HNSW index via `SpannIndexReader::from_id()`
- Use environment variables for configuration (seed, batch count, worker count, etc.)
- Implement child process spawning to isolate crashes

## Testing the Fix

Once the test is added, verify it compiles:
```bash
cd rust
cargo test --test hnsw_reload_repro -p chroma-index --no-run
```

## Key Files to Reference

- Look at existing tests in `rust/index/tests/` for patterns
- Study `SpannIndexWriter` and `SpannIndexReader` in `rust/index/src/spann/`
- Review `HnswIndexProvider` in `rust/index/src/hnsw_provider.rs`

Note: The actual bug is in the hnswlib dependency. This test demonstrates the issue and should pass once hnswlib is updated with the fix.
