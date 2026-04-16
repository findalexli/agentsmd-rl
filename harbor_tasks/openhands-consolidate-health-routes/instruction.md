# Consolidate Health Routes to app_server Package

## Problem

The OpenHands codebase is undergoing a V1 API migration to consolidate all routes in the `openhands/app_server/` package. Currently, the health check endpoints are scattered in the legacy location and need to be moved to the new app_server structure.

The health endpoints (`/alive`, `/health`, `/server_info`, `/ready`) currently exist in the old V0 server structure at `openhands/server/routes/health.py`. These need to be moved to a new `openhands/app_server/status/` package using the feature-based routing pattern with FastAPI's `APIRouter`.

Additionally, `openhands/runtime/utils/system_stats.py` contains shared utilities that are used by both the runtime and the server endpoints. This file needs to be relocated to the `openhands/app_server/status/` package as well, with all import references updated accordingly.

## What You Need to Do

1. **Create the new status router** at `openhands/app_server/status/status_router.py` that:
   - Uses `APIRouter` with the tag `'Status'`
   - Implements four endpoints with the following exact return values:
     - `GET /alive` — returns `{"status": "ok"}`
     - `GET /health` — returns the string `"OK"`
     - `GET /ready` — returns the string `"OK"`
     - `GET /server_info` — returns the result of calling `get_system_info()`
   - Imports `get_system_info` from the relocated `system_stats` module within the same package

2. **Relocate system_stats.py** from `openhands/runtime/utils/` to `openhands/app_server/status/`. The relocated module must export three callable functions: `get_system_info`, `get_system_stats`, and `update_last_execution_time`. The `get_system_info()` function returns a dictionary that contains the keys `uptime`, `idle_time`, and `resources`.

3. **Update imports in server/app.py** — The server's main app file currently imports the health endpoints from the old location. Change the import to use the new status router from the `openhands.app_server.status` package, and register it with the FastAPI app using `include_router`. The old health endpoint registration function should no longer be called.

4. **Update imports in action_execution_server.py** — Any imports of `system_stats` from `openhands.runtime.utils` should be updated to import from `openhands.app_server.status` instead.

5. **Update imports in action_execution_client.py** — The `update_last_execution_time` function should be imported from the new location under `openhands.app_server.status.system_stats`.

6. **Remove the old health.py** file from `openhands/server/routes/`

## Relevant Files

- `openhands/server/routes/health.py` — current location of health endpoints (to be removed)
- `openhands/server/app.py` — main server application that registers routes
- `openhands/runtime/utils/system_stats.py` — system stats utilities (to be moved)
- `openhands/runtime/action_execution_server.py` — uses system_stats
- `openhands/runtime/impl/action_execution/action_execution_client.py` — uses system_stats
- `openhands/app_server/` — target location for the new status package

## Expected Behavior

After the migration:
- All four health endpoints (`/alive`, `/health`, `/server_info`, `/ready`) should be accessible
- `/alive` returns `{"status": "ok"}`, `/health` and `/ready` each return the string `"OK"`, and `/server_info` returns the output of `get_system_info()`
- The status router is tagged with `'Status'` for API documentation
- `get_system_info()` returns a dictionary containing the keys `uptime`, `idle_time`, and `resources`
- In `server/app.py`, the old health endpoint registration is replaced with the new status router registered via `app.include_router`
- No import errors should occur in the modified files
- The old health.py file should no longer exist