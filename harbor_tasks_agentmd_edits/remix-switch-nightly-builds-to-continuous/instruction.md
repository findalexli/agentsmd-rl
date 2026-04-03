# Switch nightly builds to continuous preview builds

## Problem

The project currently has a separate CI workflow (`.github/workflows/nightly.yml`) that runs on a daily cron schedule to build the latest `main` into a `nightly` branch. This means that after merging a PR, there's a gap until the next nightly run before the merged work is installable — you have to wait up to 24 hours.

Meanwhile, there's already a `preview.yml` workflow that creates installable PR preview branches. These two workflows duplicate a lot of setup logic (checkout, pnpm, node, build).

The `setup-installable-branch.ts` script also has logic specific to the nightly flow — it defaults to the `nightly` branch name and has a hardcoded allowlist (`allowedOverwrites = ['nightly']`) that prevents overwriting any other remote branch.

## Expected Behavior

The nightly workflow should be replaced by extending the existing `preview.yml` workflow to also trigger on every push to `main`, building to a `preview` branch instead of `nightly`. This eliminates the delay between merging and availability.

The build script (`scripts/setup-installable-branch.ts`) should be simplified: remove the `--branch` flag and nightly default, require the branch name as a positional argument, and remove the overwrite protection logic (since the workflow now controls which branches get force-pushed).

After making the code changes, update the documentation in `README.md` and `CONTRIBUTING.md` to reflect the new branch name and workflow — references to "nightly" builds and the `nightly` branch should be updated to reference "preview" builds and the `preview` branch.

## Files to Look At

- `.github/workflows/nightly.yml` — the old nightly cron workflow
- `.github/workflows/preview.yml` — the PR preview workflow to extend
- `scripts/setup-installable-branch.ts` — the build script invoked by both workflows
- `README.md` — contains install instructions referencing the build branch
- `CONTRIBUTING.md` — documents the build system and install commands
