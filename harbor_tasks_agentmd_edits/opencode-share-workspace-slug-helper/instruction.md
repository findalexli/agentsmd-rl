# Share workspace slug wait helper across e2e specs

## Problem

The E2E test suite has duplicated helper functions across multiple spec files. Three test files (`projects-switch.spec.ts`, `workspace-new-session.spec.ts`, and `workspaces.spec.ts`) each define their own local copies of:

- `slugFromUrl(url)` — extracts the workspace slug from a URL
- `waitSlug(page, skip?)` — polls until the URL slug stabilizes (handles transient slug states)

This duplication makes the helpers hard to maintain and inconsistent. The `waitSlug` implementation varies slightly between files — some versions have a bug where they return the slug at the wrong time, causing flaky tests on Windows where workspace slugs get canonicalized.

## Expected Behavior

1. Move both `slugFromUrl` and `waitSlug` into `packages/app/e2e/actions.ts` as shared exports
2. Update all three spec files to import these helpers from `../actions` instead of defining them locally
3. Update `packages/app/e2e/AGENTS.md` to document the new shared helpers
4. The spec files should use the canonicalized/resolved workspace slug when asserting on session routes (important for Windows compatibility)

## Files to Look At

- `packages/app/e2e/actions.ts` — add the shared helper functions here
- `packages/app/e2e/projects/projects-switch.spec.ts` — remove local helpers, import from actions
- `packages/app/e2e/projects/workspace-new-session.spec.ts` — remove local helpers, import from actions
- `packages/app/e2e/projects/workspaces.spec.ts` — remove local helpers, import from actions
- `packages/app/e2e/AGENTS.md` — document the new helpers in the "Writing New Tests" section

## Notes

- The `waitSlug` helper should wait for the slug to settle (same value for 2 consecutive polls) before returning
- The correct implementation tracks both `prev` and `next` to avoid returning the slug immediately on first match
- After fixing the code, update the relevant documentation to reflect the new shared helpers and the guidance about Windows slug canonicalization
