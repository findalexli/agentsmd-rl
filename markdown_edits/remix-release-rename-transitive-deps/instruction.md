# Rename "Version Packages" to "Release" and add transitive dependency releases

## Problem

The release tooling in this monorepo uses the name "Version Packages" for the automated PR that bumps package versions before publishing. This naming is confusing — the PR's purpose is to prepare a **release**, not just version packages. The wording appears in:

- The script `scripts/changes-version-pr.ts` and its utility `scripts/utils/version-pr.ts`
- The GitHub Actions workflow `.github/workflows/changes-version-pr.yaml`
- String literals like the PR title (`prTitle`), branch name, and commit message subject
- The `scripts/publish.ts` comment referencing the PR

Additionally, when a package's dependencies are updated in a release, the package itself should also be released with a patch bump that lists its bumped dependencies in the changelog. Currently, only packages with explicit change files get released — transitive dependents are missed.

## Expected Behavior

1. **Rename**: All references to "Version Packages" and "changes-version-pr" should be updated to use "Release" and "release-pr" respectively. This includes file names, workflow names, branch names, PR titles, and commit message subjects.

2. **Transitive dependency releases**: When packages are released, any other monorepo packages that depend on them should also be released (patch bump) with their dependency bumps listed in the changelog. This requires:
   - A way to discover which packages depend on which (reverse dependency graph)
   - Logic to propagate releases transitively
   - A `DependencyBump` type to track which dependencies triggered a release
   - Changelog generation that includes dependency bump sections

3. **Documentation**: After making the code changes, update the project's agent instructions (`AGENTS.md`) and contributor guide (`CONTRIBUTING.md`) to reflect the new naming. References to the old workflow name, script paths, and PR title should all be updated.

## Files to Look At

- `scripts/changes-version-pr.ts` — main release PR script (needs renaming + content updates)
- `scripts/utils/version-pr.ts` — PR body generation utility (needs renaming)
- `scripts/utils/changes.ts` — change file parsing and release logic (needs transitive dep support)
- `scripts/utils/packages.ts` — package utilities (needs dependency graph functions)
- `scripts/publish.ts` — publish script (has a comment referencing old name)
- `.github/workflows/changes-version-pr.yaml` — CI workflow (needs renaming)
- `AGENTS.md` — agent instructions referencing the release workflow
- `CONTRIBUTING.md` — contributor guide documenting the release process
