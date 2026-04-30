# Effect AiError: HTTP errors lose Headers prototype

You are working in the Effect monorepo (`/workspace/effect`), specifically
in the `@effect/ai` package (`packages/ai/ai`).

## Symptom

`@effect/platform` represents HTTP headers via a `Headers` object whose
prototype carries an `[HeadersTypeId]` brand and a `[symbolRedactable]`
implementation (so `Headers.isHeaders(value)` returns `true` and the
inspector can later redact secrets).

The two `AiError` factories that wrap a platform `HttpClientError` should
forward those headers without losing that prototype:

* `AiError.HttpRequestError.fromRequestError(...)` — populates a new
  `HttpRequestError` whose `.request.headers` comes from the original
  `RequestError.request.headers`.
* `AiError.HttpResponseError.fromResponseError(...)` — populates a new
  `HttpResponseError` whose `.request.headers` comes from the original
  `ResponseError.request.headers` and whose `.response.headers` comes from
  the original `ResponseError.response.headers`.

After calling either factory, `Headers.isHeaders(...)` on the resulting
header fields currently returns `false`. The headers have been re-built as
plain `{ [k: string]: string }` objects with no prototype, so the redaction
behavior they carried is silently dropped.

## Expected behavior

Each of the following must be `true` after the factory returns:

* `Headers.isHeaders(httpRequestError.request.headers)` — for the result of
  `AiError.HttpRequestError.fromRequestError({ module, method, error })`.
* `Headers.isHeaders(httpResponseError.request.headers)` — for the result
  (in the failure channel of the returned `Effect`) of
  `AiError.HttpResponseError.fromResponseError({ module, method, error })`.
* `Headers.isHeaders(httpResponseError.response.headers)` — for the same
  `HttpResponseError`.

The shape and field values of the resulting errors must otherwise stay the
same: existing `@effect/ai` tests (under `packages/ai/ai/test/`) must keep
passing, and the package must still type-check.

## Reproduction sketch

```ts
import * as Headers from "@effect/platform/Headers"
import * as HttpClientRequest from "@effect/platform/HttpClientRequest"
import * as HttpClientError from "@effect/platform/HttpClientError"
import { AiError } from "@effect/ai"

const headers = Headers.fromInput({ authorization: "Bearer secret" })
const request = HttpClientRequest.get("https://example.com").pipe(
  HttpClientRequest.setHeaders(headers)
)
const requestError = new HttpClientError.RequestError({ request, reason: "Transport" })
const aiError = AiError.HttpRequestError.fromRequestError({
  module: "M", method: "m", error: requestError
})

Headers.isHeaders(aiError.request.headers) // currently false; must be true
```

## Code Style Requirements

* Follow the repository's `AGENTS.md`. In particular, after editing files
  run `pnpm lint-fix`, `pnpm test run`, `pnpm check`, and `pnpm build` and
  resolve any issues — the project has zero tolerance for lint, test,
  type-check, or build errors.
* Add a changeset under `.changeset/` for the fix (the project requires one
  for every PR; the affected package is `@effect/ai`).
* Keep the change minimal and focused: prefer a clear, idiomatic fix over
  a clever workaround, and do not introduce unrelated edits or comments.
