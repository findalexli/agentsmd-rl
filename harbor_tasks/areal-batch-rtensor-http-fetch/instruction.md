# Fix: RTensor fetch failure for large multimodal batches

## Problem

When training large multimodal batches (especially with multi-image samples), `RTensor.localize(...)` issues one HTTP request per shard during `compute_logp`. For batches with many images, this creates a large number of individual HTTP requests to the RPC server, making the transfer path fragile and causing `Connection reset by peer` failures.

## Root Cause

`HttpRTensorBackend.fetch()` creates one `asyncio.gather` task per shard, each making an independent HTTP GET to `/data/<shard_id>`. With large multimodal batches containing multiple images per sample, the fan-out of concurrent requests overwhelms the connection.

## Expected Behavior

1. Add a `/data/batch` endpoint on the RPC server that accepts a list of shard IDs and returns all shards in one response
2. Update `HttpRTensorBackend` to group shards by `node_addr` and batch them into fewer requests
3. Support configurable `max_shards_per_request` chunking for very large batches
4. Report missing shards with structured error messages
5. Preserve the original request order across grouped and chunked batch fetches

## Files to Modify

- `areal/infra/rpc/rpc_server.py` -- add `/data/batch` endpoint
- `areal/infra/rpc/rtensor.py` -- batch HTTP fetches by node, add chunking
