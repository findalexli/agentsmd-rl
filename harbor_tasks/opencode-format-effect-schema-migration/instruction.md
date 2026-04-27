# Migrate `MessageV2.Format` from Zod to Effect Schema

This is the opencode TypeScript/Bun monorepo. The session-domain types are being
migrated from Zod to Effect Schema, one cluster at a time. Your job is the
**output-format slice**: the leaf schemas in
`packages/opencode/src/session/message-v2.ts` plus their callers.

## Working directory

```
/workspace/opencode/packages/opencode
```

All commands below assume this directory. Use `bun` for everything (do not
invoke `tsc`, `npm`, or `node` directly).

## Background — the bridge pattern

The repo already has a helper for keeping a Zod-compatible API on top of
Effect Schema values:

```ts
import { zod } from "@/util/effect-zod"
```

`zod(schema)` returns a Zod schema derived from an Effect Schema. The
established convention is:

- For a `Schema.Class`-based type, expose a static accessor:
  `static readonly zod = zod(this)`.
- For non-class schemas (unions, etc.), wrap with `Object.assign(_inner, { zod: zod(_inner) })`
  so callers can write `Foo.zod.safeParse(...)` / `Foo.zod.optional()`.

`src/session/schema.ts` already follows this pattern and is a working reference
— look at how `SessionID`, `MessageID`, `PartID` are defined and re-exported
with `.zod`.

## What to migrate

In `src/session/message-v2.ts`, exactly three exports must move from Zod to
Effect Schema:

1. **`OutputFormatText`** — currently `z.object({ type: z.literal("text") }).meta({ ref: "OutputFormatText" })`.
   It must become a `Schema.Class` named `"OutputFormatText"` with a single
   field `type: Schema.Literal("text")`. Constructing it with
   `new OutputFormatText({ type: "text" })` must work.

2. **`OutputFormatJsonSchema`** — currently `z.object({ ... }).meta({ ref: "OutputFormatJsonSchema" })`.
   It must become a `Schema.Class` named `"OutputFormatJsonSchema"` with:
   - `type: Schema.Literal("json_schema")`
   - `schema: Schema.Record(Schema.String, Schema.Any)` annotated with
     `identifier: "JSONSchema"`
   - `retryCount: number, integer, ≥ 0, optional with a decoding default of 2`
     (so a payload that omits `retryCount` decodes to `retryCount: 2`).

3. **`Format`** — currently `z.discriminatedUnion("type", [OutputFormatText, OutputFormatJsonSchema])`.
   It must become a `Schema.Union` over the two classes, annotated with
   `discriminator: "type"` and `identifier: "OutputFormat"`. The exported
   `Format` value must additionally expose a `.zod` property holding the
   derived Zod schema (so callers can keep using `Format.zod.safeParse(...)`,
   `Format.zod.optional()`, etc.).

The exported TypeScript type alias `OutputFormat` must continue to resolve to
the parsed shape of `Format` after the migration (it can no longer use
`z.infer`).

Each of `OutputFormatText`, `OutputFormatJsonSchema`, and `Format` must expose
a `.zod` accessor that mirrors the original Zod parsing behaviour:

- `OutputFormatText.zod.safeParse({ type: "text" })` succeeds; any other shape
  fails.
- `OutputFormatJsonSchema.zod.safeParse({ type: "json_schema", schema: {...} })`
  succeeds and fills in `retryCount: 2` by default; explicit positive integers
  are accepted; negative numbers and a missing `schema` are rejected.
- `Format.zod.safeParse(...)` accepts both variants and rejects an unknown
  `type`.

After the migration, `Format` (and the two leaf schemas) no longer themselves
expose Zod methods like `.safeParse` or `.optional` — those live on the
derived `.zod` schema.

## Caller updates

Two call sites currently rely on the old Zod API of `Format`:

- `src/session/message-v2.ts` itself, in the `User` schema, does
  `format: Format.optional()`.
- `src/session/prompt.ts`, in the exported `PromptInput` schema, does
  `format: MessageV2.Format.optional()`.

After the migration, `Format` is an Effect Schema value and no longer has a
`.optional()` method. Both call sites must be updated to go through
`Format.zod.optional()` so the surrounding `z.object({...})` definitions still
type-check and parse the same way they did before.

The `User` schema must continue to accept a payload whose `format` is either
absent, `{ type: "text" }`, or `{ type: "json_schema", schema: {...} }`.

## Test-file updates

The tests in `test/session/structured-output.test.ts` currently call
`MessageV2.Format.safeParse(...)` directly. After the migration this method
no longer exists on `Format`. Update the affected `safeParse` call sites in
that file to go through the Zod-bridge accessor so the tests keep verifying
the same behaviour.

## Verification

From `/workspace/opencode/packages/opencode`:

```bash
bun test test/session/structured-output.test.ts --timeout 30000
bun test test/session/message-v2.test.ts --timeout 30000
```

Both files must continue to pass (22 + 24 tests respectively). Additional
behavioural tests will check that `OutputFormatText`, `OutputFormatJsonSchema`,
and `Format` are now Effect Schema values with working `.zod` accessors and
that `SessionPrompt.PromptInput` still parses payloads with a `format` field.

## Code Style Requirements

This repo follows the rules in `AGENTS.md` (root) and
`packages/opencode/AGENTS.md`:

- Avoid `any` outside of test or interop boundaries.
- Use `const`; avoid `let`, `else`, and unnecessary destructuring.
- Use Bun APIs and Effect services where available.
- Prefer the existing `Schema.Class` / `static readonly zod = zod(this)` pattern
  used elsewhere in `src/session/`.

No new lint or formatter is run as part of the verification, but keep the
diff stylistically consistent with the surrounding code.
