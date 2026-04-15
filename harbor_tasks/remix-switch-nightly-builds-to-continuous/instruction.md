# Switch nightly builds to continuous preview builds

## Problem

The project currently has a separate CI workflow (`.github/workflows/nightly.yml`) that runs on a daily cron schedule to build the latest `main` into a `nightly` branch. This creates up to a 24-hour delay between merging a PR and the changes becoming installable.

There is also a `preview.yml` workflow that creates installable PR preview branches. These two workflows duplicate setup logic.

The `setup-installable-branch.ts` script has nightly-specific logic: it defaults to the `nightly` branch name and contains a branch-protection allowlist that only permits overwriting the `nightly` branch.

## Required End State

After the changes, the following must be true:

### Workflow

- `.github/workflows/nightly.yml` must not exist
- `.github/workflows/preview.yml` must build and push to a `preview` branch when `main` is pushed
- The preview workflow must still support PR preview branches (`preview/{number}`) and cleanup when PRs close

### Script (`scripts/setup-installable-branch.ts`)

- The script must not accept a `--branch` flag
- The branch name must be a required positional argument (no silent default)
- The string `allowedOverwrites` must not appear in the script
- The script's install example in JSDoc must use the string `remix#preview&path:packages/remix`
- The string `remix#nightly` must not appear in the script

### Documentation

`README.md` must:
- Contain the string `remix#preview&path:packages/remix`
- Not contain the string `remix#nightly`

`CONTRIBUTING.md` must:
- Contain the section heading `## Preview builds`
- Not contain the string `remix#nightly`

## Files to Modify

- `.github/workflows/nightly.yml` — delete this file
- `.github/workflows/preview.yml` — extend to trigger on push to `main` and push builds to `preview`
- `scripts/setup-installable-branch.ts` — simplify: remove `--branch` flag, require positional branch name, remove overwrite protection
- `README.md` — update install instructions to reference preview branch
- `CONTRIBUTING.md` — update build system documentation to reference preview builds