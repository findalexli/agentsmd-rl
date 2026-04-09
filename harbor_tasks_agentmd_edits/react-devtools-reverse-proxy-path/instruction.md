# Enable React DevTools Client to Connect Through a Reverse Proxy

## Problem

React DevTools currently hardcodes the WebSocket connection URI to `protocol://host:port` when connecting the backend (running in the inspected app) to the standalone DevTools frontend. There is no way to append a custom path to the WebSocket URI, and no way to tell the served client script to connect to a different host/port/protocol than the local server.

This makes it impossible to route DevTools traffic through a reverse proxy that serves the WebSocket on a subpath (e.g. `wss://remote.example.com:443/__react_devtools__/`).

## Expected Behavior

1. **`connectToDevTools()` in `packages/react-devtools-core/src/backend.js`** should accept an optional `path` parameter that gets appended to the WebSocket URI. If the path doesn't start with `/`, one should be added automatically. An empty path should have no effect.

2. **`startServer()` in `packages/react-devtools-core/src/standalone.js`** should accept optional `path` and `clientOptions` parameters. `clientOptions` allows overriding the host, port, and protocol that appear in the script served to connecting clients (so the client connects through the proxy, not directly to the local server). When `clientOptions` fields are not set, they should fall back to the corresponding server values.

3. **The Electron app** (`packages/react-devtools/preload.js` and `app.html`) should read new environment variables (`REACT_DEVTOOLS_PATH`, `REACT_DEVTOOLS_CLIENT_HOST`, `REACT_DEVTOOLS_CLIENT_PORT`, `REACT_DEVTOOLS_CLIENT_USE_HTTPS`) and pass them through to the standalone server.

4. **Documentation** — update the README files for both `packages/react-devtools-core/` and `packages/react-devtools/` to document the new parameters and environment variables, including the reverse proxy use case.

## Files to Look At

- `packages/react-devtools-core/src/backend.js` — `connectToDevTools()` function and `ConnectOptions` type
- `packages/react-devtools-core/src/standalone.js` — `startServer()` function
- `packages/react-devtools/preload.js` — Electron preload script that reads env vars
- `packages/react-devtools/app.html` — Electron app entry that calls `startServer()`
- `packages/react-devtools-core/README.md` — API documentation for the core package
- `packages/react-devtools/README.md` — User-facing documentation for the Electron app
