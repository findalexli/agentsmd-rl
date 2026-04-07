# Switch nightly builds to continuous preview builds

## Problem

The Remix repo currently builds an installable branch (`nightly`) on a cron schedule (once per day). This creates gaps: once a PR is merged, its changes aren't available as an installable build until the next nightly run. Users who want to test the latest `main` have to wait.

The build script at `scripts/setup-installable-branch.ts` also has unnecessary complexity: it accepts a `--branch` flag, defaults to `nightly`, and includes branch overwrite protection that's no longer needed.

Additionally, the separate `nightly.yml` workflow duplicates functionality that could be consolidated into the existing `preview.yml` workflow.

## Expected Behavior

- Every commit to `main` should automatically push an installable build to a `preview` branch (not `nightly`)
- The `preview.yml` workflow should handle three event types: pushes to `main`, pull requests, and manual dispatch
- The `nightly.yml` workflow should be removed entirely
- The `setup-installable-branch.ts` script should be simplified: it should require the branch name as a positional argument (no `--branch` flag, no default value)
- PR preview branches should use the `preview/{number}` naming pattern consistently

## Files to Look At

- `scripts/setup-installable-branch.ts` — the build script that prepares installable branches
- `.github/workflows/nightly.yml` — the cron-based nightly workflow (should be removed)
- `.github/workflows/preview.yml` — the PR preview workflow (should be extended for push events)
- `README.md` — documents how to install bleeding-edge builds (update from nightly to preview)
- `CONTRIBUTING.md` — documents the build process (update Nightly Builds section to Preview builds)

After making the code changes, update the relevant documentation files to reflect the new `preview` branch naming and continuous build behavior.
