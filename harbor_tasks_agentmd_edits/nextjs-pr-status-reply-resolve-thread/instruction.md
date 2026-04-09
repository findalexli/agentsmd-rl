# Add combined reply-and-resolve command to PR status script

## Problem

When using `scripts/pr-status.js` to triage PR review threads, the workflow requires two separate commands to reply to and then resolve a thread. This is repetitive — after addressing a review comment, you typically want to reply with what was done and immediately resolve the thread.

The `replyToThread` function in the script also uses a GraphQL mutation that can result in replies being silently attached to a pending/draft review instead of being published immediately. This causes confusion when triaging PRs.

## Expected Behavior

1. `scripts/pr-status.js` should support a `reply-and-resolve-thread` subcommand that combines replying and resolving into a single invocation, calling the existing `replyToThread()` and `resolveThread()` functions in sequence.

2. The `replyToThread` function should be refactored to use the GitHub REST API instead of a GraphQL mutation, so replies are always published immediately.

3. The generated `thread-N.md` files (produced by `generateThreadMd`) should include the combined command alongside the existing separate commands.

4. The agent skill documentation (`.agents/skills/pr-status-triage/`) should be updated to document the new combined command.

## Files to Look At

- `scripts/pr-status.js` — main CLI script; `replyToThread()`, `resolveThread()`, `generateThreadMd()`, and `main()` all need changes
- `.agents/skills/pr-status-triage/SKILL.md` — skill documentation with workflow steps and quick-command reference
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow for resolving review threads
