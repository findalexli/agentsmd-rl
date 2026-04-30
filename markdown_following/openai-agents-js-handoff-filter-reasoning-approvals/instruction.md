# Fix `removeAllTools()` so handoff filtering also drops reasoning and approval placeholders

## Context

You are working in the [`openai/openai-agents-js`](https://github.com/openai/openai-agents-js) monorepo. The `@openai/agents-core` package exposes a helper called `removeAllTools()` (a *handoff input filter*) that is intended to scrub tool-related state out of an agent run before the conversation is handed off to another agent. Callers opt in to this filter when they explicitly do **not** want the next agent to see tool calls, tool outputs, or other tool-related artifacts from the previous agent's turns.

`removeAllTools()` operates over a `HandoffInputData` value, which has three buckets:

- `inputHistory` — either the raw input string or an array of `AgentInputItem` objects, each tagged with a `type` field.
- `preHandoffItems` — `RunItem[]` produced before the handoff was triggered.
- `newItems` — `RunItem[]` produced during the handoff turn.

Today the filter strips entries whose `type` is one of the recognized tool types (function calls, computer/shell/apply-patch calls and their outputs, hosted tool calls, and tool-search items) and `RunItem` instances of `RunHandoffCallItem` / `RunHandoffOutputItem` / `RunToolSearchCallItem` / `RunToolSearchOutputItem` / `RunToolCallItem` / `RunToolCallOutputItem`.

## The bug

Two important shapes leak through the filter even when the caller explicitly opted into "remove all tools":

1. **Reasoning traces.** `AgentInputItem`s with `type: 'reasoning'` (the JS runtime's representation of a model's hidden chain-of-thought) survive in `inputHistory`, and their `RunItem` counterparts survive in `preHandoffItems` / `newItems`. A handoff is supposed to give the receiving agent a clean slate; forwarding stale reasoning traces from the previous agent both wastes tokens and can mislead the next agent.

2. **Pending tool-approval placeholders.** When the runtime produces a hosted-MCP "approval request" placeholder, it is wrapped in the run-item class that represents *pending* approvals (rather than the existing `RunToolCallItem` family). Those placeholders are also tool-related state — they are still waiting on the human/runtime to decide whether the underlying tool call should run — so they should not be carried into the next agent's context when "remove all tools" is requested.

After the fix, calling `removeAllTools()` on a `HandoffInputData` that contains:

- a `type: 'reasoning'` entry inside `inputHistory`, OR
- a run-item representing a reasoning trace inside `preHandoffItems` / `newItems`, OR
- a run-item representing a pending tool-approval placeholder inside `preHandoffItems` / `newItems`,

…must return an output where every such entry has been removed, while every non-tool, non-reasoning, non-approval entry (e.g. plain user/assistant messages) is preserved unchanged. Existing behavior for tool-call and handoff items must continue to work as before.

## Where to look

- The filter lives in `packages/agents-core/src/extensions/handoffFilters.ts`.
- The run-item classes live in `packages/agents-core/src/items.ts`. Look at the exported `RunItem*` classes to identify the ones that wrap reasoning items and pending tool-approval placeholders. They are already exported from that module — you do not need to add new types, only to use them.
- The protocol-level item shape for reasoning entries uses `type: 'reasoning'` in `packages/agents-core/src/types/protocol.ts` (the same `type` literal you already see for the existing tool types in the filter).

## What to change

Update `removeAllTools()` (and any helpers it delegates to inside the same file) so that:

1. Array-form `inputHistory` no longer contains entries whose `type` is `'reasoning'`.
2. The `RunItem[]` filtering helper additionally excludes the run-item class that wraps reasoning traces, and the run-item class that wraps pending tool-approval placeholders.

Do **not** change the public signature of `removeAllTools`, the `HandoffInputData` type, or any of the run-item classes. Do not delete or rename existing filter cases — extend them.

## Constraints

- Confine your code changes to `packages/agents-core/src/extensions/handoffFilters.ts`. You may add tests, but you do not need to.
- All existing unit tests in `packages/agents-core/test/extensions/handoffFilters.test.ts` must still pass.
- The package must still type-check (`pnpm -F @openai/agents-core build-check`).

## Code Style Requirements

This repository's `AGENTS.md` requires the following for any code change:

- Code must conform to the project's ESLint and Prettier configuration. The TypeScript files you edit will be type-checked via `tsc --noEmit -p ./tsconfig.test.json` (`pnpm -F @openai/agents-core build-check`); the build-check must pass.
- Comments, when present, must end with a period.
- Do not manually hard-wrap prose in Markdown/MDX files.

## How your work is verified

Automated tests will:

1. Construct `HandoffInputData` values that contain a reasoning input entry, a `RunItem` reasoning trace, and a `RunItem` pending tool-approval placeholder, then call `removeAllTools()` and assert that all three are removed while plain message items survive.
2. Re-run the existing `packages/agents-core/test/extensions/handoffFilters.test.ts` suite to confirm no regression in the originally covered behavior.
3. Run `pnpm -F @openai/agents-core build-check` to confirm the package still type-checks.
