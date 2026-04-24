# Remove unnecessary waitForCompletion from non-navigating MCP tools

## Problem

Several MCP tool handlers in Playwright's browser automation backend unnecessarily wrap their actions in `tab.waitForCompletion()`. This wrapper is designed to wait for navigation or page-level state changes triggered by the action, but it adds unnecessary overhead for actions that never cause navigation.

The affected tools are:
- `browser_type` (fill) — wraps the entire fill+submit action in `waitForCompletion`, but only `--submit` (Enter press) or `--slowly` (sequential typing) can actually trigger navigation. A plain fill never does.
- `browser_hover` — hover never causes navigation
- `browser_select_option` — selecting a dropdown option never causes navigation
- `browser_mouse_move_xy` — moving the mouse never causes navigation

## Expected Behavior

- `browser_type`: Only use `waitForCompletion` when `submit` or `slowly` is set. A plain fill should execute without the completion wrapper.
- `browser_hover`, `browser_select_option`, `browser_mouse_move_xy`: Execute their action directly without `waitForCompletion`.
- Other tools that CAN cause navigation (like `browser_click`, `browser_press_key` for Enter) must continue using `waitForCompletion`.

After fixing the code, update the project's skill documentation to reflect the `--submit` flag behavior for the fill command. The SKILL.md at `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` should be updated so users understand when Enter is pressed after filling.

## Files to Look At

- `packages/playwright-core/src/tools/backend/keyboard.ts` — contains the `browser_type` tool handler
- `packages/playwright-core/src/tools/backend/mouse.ts` — contains the `browser_mouse_move_xy` tool handler
- `packages/playwright-core/src/tools/backend/snapshot.ts` — contains `browser_hover` and `browser_select_option` tool handlers
- `packages/playwright-core/src/tools/cli-client/skill/SKILL.md` — CLI skill documentation

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
