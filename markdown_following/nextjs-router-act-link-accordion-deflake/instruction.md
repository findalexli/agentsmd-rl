# Fix Flaky Segment Cache Staleness Test

## Problem

The test "per-page value overrides global staleTimes.dynamic regardless of direction" in the segment cache staleness test suite is flaky. The flakiness is caused by `browser.back()` triggering BFCache, which restores the full React state including `useState` values. When `LinkAccordion` components were previously toggled open, BFCache restores them in the open state, making `<Link>` components immediately visible outside any `act` scope. This triggers IntersectionObserver-based prefetches that break subsequent `no-requests` assertions when stale data causes unexpected network requests.

## Expected Fix

Replace `browser.back()` calls in the flaky test with forward navigation to fresh intermediate "hub" pages. These intermediate pages should:

- Use `LinkAccordion` (the existing component in the staleness test fixture) for controlled prefetch behavior, so links start hidden behind a toggle
- Be dynamically rendered using `connection()` from `next/server`, so navigation always produces a router request that `act` can manage
- Wrap async content in `<Suspense>` with a fallback
- Export a default page function (standard Next.js page convention)
- Contain `LinkAccordion` links to the target stale-time pages

Create enough intermediate pages (at least 3) so that each `browser.back()` replacement in the test navigates to a unique, previously-unvisited page. Since these pages are fresh, their accordions start in the closed state and no uncontrolled prefetches occur.

The existing dynamic-stale pages also need `LinkAccordion` links back to the intermediate pages, creating bidirectional navigation that lets the test move forward instead of backward.

## Documentation Requirements

This fix introduces a reusable testing pattern that should be documented:

1. **AGENTS.md**: Add a rule documenting that router act tests must use `LinkAccordion` for prefetch control and must avoid `browser.back()` due to BFCache-triggered re-prefetches. Reference the `router-act` skill.

2. **Router-act skill**: Create a new skill under `.agents/skills/router-act/` with:
   - YAML frontmatter with `name: router-act` and a `description` field
   - Documentation of the `LinkAccordion` pattern and why it controls prefetches
   - Hub/intermediate page pattern for avoiding `browser.back()`
   - Common sources of flakiness (`browser.back()` and `BFCache` state restoration)
   - Act API patterns: `'no-requests'` assertions, `includes` matching
   - How `act` internally uses `requestIdleCallback` to capture IntersectionObserver-triggered prefetches

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
