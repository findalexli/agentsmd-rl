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

`POST /data/batch` should be handled by a dedicated endpoint on the data proxy that mirrors the behavior of the corresponding handler in the Flask RPC server (`rpc_server.py`). Refer to that implementation for the expected request/response contract.

## Key Files

- `areal/experimental/inference_service/data_proxy/app.py` — the FastAPI data proxy (missing the batch endpoint)
- `areal/infra/rpc/rpc_server.py` — the Flask RPC server (has the working batch endpoint for reference)
