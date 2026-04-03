# Fix preview branch naming conflict

## Problem

The CI workflow that creates installable preview builds pushes to a branch called `preview`. However, PR-specific preview branches use the format `preview/{number}` (e.g., `preview/12345`). Git treats `preview` as both a branch name and a directory prefix, causing a "directory file conflict" error when pushing:

```
! [remote rejected] preview -> preview (directory file conflict)
```

This means the main preview build (from `main` branch commits) can never be pushed.

## Expected Behavior

The main preview branch should use a name that doesn't conflict with the PR preview branch namespace. The branch name should be updated everywhere it's referenced — in the CI workflow, in the build script, and in all documentation that tells users how to install from the preview branch.

## Files to Look At

- `.github/workflows/preview.yml` — the CI workflow that builds and pushes preview branches
- `scripts/setup-installable-branch.ts` — the build script invoked by the workflow
- `README.md` — contains install instructions referencing the preview branch
- `CONTRIBUTING.md` — documents the preview build system and install commands

After fixing the workflow and script, update the documentation files so install instructions match the new branch name.
