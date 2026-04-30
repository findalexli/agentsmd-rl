# Fix streaming tool-call schema in `@effect/ai-openrouter`

## Background

The OpenAI-compatible streaming protocol (which OpenRouter speaks)
delivers each assistant message as a sequence of Server-Sent-Event
"delta" chunks. When the assistant emits a tool call, the call is
**spread across multiple chunks**:

- The **first** chunk carries the call's `id`, `type`, and the tool
  `function.name`. Its `function.arguments` is usually `""` or a partial
  JSON prefix.
- **Subsequent** chunks for the same `index` carry **only** additional
  `function.arguments` fragments — `id` and `function.name` are absent.

The schema in `packages/ai/openrouter/src/OpenRouterClient.ts` that
parses these chunks (`ChatStreamingMessageToolCall`) is too strict: it
requires `function.name` on every chunk. As a result, every streaming
response that contains a tool call fails decoding with
`MalformedOutput` as soon as the second chunk arrives.

`id` on the same schema is already declared as
`Schema.optionalWith(Schema.String, { nullable: true })`, which is the
correct pattern for these protocol-level optional fields.

## What you need to do

Update the streaming tool-call schema so that **`function.name` is
optional** in the same way `id` is — accepting chunks where the field is
missing or `null`, while still preserving its value when present.

`function.arguments` must remain a required string (the protocol always
sends an `arguments` field on every chunk for that tool call, even if
it's the empty string).

After the fix:

- A chunk shaped `{ index, type: "function", function: { arguments } }`
  (no `name`, no `id`) must decode successfully.
- A chunk shaped `{ index, id, type: "function", function: { name,
  arguments } }` must still decode and round-trip the `name`.
- A chunk missing `function.arguments` must still be rejected.

## Reference

- File: `packages/ai/openrouter/src/OpenRouterClient.ts`
- Class: `ChatStreamingMessageToolCall`
- The shape of OpenAI-compatible tool-call deltas is documented at
  <https://platform.openai.com/docs/api-reference/chat-streaming/streaming>
  (see the `delta.tool_calls[].function` object).

## Project Conventions

The repository's `AGENTS.md` lists rules every PR must follow. The ones
relevant to this change:

- **Changesets** — every PR must include a changeset in the
  `.changeset/` directory describing the fix. The file's frontmatter
  must reference the affected package (`@effect/ai-openrouter`) with a
  semver bump level (`patch` is appropriate for a bug fix).
- **Conciseness** — keep code and any wording concise.
- **Reduce comments** — do not add comments unless absolutely required.
- **Follow established patterns** — look at existing schema fields (in
  particular how `id` is declared on the same class) before writing new
  code.
- **Barrel files are auto-generated** — never hand-edit any
  `src/index.ts`.

## Code Style Requirements

The fix will be type-checked. The package's own `tsc -b tsconfig.json`
must succeed in `packages/ai/openrouter/` after your change. The
repository also uses `eslint` (run via `pnpm lint-fix`) — keep
formatting consistent with the surrounding code.
