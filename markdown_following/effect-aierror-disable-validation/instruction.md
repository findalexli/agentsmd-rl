# Preserve `Headers` prototype on AiError HTTP errors

This task lives in the `Effect-TS/effect` monorepo. The repository is already
cloned at `/workspace/effect` and all dependencies are installed (`pnpm
install --frozen-lockfile`). Use `pnpm` from inside the repo for everything.

## What is broken

The `@effect/ai` package (`packages/ai/ai/src/AiError.ts`) defines two error
classes that callers raise when an HTTP call fails:

- `AiError.HttpRequestError`
- `AiError.HttpResponseError`

Each one exposes a static factory that converts a platform-level
`HttpClientError` into the equivalent `AiError`:

- `AiError.HttpRequestError.fromRequestError({ module, method, error })`
- `AiError.HttpResponseError.fromResponseError({ module, method, error })`

The platform-level errors carry a `Headers` instance — a special object
created by `@effect/platform/Headers.fromInput(...)` whose prototype carries
the `HeadersTypeId` symbol. `Headers.isHeaders(x)` only returns `true` when
`x` still has that prototype.

After the existing factories run, the `Headers` instance has been replaced
with a plain object. The bug is observable from a call site like:

```ts
import * as AiError from "@effect/ai/AiError"
import * as Headers from "@effect/platform/Headers"
import * as HttpClientError from "@effect/platform/HttpClientError"
import * as HttpClientRequest from "@effect/platform/HttpClientRequest"

const requestHeaders = Headers.fromInput({ "x-api-key": "secret" })
Headers.isHeaders(requestHeaders)              // true

const platformErr = new HttpClientError.RequestError({
  request: HttpClientRequest.make("POST")("https://example.test", { headers: requestHeaders }),
  reason: "Transport"
})
const aiErr = AiError.HttpRequestError.fromRequestError({
  module: "M", method: "m", error: platformErr
})

Headers.isHeaders(aiErr.request.headers)       // false  ← BUG
```

`AiError.HttpResponseError.fromResponseError(...)` returns an `Effect` that
fails with an `HttpResponseError`; the same prototype-stripping happens for
both `error.request.headers` and `error.response.headers` when that effect
is run.

## Expected behaviour

After the fix, all three of the following must hold for the values produced
by the factory methods:

1. `Headers.isHeaders(httpRequestError.request.headers) === true`
2. `Headers.isHeaders(httpResponseError.request.headers) === true`
3. `Headers.isHeaders(httpResponseError.response.headers) === true`

The ordinary scalar fields (`module`, `method`, `reason`, `request.method`,
`request.url`, `response.status`, ...) must continue to round-trip through
the factory unchanged.

## Hints

- Read the `Headers` model in `packages/platform/src/Headers.ts` to see how
  `isHeaders` and the `HeadersTypeId` symbol are wired.
- Read the existing `HttpRequestDetails` / `HttpResponseDetails` schemas at
  the top of `AiError.ts` — they describe `headers` as a string-to-string
  record. Think about what that schema does to the value when an error is
  constructed, and which constructor option lets you skip it.
- The fix is small (single-digit lines) and lives entirely inside the
  `@effect/ai` package's `AiError` module. Nothing in `packages/platform`
  or in `packages/effect` needs to change.

## Repository conventions you must follow

`AGENTS.md` at the repo root lists the rules. The ones that apply here:

- **Changesets**: every PR that touches package source must ship a file in
  `.changeset/` with YAML frontmatter declaring the affected package and
  release type. For this fix add a `.changeset/<some-name>.md` whose
  frontmatter is `"@effect/ai": patch` and whose body briefly summarises the
  change.
- **Type checking must pass** for the `@effect/ai` package: from inside
  `packages/ai/ai`, `pnpm exec tsc -b tsconfig.json` must exit 0.
- **Reduce comments**: do not add comments unless they explain non-obvious
  intent. JSDoc on public APIs is fine.
- **Conciseness / clarity over cleverness**: prefer the smallest readable
  change.
- **Do not touch barrel `index.ts` files** — they are generated.

## Code Style Requirements

The repo uses ESLint and TypeScript. Your edit must:

- Pass `pnpm exec tsc -b tsconfig.json` from `packages/ai/ai` (no new type
  errors).
- Not break the existing JSDoc examples in `AiError.ts` (the surrounding
  examples still need to compile).

You do not need to invoke `pnpm lint-fix` or `pnpm build` — the grader runs
its own checks — but your patch should be consistent with the surrounding
formatting (2-space indent, no trailing whitespace, no stray imports).

## What the grader checks

- The three `Headers.isHeaders(...)` assertions above all return `true`
  after the factories run.
- The scalar fields on the produced errors are unchanged. The grader's test
  fixture constructs a request error with method `"POST"`, URL
  `"https://api.example.com/v1/chat"`, module `"TestModule"`, reason
  `"Transport"` and a response error with status `429`, module
  `"TestModule"`, reason `"StatusCode"` — all of these must round-trip
  back to the caller without alteration.
- A `.changeset/*.md` exists that names `"@effect/ai"` with a `patch`,
  `minor`, or `major` release type.
- `pnpm exec tsc -b tsconfig.json` exits 0 for the `@effect/ai` package.
