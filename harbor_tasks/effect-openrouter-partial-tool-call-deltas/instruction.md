# OpenRouter streaming tool-call decoder rejects partial deltas

## Background

The Effect monorepo at `/workspace/effect` contains the package
`@effect/ai-openrouter` (under `packages/ai/openrouter`), which models the
OpenRouter chat-completions streaming API using `effect/Schema`. Streaming
responses are split into many SSE-style chunks, and a single tool-call may
be reassembled from several deltas: the first delta typically carries an
`id` and the function name, while later deltas carry only fragments of the
JSON `arguments` string. Per the OpenAI/OpenRouter streaming protocol, every
field in a delta except the index is optional — the consumer is expected to
merge deltas by `index` until the stream ends.

## Symptom

When the package's streaming decoder consumes a real OpenRouter response,
some tool-call chunks fail to decode. The schema for an individual streaming
tool-call delta currently demands

* `type` — required, fixed to the literal `"function"`, and
* `function.arguments` — required, a string,

so any delta that omits either field — for example the very first delta
where the model has not yet produced any argument bytes, or a continuation
delta that carries only an arguments fragment — is rejected with a
`MalformedOutput`-style decode error from `Schema.decodeUnknown`. The
upstream issue is tracked in the repo as #6128.

Concretely, decoding any of the following inputs against the current schema
must succeed once the bug is fixed (today they all fail):

* `{ "index": 0, "id": "call_1", "function": { "name": "lookup" } }`
  (no `type`, no `arguments`)
* `{ "index": 0, "id": "call_1", "function": { "name": "lookup", "arguments": "{\"q" } }`
  (no `type`)
* `{ "index": 1, "type": "function", "function": { "name": "lookup" } }`
  (no `arguments`)
* `{ "index": 2, "function": { "arguments": "uery\":1}" } }`
  (continuation delta with only an arguments fragment)

## Required behaviour

Relax the streaming tool-call schema so that partial deltas decode without
error, while keeping the existing guarantees that protect callers
downstream:

1. A delta missing `type`, missing `function.arguments`, or missing both
   must decode successfully.
2. A delta carrying only an arguments fragment under `function`
   (no `name`, no `type`, no `id`) must decode successfully.
3. When `type` *is* present it must still be constrained to the literal
   string `"function"`; any other value must continue to be rejected.
4. `index` remains the only structurally required field on a streaming
   tool-call delta; a delta without `index`, or with `index` typed as
   anything other than a number, must continue to be rejected.
5. A fully-formed tool-call (with `index`, `id`, `type: "function"`, and a
   `function` object containing both `name` and `arguments`) must continue
   to decode without regression.

The change must apply to the schema used for streaming tool-call deltas
specifically; do not weaken the schemas for non-streaming responses.

## Code Style Requirements

* Run `pnpm lint-fix` after editing files (the project uses ESLint via
  `pnpm lint`).
* The package must continue to type-check: `pnpm exec tsc -b tsconfig.src.json`
  inside `packages/ai/openrouter` must exit cleanly.
* All `pnpm` commands run from the repository root unless noted otherwise.
* Match the surrounding code's use of `Schema.optionalWith(..., { nullable: true })`
  for fields that may be absent or `null` on the wire.

## Scope

* Only the schema definition needs to change. No public API renames, and
  no edits to generated files under `src/Generated.ts`.
* The repository is a pnpm workspace; all required dependencies are already
  installed at `/workspace/effect`. There is no need to run `pnpm install`.
