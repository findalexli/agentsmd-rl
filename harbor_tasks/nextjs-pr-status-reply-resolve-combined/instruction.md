# Add combined reply-and-resolve command for PR review threads

## Problem

When addressing PR review comments using `scripts/pr-status.js`, you currently need two separate commands to reply and then resolve a thread:

```bash
node scripts/pr-status.js reply-thread <threadId> "Done -- ..."
node scripts/pr-status.js resolve-thread <threadId>
```

This is cumbersome for the common workflow of replying with what was done and immediately resolving.

Additionally, the current `replyToThread()` function uses a GraphQL mutation (`addPullRequestReviewThreadReply`) that can attach replies to a pending/draft review instead of publishing them immediately. Replies should always be published right away.

## Expected Behavior

1. A new `reply-and-resolve-thread` subcommand should combine both actions into a single command:
   ```
   node scripts/pr-status.js reply-and-resolve-thread <threadNodeId> <body>
   ```
   It should validate that both `threadNodeId` and `body` arguments are provided, printing a usage message of the form:
   ```
   Usage: ... reply-and-resolve-thread <threadNodeId> <body>
   ```
   and exiting non-zero if either is missing.

2. The `replyToThread()` function should be refactored to use the REST API for posting replies, which always publishes immediately (never attaches to a pending review). The implementation must use a REST endpoint URL matching the pattern `/pulls/.*/(comments|replies)`. The old GraphQL mutation `addPullRequestReviewThreadReply` must not be called.

3. The `generateThreadMd()` function should include the new combined command in the generated `thread-N.md` files for unresolved threads.

4. The skill documentation files should be updated to document the new command.

## Files to Look At

- `scripts/pr-status.js` — the PR status script containing `replyToThread()`, `resolveThread()`, `generateThreadMd()`, and `main()`
- `.agents/skills/pr-status-triage/SKILL.md` — skill definition with workflow steps and quick commands
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow including the "Resolving Review Threads" section
