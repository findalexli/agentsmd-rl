# Clean up stale references to dead code, debug logs, and stale comments

## Problem

The codebase has accumulated technical debt:

1. **Debug console.log statements** in UI files that clutter the console and shouldn't be in production code:
   - `ui/desktop/src/App.tsx` has multiple `console.log` calls for "reactReady signal" and "keyboard shortcuts"
   - Other UI components have similar debug logging

2. **Stale TODO comment** in `crates/goose/src/config/experiments.rs` that references keeping documentation in sync, but the experiments list is empty

3. **Debug log level** in `crates/goose/src/config/extensions.rs` - extension config save failures are logged at `debug` level instead of `warn`

4. **Dead code files** that are no longer referenced anywhere (~1,186 lines):
   - `ui/desktop/src/components/InterruptionHandler.tsx` (236 lines)
   - `ui/desktop/src/hooks/useRecipeManager.ts` (324 lines)
   - `ui/desktop/src/components/WaveformVisualizer.tsx` (113 lines)
   - `ui/desktop/src/components/schedule/ScheduleFromRecipeModal.tsx` (138 lines)
   - `ui/desktop/src/utils/sessionCache.ts` (130 lines)
   - `ui/desktop/src/components/recipes/RecipeExpandableInfo.tsx` (98 lines)
   - `ui/desktop/src/components/recipes/RecipeInfoModal.tsx` (66 lines)
   - `ui/desktop/src/components/ui/CustomRadio.tsx` (81 lines)

## Expected Behavior

- All debug `console.log` statements removed from production code
- `tracing::debug!` changed to `tracing::warn!` for extension config save failures
- Stale TODO comment removed from experiments.rs
- All 8 dead code files removed

## Files to Look At

- `crates/goose/src/config/extensions.rs` — Extension configuration persistence
- `crates/goose/src/config/experiments.rs` — Experiment configuration
- `ui/desktop/src/App.tsx` — Main React application component
- `ui/desktop/src/components/` — React components directory
- `ui/desktop/src/hooks/` — React hooks directory
