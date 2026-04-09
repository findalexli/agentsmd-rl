# Dashboard doesn't show current workspace sessions first

## Problem

The Playwright MCP dashboard groups browser sessions by workspace directory. When the dashboard is launched (e.g., from a non-workspace directory or the global scope), it doesn't correctly identify which workspace group is "current". As a result, workspace groups appear in arbitrary order instead of showing the current workspace first and expanded.

The `/api/sessions/list` API endpoint in the dashboard backend does not provide client workspace information to the frontend, so the grid component has no way to determine which workspace to prioritize.

## Expected Behavior

The dashboard should:
1. Determine the current workspace from the client's working directory
2. Show that workspace's sessions first in the list, with its group expanded
3. Fall back to the "Global" workspace group when no specific workspace directory is identified

## Files to Look At

- `packages/dashboard/src/grid.tsx` — React component that renders the session grid and handles workspace group ordering
- `packages/playwright-core/src/tools/dashboard/dashboardApp.ts` — Backend HTTP handler for the dashboard API, including `/api/sessions/list`
- `packages/playwright-core/src/tools/dashboard/DEPS.list` — Import boundary declarations for the dashboard module
