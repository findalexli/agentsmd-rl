# Replayed computer-tool turns send unsupported empty safety-check fields

You are working in the `openai/openai-agents-js` monorepo at the
`@openai/agents-openai` package, which converts SDK history items back into
OpenAI Responses API input items so a multi-turn conversation can be replayed
to the model.

## The bug

When the SDK replays a `computer_call` (or its matching
`computer_call_result`) that has no outstanding safety checks, the rebuilt
Responses-API input item still carries the safety-check field set to an empty
array. Specifically:

- A rebuilt `computer_call` input item always contains a
  `pending_safety_checks: []` field.
- A rebuilt `computer_call_output` input item (the snake-cased form of
  `computer_call_result`) always contains an
  `acknowledged_safety_checks: []` field.

This happens both when `providerData.pending_safety_checks` /
`providerData.acknowledged_safety_checks` is an empty array, and when the
field is absent from `providerData` entirely — the conversion path
defaults the missing value to `[]` and emits it.

The live OpenAI Responses API rejects these empty arrays for the `computer`
tool, so any follow-up turn after a `computer-use` (or `computer-use-hitl`)
flow fails with:

```
400 pending_safety_checks is not supported for the "computer" tool
```

## What "fixed" looks like

After the fix, when the SDK rebuilds Responses-API input items from history:

- A `computer_call` whose `providerData` has either an empty
  `pending_safety_checks` array **or no `pending_safety_checks` field at
  all** must be rebuilt **without** a `pending_safety_checks` key on the
  resulting object. The key must be **absent**, not present-and-empty.
- A `computer_call_result` whose `providerData` has either an empty
  `acknowledged_safety_checks` array **or no `acknowledged_safety_checks`
  field at all** must be rebuilt as a `computer_call_output` **without** an
  `acknowledged_safety_checks` key on the resulting object.

The non-empty path must continue to work unchanged — when
`providerData.pending_safety_checks` is a non-empty array such as
`[{ id: 'check-1', code: 'confirm', ... }]`, the rebuilt `computer_call`
must still carry that exact array on `pending_safety_checks`. The same
preservation requirement applies to `acknowledged_safety_checks` on the
`computer_call_output` form.

The other identifying fields on the rebuilt items (`type`, `id`, `call_id`,
the action payload, the output payload) must be unchanged.

## Scope

The conversion lives inside the `@openai/agents-openai` package. The only
function that needs to change is the one that turns SDK history items into
Responses-API input items (`getInputItems`). Other replay paths (messages,
reasoning items, function tool calls, shell tool calls, tool-search items,
batched computer actions with non-empty safety checks) must not be
affected.

## Verification

Run the package's existing unit tests; the helpers test file already
covers the non-empty-safety-check replay path and the broader
`getInputItems` contract. Add coverage for the empty-safety-check case
described above so the regression cannot reappear silently.

The change touches a published package, so it must be accompanied by a
Changeset entry that names `@openai/agents-openai` at a `patch` bump and
whose summary reads like a Conventional Commit subject (for example,
starting with `fix:`).

## Code Style Requirements

- ESLint must continue to pass for the package — run `pnpm exec eslint
  packages/agents-openai/src packages/agents-openai/test`.
- TypeScript must still type-check — run
  `pnpm -F @openai/agents-openai build-check`.
- Any comment you add or modify in TypeScript source must end with a
  period (per `AGENTS.md`).
