# Add CI Snapshot Persistence and Local Apply Script

## Problem

When snapshot tests fail in CI (e.g., due to platform-specific rendering differences or expected output changes), developers must manually reproduce the failure locally to update the snapshots. This is especially painful for platform-specific snapshots (macOS, Windows) that can't be reproduced on a Linux dev machine.

There is no mechanism to persist snapshot test failures from CI as downloadable artifacts, and no tooling to apply those pending snapshots locally.

## What Needs to Change

### 1. CI Workflow Changes

Modify `.github/workflows/test.yml` so that the `cargo-test-linux` and `cargo-test-windows` jobs capture pending insta snapshots when tests fail.

For the nextest run steps in each of these jobs, the following environment variables must be set:
- `INSTA_UPDATE` set to the value `new`
- `INSTA_PENDING_DIR` set to a directory path where pending snapshots will be written

Each of these jobs must also include a step that uploads the pending snapshots as a build artifact when tests fail:
- Use `actions/upload-artifact`
- The artifact name must contain the string `pending-snapshots`
- The upload step must only execute on `failure()`

Note: All workflow YAML must remain valid and properly formatted (the project enforces `prettier` formatting on workflow files).

### 2. Local Apply Script

Create a new bash script at `scripts/apply-ci-snapshots.sh` that downloads and applies pending insta snapshots from a CI run.

The script must:
- Accept an optional run ID as the first argument, and an optional action (`accept` or `review`) as the second argument
- **Validate required tools**: Check that `gh`, `cargo-insta`, and `git` are available. If any tool is missing, exit with a non-zero status and print an error message that contains `required` or `not found` (case-insensitive)
- **Validate the action argument**: If the action is not `accept` or `review`, exit with a non-zero status and print an error message that mentions both `accept` and `review` as the valid options

The script must pass `shellcheck` analysis at **style** severity (`shellcheck --severity style`). All `.sh` files in the repository are checked at this level.

### 3. Dependency Update

The `insta` crate version in the workspace `Cargo.toml` may need to be updated to support the `INSTA_PENDING_DIR` feature. Check the current version and update if necessary.

## Files to Look At

- `.github/workflows/test.yml` — CI test workflow containing the `cargo-test-linux` and `cargo-test-windows` jobs
- `Cargo.toml` — workspace dependency versions (check the `insta` version)
- `scripts/` — existing project scripts
