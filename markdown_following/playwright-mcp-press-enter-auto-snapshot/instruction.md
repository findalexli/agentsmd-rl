# MCP keyboard press Enter should wait for navigation

## Problem

The Playwright MCP `browser_press_key` tool treats all key presses the same — it calls `page.keyboard.press()` directly and returns immediately. When an agent presses Enter (e.g., to submit a form or trigger navigation), the tool returns before the page has finished loading or updating. The agent then has to manually issue a separate snapshot command to see what happened, which is both wasteful and error-prone since the page may not have settled yet.

Other input tools in the same codebase (like `browser_press_sequentially` and `browser_type` with `submit: true`) already handle this correctly by wrapping the Enter press in `waitForCompletion` and including a snapshot in the response.

## Expected Behavior

When the `browser_press_key` tool is used to press Enter specifically, it should:
1. Wait for any triggered navigation or DOM updates to complete before returning
2. Automatically include a page snapshot in the response

Other keys (arrows, letters, etc.) should continue to press immediately without waiting.

After fixing the code, update the terminal SKILL.md workflow instructions to reflect that a manual snapshot step is no longer necessary — pressing Enter now auto-captures page state.

## Files to Look At

- `packages/playwright/src/mcp/browser/tools/keyboard.ts` — defines the `browser_press_key` tool handler
- `packages/playwright/src/mcp/terminal/SKILL.md` — agent skill instructions describing the core browser automation workflow

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
