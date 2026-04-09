# Deflake per-page dynamic stale time test

## Problem

The test "per-page value overrides global staleTimes.dynamic regardless of direction" in `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` is flaky.

The flakiness occurs because `browser.back()` restores accordion state from BFCache, causing previously-opened `LinkAccordion` links to be immediately visible. This triggers uncontrolled re-prefetches outside the `act` scope. When the `IntersectionObserver` fires inside a subsequent `act` scope (after clock advancement), stale data can trigger a prefetch that violates the `no-requests` assertion.

## Expected Behavior

The test should use a deterministic pattern: instead of navigating back to previously visited pages (which have open accordions from BFCache state restoration), navigate forward to fresh "hub" pages with their own `LinkAccordion` components. Since these are never-visited pages, accordions start closed and no uncontrolled prefetches are triggered.

## Files to Modify

1. **`test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx`** — Add `LinkAccordion` components linking to hub pages
2. **`test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx`** — Add `LinkAccordion` components linking to hub pages
3. **`test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx`** — Create new hub page (fresh page with closed accordions)
4. **`test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx`** — Create new hub page
5. **`test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx`** — Create new hub page
6. **`test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts`** — Rewrite test to use hub navigation instead of `browser.back()`
7. **`.agents/skills/router-act/SKILL.md`** — Create new skill documenting router act testing patterns
8. **`AGENTS.md`** — Add router act rule about using LinkAccordion to control prefetches

## Key Principles

When using the router `act` test utility:
- **Always use `LinkAccordion`** to control when prefetches happen
- **Never use `browser.back()`** to return to a page where accordion links are already visible — BFCache restores state and triggers uncontrolled re-prefetches
- Navigate forward to fresh hub pages instead

Reference the `LinkAccordion` component in `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx` for the component API.
