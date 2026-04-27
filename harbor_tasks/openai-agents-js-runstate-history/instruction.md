# Expose run history on `RunState`

In the `@openai/agents-core` package (`packages/agents-core/`), the
`RunState` class tracks the conversation context for an agent run.
Internally it already carries:

- `_originalInput: string | AgentInputItem[]` — the input the run was
  started with (a plain string or an array of `AgentInputItem`s).
- `_generatedItems: RunItem[]` — the items generated during the run
  (model messages, tool calls, etc.).

There is, however, no public way to obtain the **combined conversation
history** (original input followed by newly-generated items) in the
shape that can be fed back as the input of a follow-up agent run.

## What you need to do

Add a public, read-only property `history` to the
`RunState<TContext, TAgent>` class so that consumers can do:

```ts
const state = new RunState(context, 'hello', agent, 1);
// ...run the agent, generated items are pushed onto _generatedItems...
const next = state.history;     //  AgentInputItem[]
```

The property must satisfy these contract requirements:

1. **Type:** `history` is an instance property typed as
   `AgentInputItem[]`.
2. **String input:** when `_originalInput` is a string `s`, the first
   element of `history` must be the message item
   `{ type: 'message', role: 'user', content: s }`. (Subsequent
   elements are the generated items in order — see point 4.)
3. **Array input:** when `_originalInput` is already an array of
   `AgentInputItem`s, those items must appear at the start of
   `history`, in their original order, unchanged.
4. **Generated items:** every entry in `_generatedItems` must be
   appended to `history` in order, **in its raw protocol form** (i.e.
   the underlying `rawItem`, not the wrapper `RunItem`). Tool-approval
   items must NOT be included — they are intermediate scaffolding and
   would otherwise cause double function calls when fed back into a
   subsequent run.
5. **Serialization round-trip:** after
   `RunState.fromString(agent, state.toString())`, the restored
   state's `history` must equal the original state's `history`. (You
   should not need new serialization logic — re-deriving `history`
   from the already-serialized `_originalInput` and `_generatedItems`
   is sufficient.)

The repository already exports a helper that produces exactly the
combined-history shape described above; locate it and reuse it rather
than reimplementing the logic. (Hint: the same merge happens
internally on every turn of `Runner.run`.)

## Where the change belongs

The new property is part of the public API of `RunState`, so it lives
in the source file that defines that class inside
`packages/agents-core/src/`. No changes are required to `runState`'s
serialization format, to `_generatedItems`, or to any other package.

## Code Style Requirements

- TypeScript / ESLint must pass (`pnpm lint` and
  `pnpm -F @openai/agents-core run build-check`).
- Public APIs must have JSDoc comments. Comments must end with a
  period.
- Follow Prettier defaults; do not introduce unused imports.

## Verification

The graded checks are:

- An oracle script that calls `state.history` on several configurations
  (string input, array input, with and without generated items, and
  after a `toString()` / `fromString()` round-trip) and asserts the
  contract above.
- `pnpm -F @openai/agents-core run build-check` (the package's own
  TypeScript compile gate).
- `pnpm lint`.
