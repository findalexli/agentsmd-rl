# Fix: RTensor fetch failure for large multimodal batches

## Problem

When training large multimodal batches (especially with multi-image samples), `RTensor.localize(...)` issues one HTTP request per shard during `compute_logp`. For batches with many images, this creates a large number of individual HTTP requests to the RPC server, making the transfer path fragile and causing `Connection reset by peer` failures.

## Root Cause

`HttpRTensorBackend.fetch()` creates one `asyncio.gather` task per shard, each making an independent HTTP GET to `/data/<shard_id>`. With large multimodal batches containing multiple images per sample, the fan-out of concurrent requests overwhelms the connection.

## Expected Behavior

### 1. Batch endpoint on the RPC server

Add a `POST /data/batch` endpoint to `areal/infra/rpc/rpc_server.py` that accepts multiple shard IDs in a single request and returns all corresponding tensor data in one response. Use the existing `serialize_value` / `deserialize_value` functions from `areal.infra.rpc.serialization` for tensor serialization, along with `orjson` for encoding/decoding.

**Request schema:** JSON body with a single field:
- `"shard_ids"`: a list of strings

Example:
```json
{"shard_ids": ["id1", "id2", "id3"]}
```

**Success response (all shards found):** HTTP 200, content type `application/octet-stream`. The response body is `orjson.dumps(serialize_value(tensors))` where `tensors` is a list of the fetched tensor objects in the **same order** as the requested `shard_ids`.

**Empty request:** When `"shard_ids"` is an empty list `[]`, return HTTP 200 with `orjson.dumps(serialize_value([]))` — i.e., a serialized empty list that round-trips through `deserialize_value(orjson.loads(...))` as an empty Python list.

**Missing shards response:** When one or more requested shard IDs do not exist in the store, return HTTP 400 with a JSON body containing these keys:
- `"status"`: the string `"error"`
- `"message"`: a human-readable error description
- `"missing_shard_ids"`: a JSON list of the shard ID strings that were **not** found. Shard IDs that *were* found must not appear in this list.

Example:
```json
{"status": "error", "message": "One or more requested shards were not found", "missing_shard_ids": ["missing-1", "missing-2"]}
```

**Invalid input response:** When the request body does not conform to the expected schema — specifically, when `"shard_ids"` is not a list of strings — return HTTP 400 with a JSON error body containing:
- `"status"`: the string `"error"`
- `"message"`: the string `"Expected JSON body with string list field 'shard_ids'"`

### 2. Batch HTTP fetches in the client

Update `HttpRTensorBackend` in `areal/infra/rpc/rtensor.py` to batch fetches instead of issuing one HTTP request per shard.

**Grouping by node:** Shards must be grouped by their `node_addr` field. All shards targeting the same node should be fetched together via the new batch endpoint (POST to `http://<node_addr>/data/batch` with `json={"shard_ids": [...]}`).

**Configurable chunking:** `HttpRTensorBackend` must accept a constructor parameter named `max_shards_per_request` (type `int`, default a positive integer) that controls the maximum number of shards sent in a single batch request. When a single node has more shards than this limit, they must be fetched in multiple sequential chunked requests of at most `max_shards_per_request` shards each. Passing a non-positive value (zero or negative) to `max_shards_per_request` must raise `ValueError`.

**Order preservation:** The `fetch()` method must return results in the **same order** as the input `shards` list, regardless of how shards are grouped by node or split into chunks.

**Batch response deserialization:** The client must deserialize the batch response bytes via `orjson.loads` followed by `deserialize_value` to recover the list of tensor objects.

### 3. Existing behavior preserved

The existing `GET /data/<shard_id>` single-shard endpoint must continue to work correctly.

## Files to Modify

- `areal/infra/rpc/rpc_server.py` — add `/data/batch` endpoint
- `areal/infra/rpc/rtensor.py` — batch HTTP fetches by node, add chunking
