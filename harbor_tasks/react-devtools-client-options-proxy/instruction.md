# React DevTools: Support connecting through a reverse proxy

## Problem

When running React DevTools behind a reverse proxy, the DevTools client cannot connect to the server through the proxy. The DevTools server always tells connecting clients to use the same host and port the server is bound to locally (e.g., `localhost:8097`). There is no way to specify:

1. A **WebSocket subpath** (e.g., `/__react_devtools__/`) — needed when the proxy routes based on path
2. A **different host/port/protocol** for the client to connect to — needed when the proxy has a public hostname, a different port, or uses HTTPS/WSS

Additionally, if the server hits an error and retries, it loses its configuration and only retains the port number.

## Expected Behavior

- `connectToDevTools()` in the backend should accept an optional `path` parameter that gets appended to the WebSocket URI. Paths without a leading `/` should have one prepended automatically.
- `startServer()` in the standalone module should accept optional `path` and `clientOptions` parameters. When serving the connection script to clients, it should use the client override values (host, port, useHttps) instead of the raw server-bound values when overrides are provided.
- Error retry handlers in `startServer()` should forward all configuration parameters when re-invoking the server, not just the port.
- The Electron `preload.js` should read `REACT_DEVTOOLS_PATH`, `REACT_DEVTOOLS_CLIENT_HOST`, `REACT_DEVTOOLS_CLIENT_PORT`, and `REACT_DEVTOOLS_CLIENT_USE_HTTPS` environment variables and return them to `app.html`.
- `app.html` should destructure and pass these new values through to `startServer()`.

## Files to Look At

- `packages/react-devtools-core/src/backend.js` — `connectToDevTools()` function, WebSocket URI construction
- `packages/react-devtools-core/src/standalone.js` — `startServer()` function, HTTP response template, error retry handlers
- `packages/react-devtools/preload.js` — Environment variable reading for the Electron app
- `packages/react-devtools/app.html` — Electron app entry point, calls `startServer()`
