# Add shared HTTP transport failure observability

## Problem

The `server` and `cache` Elixir applications have no visibility into transport-layer failures. Bandit body read timeouts, request exceptions, and Thousand Island connection drops/recv/send errors are silently swallowed — there are no Prometheus metrics or structured log lines for these events. When incidents occur (e.g., a spike in client disconnects or body read timeouts), the oncall engineer has no transport-level telemetry to correlate with.

Currently `server/lib/tuist/http/` only handles Finch client-side metrics. There is no server-side (Bandit/Thousand Island) transport observability at all.

## Expected Behavior

1. A shared module in `tuist_common/lib/tuist_common/http/` should normalize Bandit and Thousand Island telemetry metadata — classifying body read timeouts, request failures, connection drops, and recv/send errors.

2. A shared PromEx plugin should emit low-cardinality Prometheus counters for:
   - Request body read timeouts (from Bandit)
   - Request failures — server errors and protocol errors (from Bandit)
   - Connection drops with a reason tag (from Thousand Island)
   - Connection recv/send errors (from Thousand Island)

3. A shared transport logger should log warnings for these events with enough metadata for incident correlation (request ID, span contexts, remote address, durations).

4. Both `server` and `cache` applications should wire in the shared logger and PromEx plugin on startup.

5. After implementing the code changes, update the relevant agent instruction files to reflect the new architecture. The `server/lib/tuist/http/` directory has an `AGENTS.md` that describes the HTTP context's responsibilities and boundaries — it should be updated to reflect that server-side transport observability is now shared via `tuist_common`.

## Files to Look At

- `tuist_common/lib/tuist_common/http/` — this is where shared modules should live
- `tuist_common/AGENTS.md` — describes tuist_common's role as cross-service shared utilities
- `server/lib/tuist/application.ex` — server startup telemetry wiring
- `server/lib/tuist/prom_ex.ex` — server PromEx plugin list
- `server/lib/tuist/http/AGENTS.md` — HTTP context agent instructions (needs updating)
- `cache/lib/cache/application.ex` — cache startup telemetry wiring
- `cache/lib/cache/prom_ex.ex` — cache PromEx plugin list
- `AGENTS.md` — root agent instructions (describes intent layer maintenance policy)
