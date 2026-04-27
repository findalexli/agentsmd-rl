# OpenAI Responses model: structured outputs lost when verbosity is set

The repository at `/workspace/openai-agents-js` is checked out at base
commit `2260e21192…` of `openai/openai-agents-js`. Run the agent's
toolchain (`pnpm install` already complete; `pnpm exec vitest run …`
works) from the repo root.

## Symptom

Configure an `Agent` whose `model` is `OpenAIResponsesModel` (e.g.
`'gpt-5'`) and which both:

1. declares an `outputType` for structured output (e.g. a Zod object
   schema serialized as a JSON-schema definition with
   `type: 'json_schema'`), and
2. sets `modelSettings.providerData.text` — for example the new gpt-5
   knob `{ verbosity: 'low' }`.

The serialized request that reaches the OpenAI Responses API is wrong:
the `text` field on the request body contains **only** the entries from
`providerData.text` (so `{ verbosity: 'low' }`) and the structured-output
`format` slot is missing. The model therefore returns plain text instead
of a JSON object that conforms to the requested schema.

The expected behaviour is that the request's `text` field contains
**both** the user-supplied keys from `providerData.text` (e.g.
`verbosity`) **and** the `format` derived from `outputType`, merged into
a single object.

## Concretely

Assume the agent's request comes through with:

```ts
modelSettings.providerData = { text: { verbosity: 'low' } };
outputType = {
  type: 'json_schema',
  name: 'TestSchema',
  strict: true,
  schema: { /* … */ },
};
```

Then the body of the call to `client.responses.create(...)` must satisfy:

- `args.text.format` deeply equals the `outputType` object above.
- `args.text.verbosity === 'low'`.
- Other entries in `providerData` (e.g. `reasoning`) still appear at the
  top level of the request body, not nested under `text`.

When `outputType === 'text'`, `args.text` must still carry through any
`providerData.text` entries (e.g. `verbosity`), and `args.text.format`
must be `undefined`.

When there is no `providerData` at all and `outputType` is structured,
`args.text` must equal `{ format: outputType }`.

## Where to look

`packages/agents-openai/src/openaiResponsesModel.ts` is the package that
serializes a `ModelRequest` into the OpenAI Responses API call. The fix
lives entirely inside this file. Do not modify the public types in
`@openai/agents-core`.

## Code Style Requirements

The repository's contributor guide (`AGENTS.md`) requires:

- `pnpm -F @openai/agents-openai build-check` (TypeScript `--noEmit`)
  must pass — no new type errors.
- Comments must end with a period.
- Existing tests in `packages/agents-openai/test/` must keep passing
  (run with `pnpm exec vitest run packages/agents-openai/test/`).

## Out of scope

You do **not** need to:

- Update the example program in `examples/basic/`.
- Add a changeset entry under `.changeset/`.
- Touch any other package.
