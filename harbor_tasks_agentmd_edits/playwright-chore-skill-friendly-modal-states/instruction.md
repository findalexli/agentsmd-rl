# Make Modal States Skill-Friendly

## Problem

The Playwright MCP terminal CLI uses hyphenated command names (`key-press`, `key-down`, `key-up`, `mouse-move`, `mouse-down`, `mouse-up`, `mouse-wheel`) for keyboard and mouse operations. These names are not ideal for skill-based usage patterns where commands should be compact, single-word identifiers.

Additionally, when a modal state appears (e.g., a dialog or file chooser), the response always says something like `can be handled by the "browser_handle_dialog" tool` — referencing the MCP tool name. In skill/daemon mode, users interact via CLI commands, not MCP tool names, so the message should reference the corresponding skill command name instead.

The `evaluate` command also requires users to wrap all expressions in arrow function syntax (`() => expr`), which is unnecessarily verbose for simple evaluations like `document.title`.

## Expected Behavior

1. **Rename keyboard/mouse commands** to remove hyphens: `key-press` → `press`, `key-down` → `keydown`, `key-up` → `keyup`, `mouse-move` → `mousemove`, `mouse-down` → `mousedown`, `mouse-up` → `mouseup`, `mouse-wheel` → `mousewheel`. Update both the command declarations and the help text.

2. **Make modal state messages skill-aware**: When running in daemon/skill mode, modal state messages should display the skill command name (e.g., `dialog-accept or dialog-dismiss`) instead of the MCP tool name (e.g., `browser_handle_dialog`). The `clearedBy` field on modal states needs to carry both a tool name and a skill name, and `renderModalStates` should pick the right one based on a config flag.

3. **Auto-wrap eval expressions**: If the user passes a plain expression (no `=>`) to the `evaluate` command, automatically wrap it as `() => (expression)`.

4. **Create a SKILL.md** for the terminal CLI module that documents all available commands, their arguments, and usage examples. This file should live alongside the terminal command source and follow the standard skill frontmatter format. Don't forget to ensure the build system copies this file to the output directory.

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — command declarations with name fields
- `packages/playwright/src/mcp/terminal/help.json` — help text for all commands
- `packages/playwright/src/mcp/browser/tab.ts` — `renderModalStates` function and modal state creation
- `packages/playwright/src/mcp/browser/tools/tool.ts` — `ModalState` type definitions
- `packages/playwright/src/mcp/browser/tools/evaluate.ts` — evaluate command handler
- `packages/playwright/src/mcp/browser/config.ts` — `FullConfig` type
- `packages/playwright/src/mcp/browser/response.ts` — calls `renderModalStates`
- `packages/playwright/src/mcp/program.ts` — daemon mode config setup
- `utils/build/build.js` — build copy rules
