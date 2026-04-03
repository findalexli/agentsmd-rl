# Remove Progress Service and Add Fork Deduplication

The chat fork action in VS Code (`src/vs/workbench/contrib/chat/browser/actions/chatForkActions.ts`) has two issues:

1. **Unnecessary IProgressService dependency**: The `forkContributedChatSession` function takes an `IProgressService` parameter but doesn't actually use it for progress reporting. This adds an unnecessary service dependency.

2. **No deduplication for concurrent forks**: If a user triggers the fork action multiple times quickly (e.g., double-clicking), multiple concurrent fork operations are started for the same session and request. This can lead to duplicate forked sessions.

Fix both issues by:
- Removing the `IProgressService` import and parameter
- Moving `forkContributedChatSession` call into a method on the action class
- Adding a `pendingFork` Map to deduplicate concurrent fork operations by session+request key
- Cleaning up the map entry after the fork completes (in a finally block)
