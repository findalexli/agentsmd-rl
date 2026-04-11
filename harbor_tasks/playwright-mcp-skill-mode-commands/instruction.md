# Make MCP terminal modal states skill-friendly

## Problem

The Playwright MCP terminal commands use hyphenated names for keyboard and mouse commands (`key-press`, `key-down`, `key-up`, `mouse-move`, `mouse-down`, `mouse-up`, `mouse-wheel`). When the CLI runs in daemon/skill mode, modal state messages (like dialog prompts or file chooser notifications) tell the user to use tool names like `browser_handle_dialog` — but in skill mode, the user should instead see human-friendly skill command names like `dialog-accept` or `upload`.

Additionally, the `eval` command requires users to write full arrow function syntax (`() => document.title`) even for simple expressions.

## Expected Behavior

1. **Rename terminal commands** to remove hyphens: `press`, `keydown`, `keyup`, `mousemove`, `mousedown`, `mouseup`, `mousewheel`. Update both the command declarations and the help text.

2. **Make modal state messages skill-aware**: When running in skill/daemon mode, modal state messages should show the skill-friendly command name (e.g., `dialog-accept or dialog-dismiss`, `upload`) instead of the MCP tool name (e.g., `browser_handle_dialog`, `browser_file_upload`). The `clearedBy` field on modal states needs to carry both the tool name and the skill name.

3. **Auto-wrap eval expressions**: If the user passes an expression to `eval` that doesn't contain `=>`, automatically wrap it in `() => (...)`.

4. **Create a SKILL.md file** for the terminal CLI that documents all available commands with examples. This file should live alongside the terminal command implementation and use the new command names. Don't forget to update the build script so it gets copied to the output directory.

## Files to Look At

- `packages/playwright/src/mcp/terminal/commands.ts` — command declarations with names
- `packages/playwright/src/mcp/terminal/help.json` — CLI help text
- `packages/playwright/src/mcp/browser/tools/tool.ts` — ModalState type definitions
- `packages/playwright/src/mcp/browser/tab.ts` — modal state creation and rendering
- `packages/playwright/src/mcp/browser/response.ts` — response building that renders modal states
- `packages/playwright/src/mcp/browser/config.ts` — FullConfig type
- `packages/playwright/src/mcp/program.ts` — daemon mode setup
- `packages/playwright/src/mcp/browser/tools/evaluate.ts` — eval command handler
- `utils/build/build.js` — build script for copying assets
