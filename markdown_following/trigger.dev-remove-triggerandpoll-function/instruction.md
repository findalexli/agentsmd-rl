# Remove the `triggerAndPoll()` API

## Problem

The `tasks.triggerAndPoll()` function in the SDK is a bad pattern — it blocks by polling until a run completes, which is especially problematic inside web request handlers. It has always carried warnings against its use, and the recommended approach is to use Realtime subscriptions or `runs.poll()` directly instead.

This function needs to be fully removed from the codebase: the implementation, its export, any reference usage, and all documentation that describes it.

## Expected Behavior

- `tasks.triggerAndPoll()` should no longer exist as a function in the SDK
- The `tasks` export object should not include `triggerAndPoll`
- No reference/example code should call `triggerAndPoll`
- All documentation and agent instruction files that describe `triggerAndPoll` should be updated to remove references to it
- Other SDK methods (`trigger`, `batchTrigger`, `triggerAndWait`, etc.) must remain intact

## Files to Look At

- `packages/trigger-sdk/src/v3/shared.ts` — contains the `triggerAndPoll` function implementation
- `packages/trigger-sdk/src/v3/tasks.ts` — exports the `tasks` object with all available methods
- `references/v3-catalog/src/trigger/sdkUsage.ts` — example/reference code that uses SDK methods
- `.cursor/rules/writing-tasks.mdc` — agent instructions for writing tasks, documents available SDK methods
- `docs/triggering.mdx` — public documentation for triggering tasks

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
