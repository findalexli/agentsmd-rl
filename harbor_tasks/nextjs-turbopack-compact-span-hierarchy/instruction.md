# Bug: Turbopack "compact database" tracing span is misplaced and noisy

## Summary

The `compact()` function in `turbopack/crates/turbo-persistence/src/db.rs` creates its own `"compact database"` tracing span internally. This causes two problems:

1. **Incorrect span hierarchy**: The compact database span inherits the ambient `"persisting background job"` span as its parent (via `.in_current_span()` at task spawn time). This makes it appear nested under `"persisting background job"` in trace viewers, inconsistent with the sibling `"snapshot"` and `"persist"` spans which are already top-level root spans.

2. **Span-per-iteration noise**: The span is created inside the compaction loop, producing one `"compact database"` span per iteration rather than one per compaction session. This clutters traces with many small identical spans.

Additionally, the `"sync new files"` span in the same file (`db.rs`) uses `info_span!` level, which produces unnecessary noise in production traces — it should be at `trace` level.

## Goal

Reorganize the tracing span hierarchy so that:
- The `compact()` call site in `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs` controls the span (not `db.rs`)
- All background snapshot work (persist + compact) is grouped under a shared root span
- The compact span is entered only around the synchronous `compact()` call, not across async `select!` await points (since `EnteredSpan` is `!Send`)
- One compact span per compaction session, not per iteration
- The `"sync new files"` span is downgraded from `info` to `trace`

## Relevant Files

- `turbopack/crates/turbo-persistence/src/db.rs` — contains the misplaced span and the noisy sync span
- `turbopack/crates/turbo-tasks-backend/src/backend/mod.rs` — the call site where `snapshot_and_persist` and the idle compaction loop run
