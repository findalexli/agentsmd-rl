# Enhance `browser_network_requests` with Filtering and Debug Options

## Problem

The `browser_network_requests` MCP tool and its CLI counterpart (`network` command) only return a flat list of requests with method, URL, and status. When debugging API issues, developers need to:

1. **Filter by URL** — currently there's no way to narrow results to specific endpoints (e.g. only `/api/` routes), forcing manual scanning of potentially hundreds of requests.
2. **Inspect request headers** — custom headers (auth tokens, content types) are invisible in the output.
3. **Inspect request body** — POST/PUT payloads are not shown, making it hard to debug request issues.

Additionally, the existing `includeStatic` parameter name is inconsistent with the CLI option naming convention (which uses just `--static`). This should be unified.

## Expected Behavior

The `browser_network_requests` tool should accept these new optional parameters:

- **`filter`** (string) — a regexp pattern; only requests whose URL matches are returned.
- **`requestHeaders`** (boolean, default false) — when true, include the request headers in the output.
- **`requestBody`** (boolean, default false) — when true, include the request body/payload in the output.
- Rename `includeStatic` to `static` for consistency with the CLI.

The corresponding CLI `network` command must also expose these as `--filter`, `--request-headers`, and `--request-body` flags, mapping them to the appropriate MCP tool parameters.

When headers or body are included, render them under the request line (e.g. "Request headers:" / "Request body:" sections).

## Documentation Update

The project does not yet have a `.github/copilot-instructions.md` file. As part of this change, create one with guidelines for how automated PR reviewers should behave — focusing reviews on semantically meaningful issues (bugs, incorrect logic, security) rather than style, formatting, or naming nitpicks. Keep it concise.

## Files to Look At

- `packages/playwright-core/src/tools/backend/network.ts` — MCP tool definition and `renderRequest()` function
- `packages/playwright-core/src/tools/cli-daemon/commands.ts` — CLI command declarations (look for `networkRequests`)
- `.github/copilot-instructions.md` — needs to be created
