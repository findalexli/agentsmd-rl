# Preserve canonical Chat Completions envelopes when merging `providerData`

## Repo

You are working in `/workspace/openai-agents-js`, a pnpm monorepo. The package
in question is `@openai/agents-openai`.

## Symptom

Across the chat-completions converter (the helpers that turn this SDK's
internal `protocol.ModelItem` representation into the `messages` array sent to
OpenAI's Chat Completions API), arbitrary `providerData` from a model item is
spread directly onto the canonical envelope the SDK constructs. That spread
**lets `providerData` silently overwrite canonical fields**, even though
`providerData` is meant to carry only *extra* provider-specific metadata.

Concretely, given a `ModelItem` whose `providerData` contains keys that
collide with the canonical envelope, the converter currently produces wrong
output:

| Item kind                       | Reserved keys that must NOT be overwritten by `providerData` |
| ------------------------------- | ------------------------------------------------------------ |
| user message                    | `role`, `content`                                            |
| system message                  | `role`, `content`                                            |
| assistant message               | `role`, `content`, `tool_calls`, `audio`                     |
| function-call (tool-call)       | top-level: `id`, `type`, `function`, plus the assistant-level `role`, `content`, `tool_calls`, `audio`; nested `function`: `name`, `arguments` |
| function-call result (tool msg) | `role`, `tool_call_id`, `content`                            |
| `input_text` content part       | `type`, `text`                                               |
| `input_image` content part      | `type`, `image_url` (top level); `url` (nested in `image_url`) |
| `audio` content part            | `type`, `input_audio` (top level); `data` (nested in `input_audio`) |
| `file` content part             | `type`, `file`, `filename`                                   |
| `output_text` (assistant)       | `type`, `text`                                               |
| `refusal` (assistant)           | `type`, `refusal`                                            |
| Hosted `file_search_call` arguments JSON | `queries`, `status`, plus nested `name`/`arguments` and outer `id`/`type`/`function` |

Any key in `providerData` that is *not* on the reserved list for that envelope
must still be merged through unchanged.

### Concrete example of the bug

```ts
itemsToMessages([
  {
    type: 'message',
    role: 'user',
    content: 'real-user',
    providerData: {
      role: 'assistant',          // collides — must NOT win
      content: 'override-user',   // collides — must NOT win
      customUser: true,           // extra — MUST flow through
    },
  },
]);
```

Today this returns a message whose `role` is `'assistant'` and whose `content`
is `'override-user'`. After your fix, the result must keep `role: 'user'`, the
SDK-built `content`, and still expose `customUser: true`.

## Behavioural contract

For every code path listed in the table above, the resulting object sent to
OpenAI must satisfy:

1. The SDK-authored canonical fields are exactly what the existing converter
   builds (no change in their values).
2. Any `providerData` key that collides with a reserved name is dropped.
3. Any other `providerData` key (and any other key in nested objects like
   `image_url`, `input_audio`, `function`) is preserved verbatim.
4. `providerData` being `undefined`, `null`, or a non-object is a no-op (the
   canonical envelope is returned unchanged).

## Where to look

The converter lives in `packages/agents-openai/src/`. Helpers that already
deal with `providerData` shape conversion are co-located with the converter.

## Code Style Requirements

The repository's automated checks and contributor guide enforce style. Your
fix must satisfy all of:

- **`pnpm lint`** (ESLint, configured by `eslint.config.mjs`, with Prettier
  defaults) passes cleanly.
- **`pnpm -F @openai/agents-openai build-check`** (TypeScript
  `tsc --noEmit -p tsconfig.test.json`) passes — the change must remain
  type-safe under the project's strict settings.
- Any new or modified inline comments end with a period.
- Add or update unit tests under `packages/agents-openai/test/` covering the
  new behaviour, unless infeasible.
- Because this PR touches a published package, add an appropriate
  `.changeset/*.md` file using a Conventional-Commit-style summary
  (e.g. `fix: ...`) at patch level for `@openai/agents-openai`.

## Verification

The grader will, in order:

1. Run the existing `@openai/agents-openai` vitest suite — it must keep
   passing.
2. Run a behavioural test that constructs items whose `providerData`
   contains every reserved key listed in the table above, and assert the
   canonical envelope is preserved while the extras flow through.
3. Run `pnpm lint` and `pnpm -F @openai/agents-openai build-check`.

You may run these commands locally at any time.
