# Task: slime-httpx-disable-system-proxy

Internal SGLang HTTP clients (used for operations like `/generate`, `/update_weights_from_distributed`, and `/health`) are incorrectly reading `HTTP_PROXY` / `HTTPS_PROXY` environment variables and routing intra-cluster traffic through the system proxy. On clusters where these variables are set for external internet access (e.g., Weights & Biases logging), this causes `503 Service Unavailable` errors because the proxy cannot reach internal service endpoints.

The two affected clients live in `slime/utils/http_utils.py`:
1. The client created by `init_http_client()` — used for local intra-cluster calls
2. The client created in `_HttpPosterActor.__init__()` (inside `_init_ray_distributed_post`) — used for distributed posting

**Correct behavior:** Both clients must communicate intra-cluster without using the system proxy, regardless of environment variable settings.

**File to modify:** `slime/utils/http_utils.py`