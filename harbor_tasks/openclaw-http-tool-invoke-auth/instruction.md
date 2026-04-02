# Gateway HTTP Tool Invoke Missing Authorization Controls

## Bug Report

The Gateway HTTP `POST /tools/invoke` endpoint has several security gaps in its authorization flow:

### 1. No Scope Verification

The endpoint authenticates the bearer token but never verifies that the caller holds the required operator scope before executing a tool. Any valid gateway token holder can invoke arbitrary tools, even if they should only have read access. The endpoint should require an `operator.write` scope for tool invocation requests.

### 2. Owner-Only Tools Exposed on HTTP Surface

The tool policy pipeline applies owner-only filtering for WebSocket/internal callers, but the HTTP tool invocation path skips this step entirely. Tools marked with `ownerOnly: true` are available to any authenticated HTTP caller, which defeats the owner-only policy.

Look at `src/gateway/tools-invoke-http.ts` — the gateway deny filtering step (`gatewayFiltered`) operates on `subagentFiltered` directly without first removing owner-only tools. Compare this with how other surfaces handle tool filtering.

### 3. Incomplete Default HTTP Deny List

The `DEFAULT_GATEWAY_HTTP_TOOL_DENY` array in `src/security/dangerous-tools.ts` blocks session orchestration and control-plane tools but does not block direct command execution and file mutation tools. Several tools that are already recognized as dangerous in `DANGEROUS_ACP_TOOL_NAMES` (in the same file) are missing from the HTTP deny list. Additionally, the `nodes` tool (which can relay commands to paired hosts) is also unblocked.

### Relevant Files

- `src/gateway/tools-invoke-http.ts` — HTTP tool invocation handler
- `src/security/dangerous-tools.ts` — shared deny list constants
- `src/gateway/http-auth-helpers.ts` — scope resolution utilities
- `src/gateway/method-scopes.ts` — scope authorization logic
