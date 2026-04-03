# Remove the `triggerAndPoll()` method from the SDK

## Problem

The `tasks.triggerAndPoll()` function in `@trigger.dev/sdk` has always been discouraged — it blocks the caller until the triggered run completes, which is a serious problem in web request handlers where you'd be tying up a server connection for the entire duration of a background task. The recommended alternative is the Realtime API.

The decision has been made to remove `triggerAndPoll()` entirely rather than continue shipping a function that we actively tell people not to use.

## What needs to happen

1. Remove the `triggerAndPoll` function implementation from the SDK source code.
2. Remove it from the public `tasks` API surface (imports and exports).
3. Clean up any reference usage of `triggerAndPoll` in the codebase.
4. Update the project's documentation and agent instruction files so they no longer mention or recommend `triggerAndPoll`. This includes any docs pages that list available trigger methods, and any AI coding assistant rule files that document how to use the SDK's triggering APIs.

## Files to look at

- `packages/trigger-sdk/src/v3/shared.ts` — where the function is defined
- `packages/trigger-sdk/src/v3/tasks.ts` — where the public `tasks` object is assembled
- `references/v3-catalog/src/trigger/sdkUsage.ts` — example usage in the reference catalog
- `docs/triggering.mdx` — documentation page listing trigger methods
- `.cursor/rules/writing-tasks.mdc` — AI assistant rules for writing Trigger.dev tasks
