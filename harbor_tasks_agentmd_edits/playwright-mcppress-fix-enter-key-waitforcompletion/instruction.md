# Fix MCP keyboard press handler for Enter key

## Problem

The `browser_press_key` MCP tool in Playwright's MCP server treats all key presses identically. When pressing Enter — which often triggers form submissions, navigation, or significant DOM changes — the tool fires the key press and returns immediately without waiting for the page to settle or including a snapshot of the resulting state.

This is inconsistent with how `browser_type` and `browser_press_sequentially` already handle Enter (they both use `waitForCompletion` and include a snapshot when Enter/submit is involved).

## Expected Behavior

When the Enter key is pressed via `browser_press_key`, the handler should:
1. Wait for any navigation or DOM changes to complete before returning
2. Include a page snapshot in the response so the caller can see the result

Other keys (arrows, letters, etc.) should continue to work as before.

After fixing the code, update the relevant MCP terminal skill documentation to reflect that snapshots are now more automatic — the core workflow instructions should be simplified accordingly.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/keyboard.ts` — the press tool handler
- `packages/playwright/src/mcp/terminal/SKILL.md` — MCP terminal skill documentation with core workflow steps
