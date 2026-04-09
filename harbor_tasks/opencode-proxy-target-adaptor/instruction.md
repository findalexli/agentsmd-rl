# Refactor workspace adaptor interface: replace fetch() with target() and add full HTTP proxy

## Problem

The current workspace adaptor interface requires each adaptor implementation to manually proxy HTTP requests via a `fetch()` method. This design has two major issues:

1. **Excessive complexity for adaptor implementors** — Every workspace adaptor must implement a full `fetch(config, input, init)` method that proxies HTTP requests. For remote environments, this means each adaptor has to manually construct and forward requests, which is duplicated boilerplate.

2. **No WebSocket support** — The `fetch()` API is HTTP-only and cannot handle WebSocket upgrades. This means features like terminal support in the web app that rely on WebSocket connections to remote workspaces are broken — the proxy layer has no path for upgrading connections.

## Expected Behavior

The adaptor interface should be simplified so that adaptors only need to declare *where* a workspace lives (local directory or remote URL), not *how* to proxy requests to it. A centralized proxy module should handle the actual HTTP and WebSocket proxying for remote targets.

Specifically:
- The `Adaptor` type should have a `target()` method instead of `fetch()`, returning a discriminated union describing whether the workspace is local (with a directory path) or remote (with a URL)
- A new proxy module should handle HTTP request forwarding and WebSocket upgrade proxying for remote targets, including proper hop-by-hop header stripping
- The workspace event loop should use the new target interface and skip SSE polling for local workspaces
- The router should use the target type to decide how to route requests, and should delegate WebSocket upgrades and HTTP requests to the proxy module
- The router should also accept workspace ID from an `x-opencode-workspace` header as a fallback to the query parameter

## Files to Look At

- `packages/opencode/src/control-plane/types.ts` — The `Adaptor` type definition and workspace types
- `packages/opencode/src/control-plane/adaptors/worktree.ts` — The worktree adaptor implementation
- `packages/opencode/src/control-plane/workspace.ts` — Workspace event loop that polls remote workspaces
- `packages/opencode/src/server/router.ts` — The workspace router middleware that dispatches requests
