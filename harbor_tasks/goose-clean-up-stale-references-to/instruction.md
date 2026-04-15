# Clean up stale references to dead code, debug logs, and stale comments

## Problem

The codebase has accumulated technical debt:

1. **Debug console.log statements** in UI files that clutter the console and shouldn't be in production code. Specifically, `ui/desktop/src/App.tsx` contains debug logging statements including:
   - Messages about "reactReady signal" being sent to Electron
   - Messages about "keyboard shortcuts" being set up

2. **Stale TODO comment** in `crates/goose/src/config/experiments.rs` containing the text:
   ```
   TODO: keep this up to date with the experimental-features.md
   ```
   This comment references keeping documentation in sync, but the experiments list is empty, making the TODO obsolete.

3. **Insufficient log level** in `crates/goose/src/config/extensions.rs`. The function `save_extensions_map` logs configuration save failures at the `tracing::debug!` level. Since save failures indicate potential user-facing issues (extensions not persisting), these should be logged at a more visible level like `tracing::warn!`. The expected log message content is "Failed to save extensions config".

4. **Dead code files** that are no longer referenced anywhere in the codebase:
   - `ui/desktop/src/components/InterruptionHandler.tsx` (236 lines)
   - `ui/desktop/src/hooks/useRecipeManager.ts` (324 lines)
   - `ui/desktop/src/components/WaveformVisualizer.tsx` (113 lines)

## Expected Behavior

- Debug `console.log` statements with content matching "reactReady signal" or "keyboard shortcuts" should not appear in production code files
- The stale TODO comment containing "TODO: keep this up to date with the experimental-features.md" should be removed from `experiments.rs`
- Extension configuration save failures in `save_extensions_map` should be logged using `tracing::warn!` with a message containing "Failed to save extensions config", not `tracing::debug!`
- Dead code files that are no longer imported or used anywhere should be removed from the repository

## Files to Look At

- `crates/goose/src/config/extensions.rs` — Extension configuration persistence (contains `save_extensions_map` function)
- `crates/goose/src/config/experiments.rs` — Experiment configuration (contains stale TODO)
- `ui/desktop/src/App.tsx` — Main React application component (contains debug console.log statements)
- `ui/desktop/src/components/` — React components directory
- `ui/desktop/src/hooks/` — React hooks directory
