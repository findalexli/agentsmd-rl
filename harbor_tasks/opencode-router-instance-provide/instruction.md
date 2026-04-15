# Workspace routing and Instance.provide are split across two middleware layers

## Problem

In the opencode server, there are two separate middleware concerns that should be unified:

1. **Workspace routing** — in `packages/opencode/src/control-plane/workspace-router-middleware.ts`, this middleware decides whether to handle requests locally or forward them to a workspace adaptor (e.g., worktree). However, it doesn't handle `Instance.provide` at all.

2. **Instance bootstrapping** — in `packages/opencode/src/server/instance.ts`, a Hono middleware inside `InstanceRoutes` resolves the `directory` parameter (from query string or `x-opencode-directory` header), then wraps the handler in `Instance.provide({ directory, init: InstanceBootstrap, ... })`.

This split causes several issues:

- The workspace router forwards requests to workspace adaptors (like the worktree adaptor), which then have to re-create the HTTP request, set headers, and call `Server.Default().fetch()` just to get back into the same middleware chain. This is a convoluted round-trip.
- For worktree workspaces specifically, the adaptor has to reconstruct the entire request with the right `x-opencode-directory` header, even though the router already knows the workspace's directory.
- The `Instance.provide` middleware in `InstanceRoutes` is applied to every route handler, even for requests that come from remote workspace adaptors that don't need project bootstrapping.
- There's no way to provide different `Instance.provide` contexts for different workspace types without going through the adaptor fetch dance.

## Expected behavior

The workspace routing and instance bootstrapping should be consolidated into a single router module at `packages/opencode/src/server/router.ts`. This router should:

- Export a middleware function named `WorkspaceRouterMiddleware`
- Take over the `Instance.provide` responsibility that is currently in `InstanceRoutes`
- Handle directory resolution from query param `directory` and header `x-opencode-directory` directly
- For requests without a workspace parameter, wrap in `Instance.provide` with the resolved directory
- For worktree workspaces, call `Instance.provide` directly with the workspace's directory instead of going through the adaptor's fetch
- For remote workspaces, continue forwarding through the adaptor
- The old `workspace-router-middleware.ts` in the control-plane directory should be removed
- The worktree adaptor's `fetch` method is no longer needed and can throw

The router must have at least two separate `Instance.provide` calls to handle: (1) requests with no workspace parameter, and (2) worktree workspace requests.

## Files to investigate

- `packages/opencode/src/control-plane/workspace-router-middleware.ts` — current workspace routing
- `packages/opencode/src/server/instance.ts` — current `InstanceRoutes` with Instance.provide middleware
- `packages/opencode/src/control-plane/adaptors/worktree.ts` — worktree adaptor with fetch logic
- `packages/opencode/src/server/server.ts` — imports the workspace router middleware
