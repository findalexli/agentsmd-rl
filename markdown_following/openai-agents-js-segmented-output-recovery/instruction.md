# Recover segmented assistant output in agent tools and finalization

You are working in the `openai-agents-js` monorepo at
`/workspace/openai-agents-js`. The repository is a pnpm workspace; the
relevant package for this task is `@openai/agents-core` under
`packages/agents-core/`.

## Background

When the OpenAI Responses API streams an assistant turn, the final
`message` item can carry **multiple `output_text` content segments** in
order — for example, when a long answer arrives in chunks or when
structured-JSON output is split across deltas:

```jsonc
{
  "type": "message",
  "role": "assistant",
  "content": [
    { "type": "output_text", "text": "first " },
    { "type": "output_text", "text": "second" }
  ]
}
```

The full assistant message text is the in-order concatenation of every
`output_text` segment (`"first second"` in the example above). Other
content types (e.g. `refusal`) MUST be skipped, but they MUST NOT
abort the concatenation — segments after a non-text item still
contribute their text.

## The bug

The runtime currently derives the final assistant text from **only the
last `output_text` segment** of the trailing assistant message. This
truncates user-visible output in two places:

1. **`Agent.asTool()`** — when one agent invokes another agent as a
   tool, the parent receives only the tail chunk of the nested agent's
   answer instead of the complete reply. For a plain-text reply with
   segments `["first ", "second"]` the parent sees `"second"` instead
   of `"first second"`.

2. **Normal turn finalization** in
   `resolveTurnAfterModelResponse` — the resolved `nextStep.output`
   for an `outputType: 'text'` agent is the last segment only. For an
   agent with a structured `outputType` (e.g. a `zod` schema) whose
   JSON payload is split across segments such as
   `['{"foo":"ba', 'r"}']`, parsing fails because the partial tail
   `'r"}'` is not valid JSON for the schema.

## What you need to fix

In `packages/agents-core/src/utils/messages.ts`, the helper that the
runtime uses to derive the final assistant text from a `message` item
must return the **concatenation of all `output_text` segments** in
their original order (skipping non-`output_text` content), not just
the last segment. The shared "get text from output message" helper is
consumed both by `getOutputText(modelResponse)` (which feeds
`Agent.asTool` finalization via the runner) and by
`resolveTurnAfterModelResponse` in
`packages/agents-core/src/runner/turnResolution.ts`. Both call sites
must end up using the concatenating behavior.

You MUST preserve `getLastTextFromOutputMessage`'s existing semantics
(returning only the last `output_text` segment, or `undefined` if the
last content item is not an `output_text`) so that any caller that
specifically wants the tail chunk continues to work. The new
"concatenate-all" behavior should be exposed alongside it, not by
mutating `getLastTextFromOutputMessage` itself.

## Acceptance criteria (observable)

After your fix, the following must hold for the public API of
`@openai/agents-core`:

- `getOutputText(response)` returns `"first second"` for a response
  whose final assistant message has content
  `[{type:'output_text', text:'first '}, {type:'output_text', text:'second'}]`.
- `getOutputText(response)` returns `'{"answer":"structured"}'` for a
  response whose final assistant message has content
  `[{type:'output_text', text:'{"answer":"str'}, {type:'output_text', text:'uctured"}'}]`.
- `getOutputText(response)` returns `"part1part2"` for a final message
  whose content is
  `[{type:'output_text', text:'part1'}, {type:'refusal', refusal:'ignored'}, {type:'output_text', text:'part2'}]`
  (non-`output_text` segments are skipped, not boundary stops).
- `getLastTextFromOutputMessage(item)` continues to return `"b"` for
  a message whose content is
  `[{type:'output_text', text:'a'}, {type:'output_text', text:'b'}]`.
- `Agent.asTool(...).invoke(ctx, ...)` returns `"first second"` (not
  `"second"`) when the underlying run returns a single assistant
  `message` with content
  `[{type:'output_text', text:'first '}, {type:'output_text', text:'second'}]`.
- The agents-core type check must pass (`pnpm -F @openai/agents-core
  build-check`).

## Constraints

- Do not change package public exports in incompatible ways. You may
  add new exports to `packages/agents-core/src/utils/messages.ts`, but
  the existing exports `getLastTextFromOutputMessage` and
  `getOutputText` must remain exported with compatible signatures.
- Do not modify files outside `packages/agents-core/`.
- Do not weaken existing assistant/role guards: a non-`message`
  output item, or a `message` whose `role !== 'assistant'`, must
  still cause the helper(s) to return `undefined`.

## Code Style Requirements

The TypeScript type checker (`pnpm -F @openai/agents-core build-check`,
which runs `tsc --noEmit` against `tsconfig.test.json`) is part of the
verifier. Your code must type-check cleanly there. Per the repository's
contributor guide (`AGENTS.md`):

- Comments must end with a period.
- Public APIs (exported functions) must have JSDoc-style doc comments.
- Follow the existing TypeScript style used in
  `packages/agents-core/src/utils/messages.ts`.

## Where to look

- `packages/agents-core/src/utils/messages.ts` — the helpers that
  derive text from a `ResponseOutputItem`.
- `packages/agents-core/src/runner/turnResolution.ts` — the runtime
  caller that decides the final output of a turn.
- `packages/agents-core/test/utils/messages.test.ts` — the existing
  unit tests you must not break.

If your change affects the public API of `@openai/agents-core`, add a
patch-level changeset entry under `.changeset/` describing the fix
(see `AGENTS.md` for the project's changeset workflow).
