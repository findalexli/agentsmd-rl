# Share workspace slug wait helper across e2e specs

## Problem

The E2E test suite has duplicated helper functions across multiple spec files. Three test files (`projects-switch.spec.ts`, `workspace-new-session.spec.ts`, and `workspaces.spec.ts`) each define their own local copies of `slugFromUrl` and `waitSlug`. These local copies cause flaky tests on Windows where workspace slugs get canonicalized.

## Expected Behavior

1. Export `slugFromUrl` and `waitSlug` from `packages/app/e2e/actions.ts` as shared helpers
2. Update the three spec files to import these helpers from `../actions` instead of defining them locally
3. Update `packages/app/e2e/AGENTS.md` to document the new shared helpers

### Required Exports from actions.ts

The `actions.ts` file must export:
- A `slugFromUrl` function that extracts the workspace slug from a URL
- A `waitSlug` async function that polls until the URL slug stabilizes

### Spec File Updates

- `packages/app/e2e/projects/projects-switch.spec.ts` — remove local helpers, import `waitSlug` from `../actions`
- `packages/app/e2e/projects/workspace-new-session.spec.ts` — remove local helpers, import both helpers from `../actions`
- `packages/app/e2e/projects/workspaces.spec.ts` — remove local helpers, import both helpers from `../actions`

### AGENTS.md Updates

The `packages/app/e2e/AGENTS.md` file must be updated in the "Writing New Tests" section to:
1. Document the new `slugFromUrl(url)` and `waitSlug(page, skip?)` helper functions
2. Recommend using shared helpers from `../actions` when validating routing
3. Note that workspace URL slugs can be canonicalized on Windows

### Verification

All modified files must pass TypeScript type checking, Prettier formatting, and Biome linting.