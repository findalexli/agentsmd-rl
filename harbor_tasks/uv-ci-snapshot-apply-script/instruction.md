# Add CI Snapshot Persistence and Local Apply Script

## Problem

When snapshot tests fail in CI (e.g., due to platform-specific rendering differences or expected output changes), developers must manually reproduce the failure locally to update the snapshots. This is especially painful for platform-specific snapshots (macOS, Windows) that can't be reproduced on a Linux dev machine.

There is no mechanism to persist snapshot test failures from CI as downloadable artifacts, and no tooling to apply those pending snapshots locally.

## What Needs to Change

1. **CI workflow** (`.github/workflows/test.yml`): Configure the test jobs to write pending insta snapshots to a separate directory and upload them as artifacts when tests fail.

   The relevant jobs are `cargo-test-linux` and `cargo-test-windows`. In each job's nextest step, set these env vars:
   - `INSTA_UPDATE`: `new`
   - `INSTA_PENDING_DIR`: a path relative to the workspace (e.g., `${{ github.workspace }}/pending-snapshots`)

   Add an upload-artifact step that runs only on `failure()`. The artifact name must contain `pending-snapshots` (e.g., `pending-snapshots-linux`, `pending-snapshots-windows`).

2. **Local apply script**: Create a bash script at `scripts/apply-ci-snapshots.sh` that:
   - Downloads pending snapshot artifacts from a CI run (auto-detecting the PR for the current branch, or accepting a run ID as argument)
   - Merges snapshots from multiple platform artifacts
   - Applies them locally using `cargo-insta`
   - Supports both `accept` and `review` modes
   - Requires `gh`, `cargo-insta`, and `git`
   - Exits non-zero with an error message that mentions both `accept` and `review` when given an invalid action argument

3. **Documentation**: After implementing the above, update the relevant project documentation to inform contributors about this new workflow for updating snapshots from CI failures.

## Files to Look At

- `.github/workflows/test.yml` — CI test workflow with Linux, macOS, and Windows jobs
- `Cargo.toml` — workspace dependency versions (check the `insta` version)
- `scripts/` — existing project scripts
- `CONTRIBUTING.md` — contributor documentation, especially the snapshot testing section