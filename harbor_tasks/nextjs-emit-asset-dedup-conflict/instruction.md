# next-core: deduplicate output assets and detect content conflicts on emit

## Problem

When Turbopack emits output assets, duplicate assets targeting the same output path are emitted unconditionally — whichever write happens last silently wins. This masks build graph bugs where two different modules produce conflicting output files for the same path, making it very difficult to diagnose the root cause.

## Expected Behavior

Duplicate output assets for the same path should be detected during emission:

- If multiple assets map to the same path with identical content, one should be silently chosen (deduplication).
- If their content differs, a structured issue should be reported with severity Error, at a new `Emit` stage, so developers can see the conflict without breaking the build. Both conflicting versions should be written to disk so they can be diffed.
- Node-root and client assets should be emitted in parallel with deterministic error reporting (both branches always run to completion).

## Files to Look At

- `crates/next-core/src/emit.rs` — the `emit_assets` function that handles asset emission, and new helper structs/functions for conflict detection
- `turbopack/crates/turbopack-core/src/issue/mod.rs` — the `IssueStage` enum that needs a new variant for the emit phase
