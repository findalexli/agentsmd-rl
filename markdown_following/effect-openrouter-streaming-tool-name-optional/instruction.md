# Streaming tool-call chunks fail to decode in @effect/ai-openrouter

The `@effect/ai-openrouter` package ships a `Schema.Class` named
`ChatStreamingMessageToolCall` that is used to decode tool-call entries that
arrive as Server-Sent Events from the OpenRouter / OpenAI Chat Completions
streaming API.

## The bug

Per the OpenAI streaming protocol, a single tool call is split across many SSE
chunks:

- The **first** chunk carries `id`, `type: "function"`, and
  `function.name`.
- **Subsequent** chunks carry only `index`, `type: "function"`, and an
  `function.arguments` delta — `id` and `function.name` are absent.

Today the schema rejects every continuation chunk and the model run aborts
with a `MalformedOutput` parse error. The encoded shape it currently demands
is:

```ts
{
  index: number,
  id?: string | null,
  type: "function",
  function: { name: string, arguments: string }
}
```

`id` is already optional/nullable. `function.name` should be exactly the same
shape as `id` — optional and nullable — so that continuation chunks (and
chunks where the provider returns `name: null`) decode successfully.

`function.arguments` must remain required: every chunk we accept carries an
arguments delta, even if it is the empty string `""`.

## What "decode successfully" means

For both of the following inputs, calling
`Schema.decodeUnknown(ChatStreamingMessageToolCall)(input)` must succeed (no
`ParseError`):

```ts
// continuation chunk
{ index: 0, type: "function", function: { arguments: "{\"a\":1}" } }

// explicit null name
{ index: 1, id: null, type: "function", function: { name: null, arguments: "abc" } }
```

A correct fix should not loosen any other field — initial chunks with
`id` and `function.name` populated must still decode, and a chunk that omits
`function.arguments` must still be rejected.

## Other repository expectations

- This package lives in a `pnpm` monorepo. After your edit, the openrouter
  package must continue to type-check (`pnpm check` from
  `packages/ai/openrouter/`) and lint cleanly.
- Per the repo's `AGENTS.md`, every PR adds a changeset under `.changeset/`.
  Add one for this fix as a `patch` for `@effect/ai-openrouter` describing
  the change in one or two sentences. The changeset filename can be any
  descriptive slug.
- Keep the change minimal — do not edit auto-generated `index.ts` barrel
  files, do not add comments unless they explain something non-obvious, and
  follow the existing schema-definition style already used elsewhere in the
  same file (look at how the sibling `id` field is declared).

## Code Style Requirements

The repository's CI runs:

- **`pnpm check`** (TypeScript `tsc -b`) — must pass with no errors.
- **`pnpm exec eslint packages/ai/openrouter/src`** — must pass with no
  errors. The repo's ESLint config enforces import sorting and the project's
  `@effect/eslint-plugin` rules. If you are unsure about formatting, run
  `pnpm lint-fix` from the repo root.
