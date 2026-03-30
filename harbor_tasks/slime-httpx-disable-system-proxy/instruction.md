# Internal SGLang httpx clients route through system proxy causing 503 errors

## Problem

In `slime/utils/http_utils.py`, the `httpx.AsyncClient` instances used for internal SGLang communication (e.g., `/generate`, `/update_weights_from_distributed`, `/health`) default to `trust_env=True`. This means they read `http_proxy`/`https_proxy` environment variables and route all requests through the configured proxy.

On clusters where proxy environment variables are set for external internet access (e.g., Weights & Biases logging), all intra-cluster SGLang HTTP calls are inadvertently routed through the proxy, resulting in `503 Service Unavailable` errors.

The standard workaround of adding `10.0.0.0/8` to `no_proxy` does not work for httpx -- unlike `requests`, httpx does not support CIDR notation in `no_proxy` (only exact hostnames/IPs and the `*` wildcard are supported).

There are two `httpx.AsyncClient` instances that need to be fixed:
1. The local client created in `init_http_client()`
2. The Ray actor client created in the `_HttpPosterActor.__init__()` method inside `_init_ray_distributed_post()`

## Expected Behavior

Both `httpx.AsyncClient` instances should be configured to ignore system proxy settings, since they are exclusively used for intra-cluster SGLang communication and should never be routed through a system proxy.

## File to Modify

- `slime/utils/http_utils.py` -- the `init_http_client()` function and the `_HttpPosterActor.__init__()` method
