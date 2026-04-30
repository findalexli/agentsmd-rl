# Dashboard screenshot downloads return stale cached images

## Bug

In Apache Superset, when a user downloads a dashboard as PNG or PDF
from the dashboard menu, the export sometimes contains an outdated
version of the dashboard that does not reflect recent data changes.
The download is silently served from the thumbnail cache.

The thumbnail cache exists for *passive* preview tiles, where slight
staleness is fine. **Explicit user-initiated downloads are different:
when the user clicks "Download as Image" or "Download as PDF", the
exported file must reflect the current dashboard state.**

The frontend dashboard hook that triggers the download is in:

```
superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts
```

It calls the backend's `cache_dashboard_screenshot` API. That API
already supports requesting a fresh (uncached) screenshot — the
frontend just isn't asking for one.

## Expected behaviour

When the download flow POSTs to
`/api/v1/dashboard/<id>/cache_dashboard_screenshot/`, the request must
ask the backend for a fresh screenshot. Concretely:

- The URL must include a `force` flag set to `true` in the query
  string. The Superset backend reads its query parameters as a single
  rison-encoded `q=...` blob, so the standard way to set this is to
  encode `{ force: true }` with `rison` and append it as `?q=<encoded>`
  to the endpoint. Both the literal `true` form and the rison short
  form `!t` are acceptable encodings.
- The dashboard id must still be interpolated into the path
  (`/dashboard/<id>/cache_dashboard_screenshot/...`).
- The HTTP call must still go through `SupersetClient.post` from
  `@superset-ui/core`. Don't introduce a raw `fetch` or `axios` call.

## Constraints from repo conventions

The repository's contributor guide (`AGENTS.md`) imposes a few rules
that are relevant here:

- **TypeScript: no `any` types.** Don't add `any` casts on the changed
  lines.
- **Functional components / hooks.** Keep the change inside the
  existing custom hook; preserve the existing `useCallback` /
  `useEffect` / `useRef` structure.
- **`@superset-ui/core` for shared utilities.** Don't reimplement
  HTTP — use `SupersetClient`, which is already imported.
- **Comments must be timeless.** If you add comments, avoid words like
  "now", "currently", or "today" — they age badly.
- **Apache 2.0 license header.** Any source file you modify must keep
  its existing ASF license header.

## How this is evaluated

Tests load the modified hook in a stubbed environment, call the
returned `downloadScreenshot('png')` callback, and inspect the URL
that gets POSTed to `cache_dashboard_screenshot`. They assert:

1. The URL still targets the `cache_dashboard_screenshot` endpoint
   under the right dashboard id.
2. The URL includes a `force` flag set to `true` (`force:true`,
   `force:!t`, `force=true`, or any equivalent URL/rison encoding).
3. The `force` flag is delivered as a rison-encoded `?q=<rison>` query
   parameter (the standard Superset mechanism), not as bare
   `?force=true`-style params.
4. The file retains its Apache 2.0 license header.
