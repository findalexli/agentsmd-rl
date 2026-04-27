# Safari race condition: dashboard filters not inherited on the chart explore page

You are working in a checkout of [apache/superset](https://github.com/apache/superset)
at `/workspace/superset`. The frontend lives under `superset-frontend/`.

## Symptom

When a user clicks a chart inside a dashboard to open the **chart explore page**,
the explore page is supposed to inherit the dashboard's runtime context: native
filters, color scheme, label colors, data masks, etc. This works reliably in
Chrome and Firefox.

In **Safari**, the inheritance fails *intermittently*. After navigating from the
dashboard to the explore page, none of the dashboard filters are applied to the
chart — the chart re-renders as if it had been opened standalone.

## Root cause

The explore page reads `dashboard_page_id` from the URL query string at mount
time, then uses that ID to look up a context object that the dashboard wrote to
`localStorage` at click-time. The lookup happens via
`new URLSearchParams(window.location.search).get('dashboard_page_id')`.

In Safari, **`window.location.search` is not guaranteed to be synchronously
updated after a `history.push()` navigation**. When the explore page's
`useEffect` runs, `window.location.search` can still reflect the *previous*
dashboard URL. The result:

- `dashboard_page_id` is read as `null` from the stale `window.location.search`.
- The localStorage context lookup is skipped.
- No dashboard filters propagate to the chart.

Chrome and Firefox update `window.location.search` synchronously, so this
race never trips on those browsers.

React Router's `useLocation()` hook, in contrast, returns a `location` object
that is **always in sync with the current render cycle** — its `.search` field
correctly reflects the new explore URL even in Safari, because React Router
manages it independently of the browser's URL bar update timing.

## What to fix

The fix has two parts. Both are required for the bug to actually go away.

### 1. Make `getUrlParam` parameterisable on the search string

`getUrlParam` (in `superset-frontend/src/utils/urlUtils.ts`) currently always
reads from `window.location.search`. It should accept an **optional** second
parameter that, when supplied, is parsed *instead of* `window.location.search`.

- The parameter must be `string`-typed and **optional** so existing callers
  that don't pass it continue to work unchanged.
- All overload signatures of `getUrlParam` must be updated to declare the new
  parameter (otherwise TypeScript rejects the new call shape at compile
  time for some `UrlParamType`s).
- The implementation must consume the new parameter via
  `new URLSearchParams(<override> ?? window.location.search)`.

Concretely, after the fix the following must hold:

- `getUrlParam(URL_PARAMS.dashboardPageId)` (no second argument) reads from
  `window.location.search` exactly as before.
- `getUrlParam(URL_PARAMS.dashboardPageId, '?dashboard_page_id=correct-id')`
  returns `'correct-id'` even if `window.location.search` is empty or stale.
- `getUrlParam(URL_PARAMS.sliceId, '?slice_id=42')` returns the number `42`
  (the existing per-type coercion still applies — the override only changes
  the source of the raw query string, not the type handling).

### 2. Thread the per-render `location.search` through `ExplorePage`

In `superset-frontend/src/pages/Chart/index.tsx` the helper
`getDashboardContextFormData` calls `getUrlParam` internally to look up the
`dashboard_page_id` and `slice_id`. It is invoked from inside `ExplorePage`'s
`useEffect`, which already has access to React Router's `location` object
(typically named `loc` in this file).

Update both ends of that wiring:

- `getDashboardContextFormData` must accept a single `string` parameter and
  forward it to **every** `getUrlParam` call inside the helper. After the
  change the helper must not read `window.location.search` (directly or
  indirectly) anywhere — every URL-param read must go through the
  injected search string.
- The `ExplorePage` call site must invoke
  `getDashboardContextFormData(...)` with an argument derived from React
  Router's location (e.g. `loc.search`). Calling it with no arguments,
  with an empty string, or with a hard-coded constant defeats the fix.

## Constraints

- Do not introduce TypeScript `any` types.
- Do not create new `.js` / `.jsx` files; if you add new modules they must be
  TypeScript.
- Existing callers of `getUrlParam` must keep working without modification,
  i.e. the new parameter must be optional, not required.
- The fix should be the minimum needed to address the race condition; do
  not refactor unrelated code.

## Code Style Requirements

- The repo lints touched frontend files with **oxlint** (`npx oxlint
  --config oxlint.json`). The verifier runs oxlint on the files you touch
  (`src/utils/urlUtils.ts`, `src/pages/Chart/index.tsx`); your patch must
  remain clean.

## Verifying locally

The frontend lives in `superset-frontend/`. From that directory, jest is
already configured:

```bash
cd /workspace/superset/superset-frontend
npx jest src/utils/urlUtils.test.ts --no-coverage --runInBand
npx oxlint --config oxlint.json --quiet src/utils/urlUtils.ts src/pages/Chart/index.tsx
```

The `node_modules/` tree is pre-installed; you do not need to run
`npm ci` again.

## Reference

- Repo agent guide: `AGENTS.md` (linked from `CLAUDE.md`) at the repo root.
