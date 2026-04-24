# Clean up stale references to dead code, debug logs, and stale comments

## Problem

The codebase has accumulated technical debt that needs addressing:

1. **Debug console.log statements** in UI files that clutter the console and shouldn't be in production code. `ui/desktop/src/App.tsx` contains debug logging statements with content including:
   - `Sending reactReady signal to Electron`
   - `Setting up keyboard shortcuts`

2. **Stale TODO comment** in `crates/goose/src/config/experiments.rs` containing the text:
   ```
   TODO: keep this up to date with the experimental-features.md
   ```
   This comment references keeping documentation in sync, but the experiments list is empty, making the TODO obsolete.

3. **Insufficient log level** in `crates/goose/src/config/extensions.rs`. The function `save_extensions_map` logs configuration save failures at a level that may not be visible in production monitoring. Since save failures indicate potential user-facing issues (extensions not persisting), these should be logged at a more visible level. The log message content includes `Failed to save extensions config`.

4. **Dead code files** that are no longer referenced anywhere in the codebase:
   - `ui/desktop/src/components/InterruptionHandler.tsx`
   - `ui/desktop/src/hooks/useRecipeManager.ts`
   - `ui/desktop/src/components/WaveformVisualizer.tsx`

## Expected Behavior

- Debug `console.log` statements with content matching `Sending reactReady signal to Electron` or `Setting up keyboard shortcuts` should not appear in production code files
- The stale TODO comment containing `TODO: keep this up to date with the experimental-features.md` should be removed from `experiments.rs`
- Extension configuration save failures in `save_extensions_map` should be logged at a level that will be visible in production monitoring (`tracing::warn!` or higher) with a message containing `Failed to save extensions config`
- Dead code files that are no longer imported or used anywhere should be removed from the repository

## Files to Look At

- `crates/goose/src/config/extensions.rs` — Extension configuration persistence
- `crates/goose/src/config/experiments.rs` — Experiment configuration
- `ui/desktop/src/App.tsx` — Main React application component
- `ui/desktop/src/components/` — React components directory
- `ui/desktop/src/hooks/` — React hooks directory

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo clippy (Rust linter)`
- `cargo fmt (Rust formatter)`
