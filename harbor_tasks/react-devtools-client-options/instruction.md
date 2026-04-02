# Bug Report: React DevTools WebSocket connection lacks path support and proxy configuration

## Problem

When running React DevTools behind a reverse proxy (e.g., nginx), the WebSocket connection cannot be established because there is no way to specify a custom URL path. The DevTools backend constructs the WebSocket URI using only `host` and `port`, producing URIs like `ws://localhost:8097` with no option to append a path segment. This makes it impossible to use DevTools through proxies that route based on URL paths.

Additionally, the standalone DevTools server always tells the injected client script to connect back using the same host/port/protocol the server is listening on. When a reverse proxy fronts the server, the client may need to connect to a completely different host, port, or protocol than the server's internal address.

## Expected Behavior

Developers should be able to configure a custom WebSocket path and override the client-facing connection parameters (host, port, HTTPS) so DevTools works correctly behind reverse proxies.

## Actual Behavior

The WebSocket URI has no path component. The standalone server's injected client script hardcodes the server's own listen address, and on server error retry, not all parameters are forwarded, causing silent configuration loss.

## Files to Look At

- `packages/react-devtools-core/src/backend.js`
- `packages/react-devtools-core/src/standalone.js`
