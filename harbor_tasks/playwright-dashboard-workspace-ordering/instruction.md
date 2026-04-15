# Dashboard doesn't show current workspace sessions first

## Problem

The Playwright MCP dashboard groups browser sessions by workspace directory. When the dashboard is launched (e.g., from a non-workspace directory or the global scope), it doesn't correctly identify which workspace group is "current". As a result, workspace groups appear in arbitrary order instead of showing the current workspace first and expanded.

The `/api/sessions/list` API endpoint in the dashboard backend does not provide client workspace information to the frontend, so the grid component has no way to determine which workspace to prioritize.

## Expected Behavior

### 1. API must include client workspace info in session list response

The `/api/sessions/list` endpoint currently only sends session data. It must be updated to also include client information containing the workspace directory.

- The backend handler must import the client info creation function from `'../cli-client/registry'`.
- Inside the `/api/sessions/list` handler, obtain the client info containing the workspace directory.
- The response must include both `sessions` and `clientInfo` fields.

### 2. Grid must sort current workspace group first, defaulting to `'Global'`

The grid component must use the client workspace information from the API to determine and prioritize the current workspace:

- When `clientInfo.workspaceDir` is present, use it to identify the current workspace group.
- When `clientInfo.workspaceDir` is undefined, treat `'Global'` as the current workspace.
- Use the identified current workspace value (not the raw `clientInfo.workspaceDir` property) when determining which group matches the current workspace.
- Current workspace groups should be listed first; all other groups remain sorted alphabetically via `localeCompare`.

### 3. Declare the new import in DEPS.list

Per the project's CLAUDE.md rules ("When creating or moving files, update the relevant DEPS.list to declare allowed imports"), the new import path `../cli-client/registry.ts` must be added to `packages/playwright-core/src/tools/dashboard/DEPS.list`.

## Files to Look At

- `packages/dashboard/src/grid.tsx` — React component that renders the session grid and handles workspace group ordering
- `packages/playwright-core/src/tools/dashboard/dashboardApp.ts` — Backend HTTP handler for the dashboard API, including `/api/sessions/list`
- `packages/playwright-core/src/tools/dashboard/DEPS.list` — Import boundary declarations for the dashboard module
