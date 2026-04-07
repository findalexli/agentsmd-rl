# Support Publishing Prerelease `remix` Package

## Problem

The monorepo uses `pnpm publish --recursive` to publish all packages to npm. However, the `remix` package needs to publish prerelease versions (e.g., `3.0.0-alpha.0`) with a custom dist-tag (e.g., `alpha`) while all other packages continue to publish as `latest`. The current publish script has no concept of prerelease mode and cannot handle mixed dist-tags.

Additionally, the change/version scripts (`changes-preview.ts`, `changes-validate.ts`, `changes-version.ts`, `changes-version-pr.ts`) use separate `validateAllChanges()` and `getAllReleases()` functions that don't account for prerelease versioning. The version bumping logic in `scripts/utils/semver.ts` only handles standard semver increments.

## Expected Behavior

1. **Prerelease config**: The `remix` package should support an optional `.changes/prerelease.json` file (e.g., `{"tag": "alpha"}`) that puts it into prerelease mode. Only the `remix` package should support this.

2. **Unified change file parsing**: The separate `validateAllChanges()` and `getAllReleases()` functions should be consolidated into a single `parseAllChangeFiles()` that handles validation, release computation, and prerelease version logic together. The old `getNextVersion` in `scripts/utils/semver.ts` should be replaced with prerelease-aware logic in `scripts/utils/changes.ts`.

3. **Two-phase publishing**: When remix is in prerelease mode, `scripts/publish.ts` should publish in two phases — first all other packages as `latest`, then remix with its prerelease tag. A `--dry-run` flag should show what would be published without actually publishing.

4. **Version bumping in prerelease mode**: Normal change files should bump the prerelease counter (e.g., `3.0.0-alpha.1` → `3.0.0-alpha.2`). Changing the tag in `prerelease.json` should reset the counter. Deleting `prerelease.json` should graduate to stable.

5. **All callers updated**: The change/version scripts that called the old API must be updated to use the new unified function.

After making the code changes, update the relevant documentation (AGENTS.md, CONTRIBUTING.md) to describe the new prerelease workflow so that contributors and agents understand how to use it.

## Files to Look At

- `scripts/publish.ts` — publish workflow, needs two-phase logic and `--dry-run`
- `scripts/utils/changes.ts` — core change file parsing and version logic
- `scripts/utils/semver.ts` — old version bumping (should be replaced)
- `scripts/changes-preview.ts` — preview script, uses old API
- `scripts/changes-validate.ts` — validation script, uses old API
- `scripts/changes-version.ts` — version script, uses old API
- `scripts/changes-version-pr.ts` — version PR script, uses old API
- `packages/remix/.changes/` — where prerelease.json goes
- `AGENTS.md` — agent instructions for changes and releases
- `CONTRIBUTING.md` — contributor guide for changes and releases
