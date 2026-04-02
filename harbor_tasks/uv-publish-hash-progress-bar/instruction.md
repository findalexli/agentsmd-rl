# Bug: `uv publish` appears frozen during file hashing

## Context

When running `uv publish`, there is a phase before uploading where the tool computes cryptographic hashes of the distribution files. During this phase, the terminal shows no output — it appears to freeze for several seconds (or longer for large files) with no indication that anything is happening. The "Uploading" message appears before hashing even starts, which is misleading since the tool is actually computing hashes, not uploading.

## Problem

The `hash_file` function in `crates/uv-publish/src/lib.rs` computes hashes without any progress feedback. The `Reporter` trait in the same file has methods for tracking upload progress (`on_upload_start`, `on_upload_progress`, `on_upload_complete`) but has no equivalent for the hashing phase.

Additionally, the publish command in `crates/uv/src/commands/publish.rs` prints "Uploading" before the hashing step, so the user sees "Uploading ..." and then waits with no feedback while hashing happens silently.

The `ProgressReporter` in `crates/uv/src/commands/reporters.rs` has a `Direction` enum with `Upload`, `Download`, and `Extract` variants that drive progress display, but nothing for hashing.

## Expected behavior

- A "Hashing" progress indicator should appear during hash computation
- The "Uploading" message should appear only when the actual upload begins (after hashing)
- Progress should be tracked through the existing reporter infrastructure

## Relevant files

- `crates/uv-publish/src/lib.rs` — `Reporter` trait, `hash_file()`, `FormMetadata::read_from_file()`, `check_url()`
- `crates/uv/src/commands/publish.rs` — publish command orchestration
- `crates/uv/src/commands/reporters.rs` — `PublishReporter`, `ProgressReporter`, `Direction` enum
