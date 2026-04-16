# Workspace routing causes convoluted request round-trips

## Problem

In the opencode server, workspace routing and instance bootstrapping are handled by two separate middleware layers, causing a convoluted round-trip for worktree workspace requests.

The workspace router in `packages/opencode/src/control-plane/workspace-router-middleware.ts` forwards requests to workspace adaptors (like the worktree adaptor), which then re-create the HTTP request, set the `x-opencode-directory` header, and call back into the server via `Server.Default().fetch()`. This is inefficient because:

- The router already knows the workspace's directory but delegates to an adaptor that has to reconstruct the request
- The `Instance.provide` middleware in `packages/opencode/src/server/instance.ts` applies to all routes including those from remote workspace adaptors that don't need project bootstrapping
- There's no way to provide different `Instance.provide` contexts for different workspace types without going through the adaptor fetch dance

## Current architecture

- **Workspace routing** (`workspace-router-middleware.ts`): Decides whether to handle requests locally or forward to workspace adaptors. Does not call `Instance.provide`.
- **Instance bootstrapping** (`instance.ts`): The `InstanceRoutes` function wraps handlers in `Instance.provide({ directory, init: InstanceBootstrap, ... })` after resolving the directory from query string parameter `directory` or header `x-opencode-directory`.

## Expected behavior

Consolidate workspace routing and instance bootstrapping to eliminate the round-trip for worktree requests:

1. **Single routing entry point** — A router module should export a `WorkspaceRouterMiddleware` function that handles both routing decisions and instance bootstrapping

2. **Directory resolution in the router** — The router must extract the directory from the `directory` query parameter or `x-opencode-directory` header (same logic as currently in `instance.ts`)

3. **Routing branches to support**:
   - **No workspace parameter**: Wrap the request in `Instance.provide` with the resolved directory and `init: InstanceBootstrap`
   - **Worktree workspace**: Call `Instance.provide` directly with the workspace's directory (skip the adaptor round-trip)
   - **Remote workspace**: Forward through the adaptor's `fetch` method (adaptor handles the remote call)

4. **Delegation**: The router should delegate to `InstanceRoutes` for actual request handling

5. **Cleanup**: The old `workspace-router-middleware.ts` file in the control-plane directory should be removed, and `server.ts` should import from the new location. The worktree adaptor's `fetch` method should throw an error since it's no longer called directly.

## Files to investigate

- `packages/opencode/src/control-plane/workspace-router-middleware.ts` — current workspace routing with adaptor delegation
- `packages/opencode/src/server/instance.ts` — current `InstanceRoutes` with `Instance.provide` middleware
- `packages/opencode/src/control-plane/adaptors/worktree.ts` — worktree adaptor with `fetch` logic that calls back to server
- `packages/opencode/src/server/server.ts` — imports the workspace router middleware
