# Control UI Bootstrap Endpoint Leaks Internal Runtime Identifiers

## Bug Description

The Control UI bootstrap endpoint (`/api/control-ui/bootstrap`) returns more data than the page actually needs. Specifically, the JSON payload includes internal runtime identifiers — an agent ID and a server version string — that the Control UI page does not use and should not be exposed to clients.

The affected code spans three layers:

1. **Shared contract** (`src/gateway/control-ui-contract.ts`): The `ControlUiBootstrapConfig` type declares fields the UI never consumes.
2. **Gateway handler** (`src/gateway/control-ui.ts`): The handler populates these extra fields by reading from assistant identity and resolving the runtime service version from `process.env`.
3. **UI bootstrap controller** (`ui/src/ui/controllers/control-ui-bootstrap.ts`): The `loadControlUiBootstrapConfig` function reads and stores these unnecessary fields into the UI state.
4. **Vite dev stub** (`ui/vite.config.ts`): The local dev server mock response includes the extra field in its stub payload.

## Expected Behavior

The bootstrap payload should only contain the display-relevant fields the Control UI actually needs: the configured base path, assistant display name, and assistant avatar. Internal identifiers like the agent ID and runtime version should not be part of this response — version information is already available through the normal gateway handshake, and the UI refreshes assistant identity after connecting.

## Relevant Files

- `src/gateway/control-ui-contract.ts` — shared TypeScript type
- `src/gateway/control-ui.ts` — gateway HTTP handler
- `ui/src/ui/controllers/control-ui-bootstrap.ts` — UI-side bootstrap loader
- `ui/vite.config.ts` — Vite dev server with mock bootstrap endpoint
- `src/gateway/control-ui.http.test.ts` — gateway-side test
- `ui/src/ui/controllers/control-ui-bootstrap.test.ts` — UI-side test
