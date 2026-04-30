# Prune orphan hosted shell calls from public history

You are working in the `openai/openai-agents-js` monorepo (a pnpm workspace).
The working directory is `/workspace/openai-agents-js`. The package of interest
is `@openai/agents-core` under `packages/agents-core/`.

## The bug

`@openai/agents-core` has two functions that assemble the input array for a
turn:

- An internal helper that constructs the model input for the *current* turn,
  combining the original input with newly generated run items. This helper
  already filters out **orphan tool calls** (a hosted-shell `shell_call`
  whose `shell_call_output` companion never came back from the model).
- `getTurnInput()`, which is also used to build the *public-facing* history —
  what `RunResult.history` and `RunState.history` expose to library users,
  and what feeds into follow-up runs that continue the conversation. This
  function does **not** apply the orphan-tool-call filter.

The asymmetry creates a continuation-history gap: when a user kicks off a
new run by passing `firstResult.history` (or `firstResult.state.history`)
back into the runner, an orphan hosted `shell_call` from the previous run
gets re-sent to the model. The Responses API rejects orphan tool calls, so
this corrupts the next turn.

The fix should make the public-history path go through the same orphan-call
pruning as the internal turn-input path, so that:

1. `getTurnInput(originalInput, generatedItems)` — when `generatedItems`
   contains a `RunToolCallItem` of type `shell_call` with no matching
   `shell_call_output` — must return only the original input. The orphan
   shell call must NOT appear in the result.

2. `RunState.history` — when `_generatedItems` contains an orphan
   `shell_call` — must NOT include the orphan shell call. It should still
   include the original-input message.

3. End-to-end: after `await runner.run(agent, 'user_message')` produces a
   `RunResult` whose first turn emitted an orphan hosted `shell_call`,
   neither `result.history` nor `result.state.history` may contain a
   `shell_call` item. Following up with `await runner.run(agent,
   result.history)` or `await runner.run(agent, result.state.history)` must
   send the model an input array that contains no `shell_call` items, and
   the input array sent to the model must be deeply equal to the
   corresponding history array.

A "hosted shell call" here is a `protocol.ShellCallItem`:

```ts
{
  type: 'shell_call',
  callId: string,
  status: 'completed' | 'in_progress',  // or undefined
  action: { commands: string[] },
}
```

A `shell_call` is **orphan** when no companion `shell_call_output` item
shares its `callId` in the same items array. Pending shell calls (status
`'in_progress'` or `undefined`) are NOT orphans — they should be preserved
so the runtime can resume them on the next turn.

## What you are expected to change

You should reuse the existing orphan-pruning logic already wired into the
internal current-turn input path so the public-history path applies the
same filter. Where exactly to factor the shared helper, and how to name it,
are up to you, but the structure of the pruning logic itself does not need
to change.

Add a changeset under `.changeset/` that describes this as a `patch` to
`@openai/agents-core` with a Conventional-Commit-style summary line
(for example, `fix: prune orphan hosted shell calls from public history`).

## Code Style Requirements

This repo's verification stack runs on every code change:

- `pnpm lint` (ESLint) must pass on touched files. The repo follows
  `eslint.config.mjs` and Prettier defaults — keep your formatting
  consistent with the surrounding code.
- `pnpm -F @openai/agents-core build-check` (TypeScript `tsc --noEmit`)
  must pass.
- Per `AGENTS.md`: comments must end with a period.

## Verifying your work

You can run the unit tests for this package directly:

```bash
pnpm -F @openai/agents-core exec vitest run test/run.utils.test.ts
pnpm -F @openai/agents-core exec vitest run test/runState.test.ts
```

Both should remain green. The full verification stack from `AGENTS.md` is:

```bash
pnpm i
pnpm build
pnpm -r build-check
pnpm lint
CI=1 pnpm test
```
