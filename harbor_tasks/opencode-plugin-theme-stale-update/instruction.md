# TUI plugin themes become stale after plugin updates

## Context

OpenCode's TUI plugin system allows plugins to install custom themes via `api.theme.install(path)`. The theme installer in `packages/opencode/src/cli/cmd/tui/plugin/runtime.ts` handles copying theme JSON files to the user's theme directory and registering them.

The plugin metadata system (`packages/opencode/src/plugin/meta.ts`) already tracks whether a plugin's state is `"first"`, `"updated"`, or `"same"` based on fingerprint comparison across loads. This state is available during plugin activation.

## Problem

When a plugin ships an updated theme (e.g., new colors or styling), users never see the changes. The theme installer unconditionally skips installation when a theme with the same name already exists — there is no path for updating previously installed themes.

Specifically:

1. **No theme refresh on update**: The theme installer returns early if `hasTheme(name)` is true, regardless of whether the plugin itself has been updated. Even when `meta.state === "updated"`, the old theme persists.

2. **No theme tracking**: There is no record of which theme files were installed by which plugin, or what their source file stats (mtime, size) were at install time. Without this tracking, the system cannot detect when a source theme file has actually changed.

3. **No upsert capability**: The theme registration API only has `addTheme` (skip if exists). There is no way to replace an already-registered theme with updated content.

4. **Synchronous stat in async context**: The `modifiedAt` helper in `meta.ts` uses synchronous `statSync`, which blocks the event loop. This should be async, and a corresponding `statAsync` utility is missing from `packages/opencode/src/util/filesystem.ts`.

## Files to investigate

- `packages/opencode/src/cli/cmd/tui/plugin/runtime.ts` — theme installer logic (`createThemeInstaller`)
- `packages/opencode/src/cli/cmd/tui/context/theme.tsx` — theme registration (add vs upsert)
- `packages/opencode/src/plugin/meta.ts` — plugin metadata (state tracking, fingerprint)
- `packages/opencode/src/util/filesystem.ts` — filesystem utilities (stat)

## Guidance

- Refer to `packages/opencode/AGENTS.md` for the project's conventions.
- The theme installer should only update themes from plugins whose metadata state is `"updated"`, and only when the source file has actually changed (mtime/size comparison).
- Theme tracking data should be persisted alongside plugin metadata so it survives across process restarts.
- The spec at `packages/opencode/specs/tui-plugins.md` documents the expected theme install behavior.
