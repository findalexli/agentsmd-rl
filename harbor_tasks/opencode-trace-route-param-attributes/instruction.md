# Tag HTTP route spans with their route parameters

You are working in the `opencode` Bun/TypeScript monorepo. The HTTP server in
`packages/opencode` wraps every route handler with an Effect span that carries
the request's `http.method` and `http.path`. Tracing UIs (motel) display these
attributes in the **Tags** panel of each trace's root span.

Today, the only attributes emitted by `runRequest` are:

```
http.method: POST
http.path:   /session/ses_abc/prompt_async
```

That makes traces unsearchable by the IDs that actually identify the request:
to find a session's traces you have to regex over the path string.

## What the helper must do

In `packages/opencode/src/server/routes/instance/trace.ts`, introduce a helper
that builds the attribute map for a request, and have `runRequest` use it.
The helper has the contract below.

**Name:** `requestAttributes` — must be a named export of `trace.ts`. It is
imported under that name from a unit-test file (see *Tests* below).

**Input:** an HTTP request context shaped like the existing Hono `Context` —
specifically, its `.req` exposes `method: string`, `url: string`, and a
`param(): Record<string, string>` method that returns the route's matched
parameters. The implementation must accept this minimal shape so the helper is
testable without a live Hono app.

**Output:** a `Record<string, string>` of OpenTelemetry-style span attributes:

| Attribute key | Value |
|---|---|
| `http.method` | the request's HTTP method, verbatim |
| `http.path` | the URL **pathname** only — the query string is stripped |
| `opencode.<paramName>` | one entry per matched route param, prefixed `opencode.` |

The route-param attributes use the **exact** parameter name from the route
definition — `sessionID` → `opencode.sessionID`, `messageID` →
`opencode.messageID`, `name` → `opencode.name` (no renaming, no kebab-case
conversion). When a route has no matched params, no `opencode.*` keys appear
in the result. The unprefixed key (e.g. `sessionID`) must NOT appear in the
output.

## Wire it through

`runRequest(name, c, effect)` currently builds its attribute object inline
when calling `Effect.withSpan`. Refactor it to delegate to the new helper —
otherwise the route-param tags only show up when something calls the helper
directly, never on real request spans. `jsonRequest` calls `runRequest`
internally and should not need any changes.

## Tests

Add a `bun:test` file at `packages/opencode/test/server/trace-attributes.test.ts`
that imports `requestAttributes` from
`../../src/server/routes/instance/trace` and verifies each of:

- `http.method` and `http.path` are populated for a basic request.
- The query string is stripped from `http.path`.
- Route params are tagged with the `opencode.` prefix using the exact param
  names (covering nested-ID routes such as
  `/session/:sessionID/message/:messageID/part/:partID`).
- A request with no matched params produces no `opencode.*` attributes.
- A non-ID param name (e.g. the MCP `:name` param at
  `/mcp/:name/connect`) is preserved verbatim as `opencode.name`.

Use a small `fakeContext(method, url, params)` helper rather than spinning up
a real Hono app — it should return an object with the minimal `{ req: {
method, url, param() } }` shape.

## Code Style Requirements

The repo's `AGENTS.md` and `packages/opencode/AGENTS.md` documents define the
project's TypeScript conventions. Relevant ones for this change:

- Avoid unnecessary `try`/`catch`.
- Avoid the `any` type — let TypeScript infer types where possible.
- Prefer `const` over `let`.
- Prefer functional array methods (`map`, `filter`, `flatMap`, `Object.entries`)
  over imperative `for` loops where natural; either style is acceptable here
  as long as the result is the documented attribute map.
- Avoid unnecessary destructuring; use dot notation when it makes the call site
  clearer.
- Avoid mocks where possible: the `fakeContext` helper above is a minimal
  hand-rolled stand-in for a Hono `Context`, not a mocking library.
- Tests cannot run from the repo root — run from `packages/opencode` (the
  root `package.json` has `"test": "echo 'do not run tests from root' && exit 1"`).
