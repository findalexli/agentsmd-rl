# Add per-RPC defect schema support

The `@effect/rpc` package currently hardcodes `Schema.Defect` as the defect
schema used when building the `Exit` schema via `Rpc.exitSchema()`. This means
defect objects that carry extra diagnostic fields (stack traces, error codes,
custom metadata) get truncated to `{ message: "..." }` during serialization.

For internal service-to-service communication, it is useful to preserve the
full defect value so downstream consumers can see stack traces and other
diagnostic information.

## What to build

Give `Rpc.make()` an optional parameter that lets callers supply a custom defect
schema. When provided, the custom schema must flow through every path that
constructs or transforms an RPC definition so that `Rpc.exitSchema()` uses it
instead of the hardcoded `Schema.Defect`.

The custom schema should default to `Schema.Defect` so all existing callers are
unaffected.

## Behavioral contract

After the change, the following scenario must work:

1. Create an RPC with `Rpc.make("AnyName", { success: Schema.String })`
2. Attach a custom defect schema — `Schema.Unknown` is a natural choice
   because it preserves any value without transformation
3. Call `Rpc.exitSchema(rpc)` to get the Exit schema
4. Encode then decode an `Exit.die(...)` where the defect is a plain object:
   `{ message: "boom", stack: "Error: boom\n  at foo.ts:1", code: 42 }`
5. After round-tripping through encode/decode with `Schema.encodeSync` and
   `Schema.decodeSync`, the decoded defect must equal the original object
   (verified with `assert.deepStrictEqual`)

This does NOT work on the current code because `Rpc.exitSchema()` ignores any
attached defect schema and always uses the hardcoded `Schema.Defect`, which
strips all fields except `message`.

## RpcServer integration

The `@effect/rpc` server in `RpcServer.ts` has a `sendRequestDefect` function
that encodes defect values before sending them to the client. Currently it uses
a module-level `encodeDefect = Schema.encodeSync(Schema.Defect)`. After the
change, each RPC's own defect encoder must be used instead, so that a per-RPC
defect schema is honored during server-side encoding.

The server already maintains a per-RPC `schemas` cache. The defect encoder
should be added to that cache and threaded through the `handleEncode` and
`sendRequestDefect` call chains.

The module-level `Schema.Defect` encoder should still be used for protocol-level
defects — fatal infrastructure failures that occur outside any specific RPC handler.

## Constraints

- All existing RPC tests must continue to pass
- No breaking changes to the public API of `Rpc.make()` — the new parameter is
  optional
- The `Rpc.fromTaggedRequest()` path must also carry a defect schema (set it to
  `Schema.Defect` since tagged requests have no way to specify a custom one)
- Follow the existing pattern in `Proto` methods where every transformation
  spreads all fields from the current RPC and overrides only the changed one

## Code Style Requirements

Run these commands after making changes:
- `pnpm lint-fix` to format code
- `pnpm check` for type checking
