# Home footer is hardcoded instead of using the plugin slot system

## Problem

The home screen footer in `packages/opencode/src/cli/cmd/tui/routes/home.tsx` renders the directory path, MCP server status, and version number directly inline. Every other UI section on the home screen (logo, prompt area, bottom tips) and in the sidebar (context, MCP, files, footer) is rendered through the TUI plugin slot system via `TuiPluginRuntime.Slot`, but the home footer is a special case that bypasses this architecture.

This means:
- External and internal plugins cannot override or extend the home footer
- The MCP status display logic is duplicated — the prompt area has its own `Hint` component showing MCP info, and the footer renders a separate MCP status section, leading to redundant information on screen
- The `home.tsx` route file is bloated with presentation logic (directory display, MCP counting, version rendering) that should live in a dedicated plugin

## Expected behavior

The home footer should be extracted into an internal feature plugin under `packages/opencode/src/cli/cmd/tui/feature-plugins/home/`, following the same pattern as `home/tips.tsx` and `sidebar/footer.tsx`. The `TuiSlotMap` type in `packages/plugin/src/tui.ts` needs a new slot entry, and `home.tsx` should render it via `TuiPluginRuntime.Slot` instead of inline JSX.

The redundant MCP hint in the prompt area should also be removed since the footer plugin will display that information.

## Relevant files

- `packages/opencode/src/cli/cmd/tui/routes/home.tsx` — the home route with inline footer
- `packages/plugin/src/tui.ts` — `TuiSlotMap` type definition for available slots
- `packages/opencode/src/cli/cmd/tui/plugin/internal.ts` — registry of internal TUI plugins
- `packages/opencode/src/cli/cmd/tui/feature-plugins/home/tips.tsx` — example of an existing home plugin (pattern to follow)
- `packages/opencode/src/cli/cmd/tui/feature-plugins/sidebar/footer.tsx` — example of a footer plugin
