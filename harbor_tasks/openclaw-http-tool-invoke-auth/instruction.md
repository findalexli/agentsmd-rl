# Gateway HTTP Tool Invoke Missing Authorization Controls

## Bug Report

The Gateway HTTP `POST /tools/invoke` endpoint has several security gaps in its authorization flow:

### 1. No Scope Verification

The endpoint authenticates the bearer token but never verifies that the caller holds the required operator scope before executing a tool. Any valid gateway token holder can invoke arbitrary tools, even if they should only have read access.

The endpoint must require an `operator.write` scope for tool invocation requests. The handler must:
- Import `resolveGatewayRequestedOperatorScopes` from `./http-auth-helpers` to extract requested scopes from the request
- Import `authorizeOperatorScopesForMethod` from `./method-scopes` to perform scope authorization
- Call `authorizeOperatorScopesForMethod("agent", requestedScopes)` to check authorization for the `agent` method
- Return HTTP 403 with error type `"forbidden"` and message containing `"missing scope"` when authorization fails

### 2. Owner-Only Tools Exposed on HTTP Surface

The tool policy pipeline applies owner-only filtering for WebSocket/internal callers, but the HTTP tool invocation path skips this step entirely. Tools marked with `ownerOnly: true` are available to any authenticated HTTP caller, which defeats the owner-only policy.

The HTTP surface does not bind a device-owner identity, so owner-only tools must stay unavailable even when callers assert admin scopes.

The handler must:
- Import `applyOwnerOnlyToolPolicy` from the tool-policy module
- Call `applyOwnerOnlyToolPolicy(tools, false)` with `false` as the second argument to indicate no owner identity
- Apply owner-only filtering before the gateway deny filtering step

### 3. Incomplete Default HTTP Deny List

The `DEFAULT_GATEWAY_HTTP_TOOL_DENY` array in `src/security/dangerous-tools.ts` blocks session orchestration and control-plane tools but does not block direct command execution and file mutation tools. Several tools recognized as dangerous are missing from the HTTP deny list.

The deny list must include at minimum these 7 additional tools:
- `exec` - Direct command execution (immediate RCE surface)
- `spawn` - Arbitrary child process creation (immediate RCE surface)
- `shell` - Shell command execution (immediate RCE surface)
- `fs_write` - Arbitrary file mutation on the host
- `fs_delete` - Arbitrary file deletion on the host
- `fs_move` - Arbitrary file move/rename on the host
- `apply_patch` - Patch application that can rewrite arbitrary files
- `nodes` - Node command relay that can reach system.run on paired hosts

The deny list must maintain at least 10 entries total (the original entries plus the new high-risk tools).

### Relevant Files

- `src/gateway/tools-invoke-http.ts` — HTTP tool invocation handler
- `src/security/dangerous-tools.ts` — shared deny list constants
- `src/gateway/http-auth-helpers.ts` — scope resolution utilities
- `src/gateway/method-scopes.ts` — scope authorization logic
