# Fix: Skip available-versions request when dbRegion is empty

## Problem

The `useProjectCreationPostgresVersionsQuery` hook in Supabase Studio incorrectly fires an API request when `dbRegion` is an empty string (`""`). The current `enabled` condition uses `typeof dbRegion !== 'undefined'` which passes for empty strings (since `typeof "" === 'string'`), causing the request to fire before a valid region is selected.

This creates a race condition where an invalid `available-versions` request is sent with an empty region parameter.

## Expected Behavior

The query should be **disabled** when:
- `dbRegion` is `undefined`
- `dbRegion` is an empty string `''`
- `dbRegion` is `null` or any other falsy value

The query should only fire when `dbRegion` is a **truthy** non-empty string.

## Files to Look At

- `apps/studio/data/config/project-creation-postgres-versions-query.ts` — React Query hook that fetches available Postgres versions during project creation

## Implementation Notes

The fix involves changing the `enabled` check from `typeof dbRegion !== 'undefined'` to `!!dbRegion`. This handles all falsy cases (undefined, empty string, null) consistently.

The `organizationSlug` checks must be preserved:
- `typeof organizationSlug !== 'undefined'`
- `organizationSlug !== '_'`
