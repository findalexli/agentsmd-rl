# Fix Flaky Segment Cache Staleness Test

## Problem

The test "per-page value overrides global staleTimes.dynamic regardless of direction" in `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` is flaky. It intermittently fails because `browser.back()` restores BFCache state, causing previously-opened accordion links to be immediately visible. This triggers uncontrolled re-prefetches via IntersectionObserver outside of `act` scopes, which break subsequent `no-requests` assertions when stale data triggers unexpected network requests.

## Expected Behavior

The test should deterministically pass every time. Instead of navigating back to previously-visited pages (where accordion state is restored from BFCache), the test should navigate forward to fresh "hub" pages that have their own `LinkAccordion` components starting in a closed state. This ensures all prefetches are controlled within `act` scopes.

## Files to Look At

- `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` — the flaky test that uses `browser.back()`
- `test/e2e/app-dir/segment-cache/staleness/app/per-page-config/` — test fixture pages; new hub pages need to be created here
- `test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx` — needs LinkAccordion links to hub pages
- `test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx` — needs LinkAccordion links to hub pages
- `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx` — the LinkAccordion component used to control prefetch timing

## Additional Requirements

After fixing the test, update the agent instruction files to document this pattern:

- Add a rule to `AGENTS.md` about using LinkAccordion to control prefetches in router act tests, warning about browser.back()/BFCache issues
- Create a new skill file at `.agents/skills/router-act/SKILL.md` documenting the full router act testing pattern, including the LinkAccordion approach, hub page pattern, no-requests assertions, and common sources of flakiness
