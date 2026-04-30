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

After fixing the code, update the project's CLI skill documentation to reflect the `--submit` flag behavior for the fill command, so users understand when Enter is pressed after filling.

## Where to Look

Search the repository for the tool handler definitions by their schema names:

- `browser_type` (fill) — the tool that types into or fills an element, defined with `name: 'browser_type'`
- `browser_hover` — the tool that hovers over an element, defined with `name: 'browser_hover'`
- `browser_select_option` — the tool that selects a dropdown option, defined with `name: 'browser_select_option'`
- `browser_mouse_move_xy` — the tool that moves the mouse to coordinates, defined with `name: 'browser_mouse_move_xy'`

The CLI skill documentation (where the `--submit` flag must be documented) lives under the `packages/playwright-core/src/tools/cli-client/skill/` directory.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
