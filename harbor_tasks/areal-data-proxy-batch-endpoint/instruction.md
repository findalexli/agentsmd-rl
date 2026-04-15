# Bug: POST /data/batch returns HTTP 405 on the data proxy

## Context

AReaL's inference service has a **data proxy** (`areal/experimental/inference_service/data_proxy/app.py`) that fronts the Flask-based RPC server. The data proxy is a FastAPI application that mirrors the RPC server's endpoints for tensor shard storage and retrieval.

Recently, a batch tensor fetching feature was added that sends `POST /data/batch` to retrieve multiple tensor shards in a single round-trip. The corresponding endpoint was added to the Flask RPC server (`rpc_server.py`), but the FastAPI data proxy was not updated.

## Observed Behavior

When integration tests use the data proxy (instead of hitting the Flask RPC server directly), batch tensor fetching fails with:

```
HTTP 405 Method Not Allowed
```

The data proxy has no handler for `POST /data/batch`. FastAPI falls through to the parametric `/data/{shard_id}` route, which only supports `GET` and `PUT`.

## Expected Behavior

`POST /data/batch` should be handled by a dedicated endpoint on the data proxy that mirrors the behavior of the corresponding handler in the Flask RPC server (`rpc_server.py`).

### Request/Response Contract

**Request:**
- Method: `POST`
- Path: `/data/batch`
- Content-Type: `application/json`
- Body: JSON object with a single key `shard_ids` containing a list of string shard identifiers
  - Example: `{"shard_ids": ["shard_a", "shard_b"]}`

**Response:**
- Success (HTTP 200): Returns a JSON list where each element is the serialized value of the corresponding shard in the same order as the request
  - Example: `[[1, 2, 3], [4, 5, 6]]` for `{"shard_ids": ["shard_a", "shard_b"]}`
- Empty input (HTTP 200): Returns an empty JSON list `[]` when `shard_ids` is an empty list
- Invalid input (HTTP 400 or 422): Returned when:
  - `shard_ids` is not a list (e.g., string, integer)
  - `shard_ids` contains non-string items (e.g., list of integers like `[1, 2, 3]`)
- Missing shard error (HTTP 400, 404, 422, or 500): Returned when any shard_id in the list does not exist in storage

### Implementation Requirements

1. The endpoint must be registered with `@app.post("/data/batch")`
2. The route **must be declared before** the parametric `/data/{shard_id}` route in the source file. FastAPI matches routes in declaration order; if the parametric route comes first, `POST /data/batch` requests will be incorrectly routed to `/data/{shard_id}`.
3. The handler should accept a JSON body, extract the `shard_ids` field, validate that it is a list of strings, fetch each shard from `rtensor_storage`, serialize the values, and return them as a JSON list.

## Key Files

- `areal/experimental/inference_service/data_proxy/app.py` — the FastAPI data proxy (missing the batch endpoint)
- `areal/infra/rpc/rpc_server.py` — the Flask RPC server (has the working batch endpoint for reference)
