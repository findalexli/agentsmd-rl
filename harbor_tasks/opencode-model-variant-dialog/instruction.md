# Variant keybind cycles blindly instead of showing a selection dialog

## Problem

In the TUI application, the model variant keybind (`ctrl+t`) cycles through variants sequentially by calling `local.model.variant.cycle()`. This is a poor user experience — the user can't see which variants are available or jump directly to the one they want. They have to cycle through all options one by one.

A `DialogVariant` selection component already exists at `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx` and is fully functional. Other similar actions in the app (model selection, agent selection, MCP toggles) all open a dialog for the user to pick from. The variant action is the only one that uses blind cycling instead.

## Expected behavior

The variant keybind should open the `DialogVariant` selection dialog so users can see all available variants and pick one directly, consistent with how model and agent selection works.

## Relevant files

- `packages/opencode/src/cli/cmd/tui/app.tsx` — command palette entries and keybind handlers
- `packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx` — existing variant selection dialog component (already built, just not wired up)

## Hints

- Look at how the "Switch model" action opens `DialogModel` via `dialog.replace()`
- The variant action entry is in the commands array in `App()`
- The title should reflect that it's a selection action, not a cycle
