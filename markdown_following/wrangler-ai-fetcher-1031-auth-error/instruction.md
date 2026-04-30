# Helpful login hint when the AI binding hits a 403 auth error

You are working in the `cloudflare/workers-sdk` monorepo on the **wrangler**
package.

## Background

`wrangler` exposes a local AI binding that proxies inference requests through
a Cloudflare-hosted endpoint. The proxy authenticates the developer with a
short-lived token. If the user has been working for a long time, the token
can expire mid-session and the proxy starts returning HTTP `403` responses
whose JSON body looks like:

```json
{ "errors": [{ "code": 1031, "message": "Forbidden" }] }
```

Today wrangler simply forwards that 403 back to the caller with no
explanation. Users report being confused — the error gives them no path
forward.

## Your task

When the AI proxy returns a `403` whose body contains an error with
`code === 1031` (the Cloudflare API code for "auth token expired or lacks
required permissions"), wrangler must log a clear, actionable error message
that names the code and tells the user how to recover. The exact message
wrangler must surface is:

```
Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`.
```

The message must be emitted via wrangler's standard `logger.error(...)` so
that it reaches the user's terminal through the normal logging pipeline.

### Constraints

- **Only the 1031 case is special.** A 403 whose body has different error
  codes (or no `errors` array, or a body that is not valid JSON) must
  *not* produce this log line — wrangler must continue forwarding the
  upstream response unchanged. The message must also not be emitted on
  successful responses or other status codes.
- **Never throw on the diagnostic path.** A 403 with a body that fails to
  parse as JSON must not crash the fetcher; it must continue and return
  the original 403 to the caller.
- **Preserve the response.** The status code, headers, and body of the
  upstream 403 must reach the caller untouched — your diagnostic logging
  must not consume or mutate the response body. Reading the body for the
  diagnostic is fine as long as a fresh, unread copy is what gets returned.
- The fix lives entirely inside the wrangler package.

## Code Style Requirements

This repo's CI runs the wrangler TypeScript typecheck (`tsc -p ./tsconfig.json`)
on every change. Your fix must satisfy it. In particular:

- **No `any`** — `@typescript-eslint/no-explicit-any` is enforced. Type the
  parsed body explicitly.
- **No non-null assertions (`!`)** — narrow with optional chaining / `if`
  checks instead.
- **No floating promises** — every promise is either `await`ed or
  explicitly `void`ed.
- **`import type { ... }`** for type-only imports.
- **Use the `logger` singleton** (`import { logger } from "../logger"`) —
  never `console.*`.
- **Always brace control flow.**

The repo's release-notes pipeline expects every user-facing change to a
published package to have a changeset under `.changeset/`. Add a `patch`
entry for `wrangler` describing the fix in plain prose (no h1/h2/h3
headers).
