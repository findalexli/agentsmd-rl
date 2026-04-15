# Fix Flaky Segment Cache Staleness Test

## Problem

The test "per-page value overrides global staleTimes.dynamic regardless of direction" is flaky due to BFCache behavior. When `browser.back()` is used to return to a previously-visited page, BFCache restores the full page state including React `useState` values. This causes `LinkAccordion` components that were previously toggled open to be immediately visible without any `act` scope. As a result, `<Link>` components trigger IntersectionObserver-based prefetches outside controlled test scopes, which breaks `no-requests` assertions when stale data triggers unexpected network requests.

## Required Behaviors

The implementation must satisfy these verified behaviors:

1. **Hub pages with specific names and structure**: Create three pages with **exact paths** `/per-page-config/hub-a`, `/per-page-config/hub-b`, and `/per-page-config/hub-c`. Each hub page must:
   - Import and use `LinkAccordion` from the existing component at `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx`
   - Call `await connection()` in an async component (ensures dynamic rendering)
   - Use `<Suspense>` with a fallback for async content
   - Export a default `Page` function
   - Contain `LinkAccordion` links to `/per-page-config/dynamic-stale-10` and `/per-page-config/dynamic-stale-60`

2. **Stale page connectivity**: The pages at `/per-page-config/dynamic-stale-10` and `/per-page-config/dynamic-stale-60` must include `LinkAccordion` links to hub pages (`hub-a`, `hub-b`, `hub-c`).

3. **Test navigation assertions**: The test file `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` must:
   - Navigate to `/per-page-config/hub-a`, `/per-page-config/hub-b`, and `/per-page-config/hub-c` (instead of using `await browser.back()`)
   - Use `act` scopes with `includes` assertions matching hub content (e.g., `'Hub a'`)
   - Not contain `await browser.back()` calls in the "per-page value overrides global" test

4. **AGENTS.md documentation**: The file `AGENTS.md` at the repository root must document:
   - `LinkAccordion` for prefetch control
   - The `browser.back()` / `BFCache` flakiness issue
   - Reference to the `$router-act` skill

5. **Skill documentation**: Create `.agents/skills/router-act/SKILL.md` containing:
   - Frontmatter with `name: router-act` and a `description` field
   - Documentation of `LinkAccordion` pattern
   - The string `'no-requests'` for assertion patterns
   - The term `hub` for hub page pattern documentation
   - Explanation of `includes` matching and `requestIdleCallback` interception
   - Warnings about `browser.back()` flakiness and `BFCache` state restoration

## Verification Context

- **Test file**: `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts`
- **LinkAccordion component**: `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx`
- **Test fixture directory**: `test/e2e/app-dir/segment-cache/staleness/app/per-page-config/`

The test must deterministically pass every time after the fix is applied.
