# Add a per-RPC defect schema option to `@effect/rpc`

You are working in the `Effect-TS/effect` monorepo. The repo root is at
`/workspace/effect`. The relevant package is `packages/rpc`. Use `pnpm` —
the project pins `pnpm@10.17.1` and uses `pnpm` workspaces.

## Background

Inside `@effect/rpc`, an RPC's *defect* is the value that travels back to
the client when a server-side handler dies (i.e. throws something that is
not a typed `Error` channel — what `Effect.die(...)` produces). Today the
package hard-codes `Schema.Defect` for serialising every defect, regardless
of which RPC produced it. `Schema.Defect` is conservative: for arbitrary
non-`Error` values it serialises them by stringifying, so on the client
side the receiver gets back a JSON string instead of the original
structured object. The `code`, `stack`, custom tags, etc. that the
handler `die`d with are no longer accessible as properties.

For internal service boundaries this is painful: callers want the full
diagnostic shape preserved, not a summary string. There is currently no
way to override which schema the RPC uses for defects.

## What to do

Extend the public RPC definition surface so callers can opt into a
different defect schema **on a per-RPC basis**, while keeping the
existing default behaviour unchanged for all current call sites.

The new option must be wired into the public `Rpc.make` entry point so
that a definition like

```ts
import { Rpc } from "@effect/rpc"
import { Schema } from "effect"

const MyRpc = Rpc.make("MyRpc", {
  success: Schema.String,
  defect: Schema.Unknown
})
```

type-checks and behaves correctly. The option is optional; when absent,
the RPC must continue to use `Schema.Defect`, exactly as before.

The chosen schema must propagate through:

1. **`Rpc.exitSchema`** — when the option is set, the schema returned by
   `Rpc.exitSchema(rpc)` must encode/decode the defect using the
   user-supplied schema rather than `Schema.Defect`. Round-tripping an
   arbitrary value through that schema must reproduce the original value
   when the user picks `Schema.Unknown`.

2. **The Proto pipeline of `Rpc`.** Every method that returns a new
   `Rpc` instance derived from an existing one (for example chaining
   `setSuccess`, `setError`, `setPayload`, `middleware`, `annotate`,
   `annotateContext`, plus whatever else the file uses to thread Rpc
   state) must carry the defect schema through unchanged. After such a
   chain, `Rpc.exitSchema` on the resulting RPC must still use the
   original custom defect schema.

3. **`RpcServer`** — the server's per-RPC schemas cache (the object
   that today already pre-computes `decode`, `encodeChunk`, `encodeExit`
   etc. from each RPC) must also pre-compute an encoder for the defect
   schema, and the server must use *that* per-RPC encoder when sending
   a `Die` exit back to the client. Today the server uses a single
   module-level `Schema.encodeSync(Schema.Defect)` for every Die, which
   defeats the per-RPC override; that needs to be changed so the
   encoder used for a given Die comes from the cache entry of the RPC
   that produced it. The internal helpers that send Die responses
   (the function that constructs the `{ _tag: "Exit", exit: { _tag:
   "Failure", cause: { _tag: "Die", defect: <encoded> } } }` payload,
   and the per-call wrapper that catches a handler's failure cause and
   forwards it to that helper) need to receive and use the new
   encoder. Both the success-path (handler returns) and the
   payload-decode-failure path of a request must use the per-RPC
   encoder.

   Module-level / "fatal" defects that originate outside any specific
   RPC's context (for example the catch-all path that handles a top-
   level server failure with no associated requestId) are out of scope
   for this change — those still legitimately use `Schema.Defect`.

The internal `fromTaggedRequest` constructor, which builds an RPC from
a tagged-request schema and has no user-facing options, should default
to `Schema.Defect` so existing call sites are unaffected.

## Acceptance behaviour

A concrete way to think about the user-visible contract:

- Define an RPC with `defect: Schema.Unknown`.
- Take its exit schema via `Rpc.exitSchema(rpc)`, encode an
  `Exit.die({ message: "boom", stack: "...", code: 42 })`, then decode
  the result.
- `Cause.squash` of the failure cause from the decoded exit must be
  **deeply equal** to the original `{ message, stack, code }` object —
  every field preserved, no JSON-string flattening.

The same property must hold for primitive defects (e.g. a plain
number) and for nested-object defects.

If the same RPC is then chained through `setSuccess`, `setError`, etc.,
the property must continue to hold on the resulting RPC. Adding an RPC
to an `RpcGroup` must likewise preserve it.

Existing tests (the `Rpc` package test suite and the
`platform-node` `RpcServer.test.ts` suite — including its existing
`ProduceDefect` / `ProduceErrorDefect` / `defect serializes Error
objects` cases) must continue to pass.

## Code Style Requirements

The repo enforces several automated checks on every change. Your edits
must satisfy all of them:

- **`pnpm exec eslint <changed files>`** must exit cleanly. Config is
  `eslint.config.mjs` at the repo root (already installed).
- Per `AGENTS.md`, **avoid adding comments** unless absolutely required
  to explain unusual or complex logic. JSDoc on exported APIs is
  acceptable; explanatory line comments inside function bodies are not.
- Per `AGENTS.md`, **do not hand-edit `index.ts` barrel files** — they
  are generated. If a new export is needed, run `pnpm codegen`.
- All edits must keep `pnpm exec tsc -b` clean for the `rpc` package
  (no new type errors).

## Process notes

- Follow `AGENTS.md` for repo-wide expectations: zero tolerance for
  errors, clarity over cleverness, conciseness, and the requirement
  that pull requests include a `.changeset/*.md` entry describing the
  change.
- Do not introduce a new exported symbol for the option; extend the
  existing `Rpc.make` options object.
- Keep the change minimal — this is a feature addition that should not
  refactor surrounding code.
