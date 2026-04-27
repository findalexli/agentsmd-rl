# Prevent unbounded handle growth on repeated 409s

You are working on the **`@electric-sql/client`** TypeScript package, which lives at
`packages/typescript-client/` inside the Electric monorepo. The repo is already
cloned for you at `/workspace/electric` with all dependencies installed via
`pnpm`. Run unit tests with:

```bash
cd /workspace/electric/packages/typescript-client
pnpm exec vitest run --config vitest.unit.config.ts
```

## Symptom

Production telemetry has surfaced an HTTP 414 ("URI Too Long") incident on the
`ShapeStream` client when the upstream HTTP API returns repeated `409` ("must
refetch") responses **without** the `electric-handle` response header (this
happens in the wild when a CDN or reverse proxy strips it). The captured retry
URLs look like:

```
…/v1/shape?handle=87840909-…-next                   # 1st retry
…/v1/shape?handle=87840909-…-next-next              # 2nd retry
…/v1/shape?handle=87840909-…-next-next-next         # 3rd retry
…/v1/shape?handle=87840909-…-next-next-next-next    # 4th retry
…
```

A second pattern was observed when the client never received a valid handle
to begin with — the retry URL embedded the literal string `undefined`:

```
…/v1/shape?handle=undefined-next-next-next-…
```

After enough retries the URL exceeds the proxy's URI length limit and every
subsequent request fails with `414 URI Too Long`, which then degrades to
cascading 5xx errors.

## What "correct" looks like

After your fix, when the client receives a `409` response **without** an
`electric-handle` header, the following invariants must hold:

1. **No URL contains the substring `-next`.** The handle must not be mutated by
   appending suffixes; handles are server-issued opaque identities, not cache
   busters.
2. **No URL contains the substring `undefined`.** If the client never had a
   valid handle, the retry URL must simply omit the `handle` query param
   rather than stringify `undefined`.
3. **Every retry URL is unique.** Two consecutive retries to the same
   logical shape must produce two distinct URLs (otherwise CDNs will replay
   the same cached 409 forever). Use the existing `cache-buster` query
   parameter mechanism — the same one already employed by `StaleRetryState`
   for stale CDN responses — to guarantee uniqueness, or rely on
   `expired_handle` when that path applies.
4. **Both 409 code paths must be fixed.** The bug exists in two places: the
   main `ShapeStream` request loop and the snapshot-fetch path used while
   the live stream is paused. Both must produce URLs that satisfy the
   invariants above.
5. **Happy path is unchanged.** When a `409` response *does* include a fresh
   `electric-handle` header, the client must continue to adopt that handle
   exactly as before.
6. **The state-machine contract is preserved.** Per
   `packages/typescript-client/SPEC.md` invariant **I10**, resetting the
   stream when refetch is required must produce an `InitialState` with
   `offset === '-1'`, `schema === undefined`, `liveCacheBuster === ''`, and
   `lastSyncedAt` preserved. Drive the reset through the state machine's
   existing `markMustRefetch` API rather than mutating fields in place.

## How your fix is graded

Your change is checked by:

- A behavioral regression test that drives the `ShapeStream` through 8
  consecutive `409` responses (with the handle header stripped) and asserts:
  - no captured URL contains `-next`
  - no captured URL contains `undefined`
  - each retry URL after the first carries either a `cache-buster` or an
    `expired_handle` query parameter
  - the captured retry URLs are pairwise unique
- The repository's full unit-test suite, run via
  `pnpm exec vitest run --config vitest.unit.config.ts` — every existing
  test must continue to pass.
- `pnpm exec tsc -p tsconfig.json --noEmit` — must succeed.

## Out of scope

- Do not change the happy path (`409` with a handle header).
- Do not introduce a retry-count limit; the existing fast-loop detector is
  sufficient.
- Do not change the format of the `cache-buster` value used by other state
  transitions.
