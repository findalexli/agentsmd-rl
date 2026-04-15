# Share workspace slug wait helper across e2e specs

## Problem

The E2E test suite has duplicated helper functions across multiple spec files. Three test files (`projects-switch.spec.ts`, `workspace-new-session.spec.ts`, and `workspaces.spec.ts`) each define their own local copies of:

- `slugFromUrl(url)` — extracts the workspace slug from a URL
- `waitSlug(page, skip?)` — polls until the URL slug stabilizes (handles transient slug states)

This duplication makes the helpers hard to maintain and inconsistent. The `waitSlug` implementation varies between files — some versions return the slug at the wrong time (e.g., before it has settled), causing flaky tests on Windows where workspace slugs get canonicalized.

## Expected Behavior

1. Move both `slugFromUrl` and `waitSlug` into `packages/app/e2e/actions.ts` as shared exports
2. Update all three spec files to import these helpers from `../actions` instead of defining them locally
3. Update `packages/app/e2e/AGENTS.md` to document the new shared helpers

### Required Function Signatures

The shared helpers in `actions.ts` must have these exact signatures:

```typescript
export function slugFromUrl(url: string): string
export async function waitSlug(page: Page, skip: string[] = []): Promise<string>
```

### Required slugFromUrl Implementation

The `slugFromUrl` function must use a regex that:
- Matches a `/` followed by a capture group `([^/]+)` (the slug), followed by `/session`
- The session portion must be followed by either `/`, `?`, `#`, or end-of-string: `/session(?:[/?#]|$)`

The regex must contain these components: `/\/` (escaped forward slash), `([^/]+)` (capture group), and `/session(?:[/?#]|$)`.

### Required waitSlug Implementation

The `waitSlug` function must:
- Use `expect.poll` for polling
- Have a timeout of 45,000 milliseconds (written as `45_000` with underscore separator or `45000`)
- Track previous and next slug values to detect when the slug has settled
- Return the resolved slug value (not just any matching slug)

### Required AGENTS.md Documentation

The `packages/app/e2e/AGENTS.md` file must be updated in the "Writing New Tests" section (or equivalent) to:

1. Document the new helper functions with their signatures:
   - `slugFromUrl(url)` — reads workspace slug from URL
   - `waitSlug(page, skip?)` — waits for resolved workspace slug

2. Include guidance on using shared helpers from `../actions` when validating routing

3. Explain that workspace URL slugs can be **canonicalized on Windows**, and that routing assertions should use resolved/canonical workspace slugs

## Files to Modify

- `packages/app/e2e/actions.ts` — add the shared helper functions here
- `packages/app/e2e/projects/projects-switch.spec.ts` — remove local helpers, import from actions (only `waitSlug` needed)
- `packages/app/e2e/projects/workspace-new-session.spec.ts` — remove local helpers, import from actions (both `slugFromUrl` and `waitSlug`)
- `packages/app/e2e/projects/workspaces.spec.ts` — remove local helpers, import from actions (both `slugFromUrl` and `waitSlug`)
- `packages/app/e2e/AGENTS.md` — document the new helpers in the "Writing New Tests" section

## Notes

- The spec files should still work correctly on Windows after refactoring
- Ensure all modified files pass TypeScript type checking, Prettier formatting, and Biome linting