# Fix flaky per-page dynamic stale time test

## Problem

The test "per-page value overrides global staleTimes.dynamic regardless of direction" in `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` is flaky. It intermittently fails with assertion errors about unexpected prefetch requests when it should be asserting `'no-requests'`.

The flakiness occurs because the test uses `browser.back()` to return to previously visited pages. When the browser restores the page from BFCache, React state — including open `LinkAccordion` components — is preserved. This means `<Link>` components are immediately visible, triggering `IntersectionObserver` callbacks and uncontrolled re-prefetches outside any `act` scope.

## Expected Behavior

The test should pass consistently by avoiding BFCache-related state restoration. Instead of navigating back to previously visited pages (where accordions may already be open), the test should navigate forward to fresh intermediate pages that have their own `LinkAccordion` components starting in the closed state.

The dynamic stale time pages (`dynamic-stale-10` and `dynamic-stale-60`) need `LinkAccordion` links to the new intermediate pages, and the intermediate pages need `LinkAccordion` links back to the target pages.

After fixing the test, update the project's agent instructions to document this pattern so future contributors avoid the same pitfall. The `AGENTS.md` file should include a rule about using `LinkAccordion` for prefetch control in act tests and avoiding `browser.back()`. Additionally, create a skill document under `.agents/skills/` that thoroughly covers the `createRouterAct` testing utility, the `LinkAccordion` pattern, hub page navigation, fake clock setup, and common sources of flakiness.

## Files to Look At

- `test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts` — the flaky test
- `test/e2e/app-dir/segment-cache/staleness/app/per-page-config/` — test fixture pages
- `test/e2e/app-dir/segment-cache/staleness/components/link-accordion.tsx` — the LinkAccordion component
- `test/lib/router-act.ts` — the `createRouterAct` utility
- `AGENTS.md` — project agent instructions (needs new rule)
- `.agents/skills/` — skill documents directory (needs new router-act skill)
