# Make Modal States Skill-Friendly

## Problem

The Playwright MCP terminal CLI uses hyphenated command names (`key-press`, `key-down`, `key-up`, `mouse-move`, `mouse-down`, `mouse-up`, `mouse-wheel`) for keyboard and mouse operations. These names are not ideal for skill-based usage patterns where commands should be compact, single-word identifiers.

Additionally, when a modal state appears (e.g., a dialog or file chooser), the response always says something like `can be handled by the "browser_handle_dialog" tool` — referencing the MCP tool name. In skill/daemon mode, users interact via CLI commands, not MCP tool names, so the message should reference the corresponding skill command name instead.

The `evaluate` command also requires users to wrap all expressions in arrow function syntax (`() => expr`), which is unnecessarily verbose for simple evaluations like `document.title`.

## Expected Behavior

1. **Rename keyboard/mouse commands** to remove hyphens: `key-press` → `press`, `key-down` → `keydown`, `key-up` → `keyup`, `mouse-move` → `mousemove`, `mouse-down` → `mousedown`, `mouse-up` → `mouseup`, `mouse-wheel` → `mousewheel`. Update both the command declarations and the help text (both the global help string and the per-command entries in `help.json`). The global help text should show usage like `press <key>`, `keydown <key>`, `keyup <key>`, `mousemove <x> <y>`, `mousedown [button]`, `mouseup [button]`, `mousewheel <dx> <dy>`, and must not contain any of the old hyphenated names.

2. **Make modal state messages skill-aware**: When running in daemon/skill mode, modal state messages should display the skill command name (e.g., `dialog-accept or dialog-dismiss`) instead of the MCP tool name (e.g., `browser_handle_dialog`). Specifically:
   - The `clearedBy` field on modal state types (`FileUploadModalState`, `DialogModalState`) must be changed from a plain `string` to an object typed as `{ tool: string; skill: string }`.
   - When creating modal states, set `clearedBy` to an object with a `tool` property holding the MCP tool name and a `skill` property holding the skill command name.
   - The `renderModalStates` function must accept a `config` parameter (of type `FullConfig`) so it can check a boolean config flag named `skillMode` to decide whether to display `clearedBy.tool` or `clearedBy.skill`.
   - The `FullConfig` type needs a new optional boolean field called `skillMode`.
   - When daemon mode is enabled in `program.ts`, set `config.skillMode` to `true`.

3. **Auto-wrap eval expressions**: If the user passes a plain expression (i.e., the expression string does not include `=>`) to the `evaluate` command, automatically wrap it as `() => (expression)`.

4. **Create a SKILL.md** for the terminal CLI module that documents all available commands, their arguments, and usage examples. This file should live at `packages/playwright/src/mcp/terminal/SKILL.md` and follow the standard skill frontmatter format (YAML between `---` delimiters) with a `name:` field set to `playwright-cli` and a `description:` field. The file must document the `press`, `mousemove`, and `keydown` commands, and contain multiple code example blocks (at least four triple-backtick fenced code blocks). Ensure the build system has a copy rule for `terminal/*.md` files so SKILL.md gets copied to the lib output directory.

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — command declarations with name fields
- `packages/playwright/src/mcp/terminal/help.json` — help text for all commands
- `packages/playwright/src/mcp/browser/tab.ts` — `renderModalStates` function and modal state creation
- `packages/playwright/src/mcp/browser/tools/tool.ts` — `ModalState` type definitions (`FileUploadModalState`, `DialogModalState`)
- `packages/playwright/src/mcp/browser/tools/evaluate.ts` — evaluate command handler
- `packages/playwright/src/mcp/browser/config.ts` — `FullConfig` type
- `packages/playwright/src/mcp/browser/response.ts` — calls `renderModalStates`
- `packages/playwright/src/mcp/program.ts` — daemon mode config setup
- `utils/build/build.js` — build copy rules

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
