# Rename "Version Packages" to "Release" and add transitive dependency releases

## Problem

The release tooling uses the name "Version Packages" throughout the codebase — in workflow files, script names, PR titles, commit messages, and documentation. This naming is confusing because "versioning" is just one step of the release process. The name should be simplified to "Release".

Additionally, the current release system only publishes packages that have explicit change files. If package A depends on package B and B gets a new release, package A is not automatically released with the updated dependency. This means consumers may not get dependency updates until someone manually creates a change file for the dependent package.

## Expected Behavior

1. **Rename all "Version Packages" references to "Release":**
   - The workflow file `.github/workflows/changes-version-pr.yaml` should be renamed to `release-pr.yaml`
   - The script `scripts/changes-version-pr.ts` should be renamed to `release-pr.ts`
   - The utility `scripts/utils/version-pr.ts` should be renamed to `release-pr.ts`
   - The PR title, branch name, commit message subject, and all string references should use "Release" instead of "Version Packages"
   - All internal imports should be updated to match the new filenames

2. **Add transitive dependency release tracking:**
   - In `scripts/utils/packages.ts`, add utility functions for generating git tags and GitHub release URLs (e.g., `getPackageShortName`, `getGitTag`, `getGitHubReleaseUrl`)
   - Add functions to compute package dependency graphs and find transitive dependents (`getPackageDependencies`, `buildReverseDependencyGraph`, `getTransitiveDependents`)
   - In `scripts/utils/changes.ts`, extend `parseAllChangeFiles()` to automatically include packages that transitively depend on directly-changed packages
   - Add a `DependencyBump` interface and a `dependencyBumps` field to `PackageRelease`
   - Update changelog generation to include a "Bumped `@remix-run/*` dependencies" section when a package is released due to dependency changes

3. **Update documentation** — the project's `AGENTS.md` and `CONTRIBUTING.md` should be updated to reflect the new workflow name, script paths, and "Release" PR terminology.

## Files to Look At

- `.github/workflows/changes-version-pr.yaml` — the GitHub Actions workflow to rename
- `scripts/changes-version-pr.ts` — the main release PR script to rename
- `scripts/utils/version-pr.ts` — the PR body generator to rename
- `scripts/utils/changes.ts` — the change file parser and changelog generator (needs transitive dep logic)
- `scripts/utils/packages.ts` — package utilities (needs new tag/URL/dependency helpers)
- `scripts/publish.ts` — the publish script (has a stale "Version Packages" comment)
- `AGENTS.md` — agent instructions referencing the old workflow/script names
- `CONTRIBUTING.md` — contributor docs referencing the old workflow/PR names
