# Add combined reply-and-resolve command to pr-status script

## Problem

The `scripts/pr-status.js` script in this Next.js monorepo manages PR triage workflow. Currently, replying to a review thread and then resolving it requires two separate commands (`reply-thread` then `resolve-thread`). This is tedious — agents typically want to do both at once after addressing feedback.

Additionally, the `replyToThread()` function has a subtle bug: it uses a GraphQL mutation (`addPullRequestReviewThreadReply`) that can attach replies to pending/draft reviews instead of publishing them immediately. The REST API endpoint for replies always publishes immediately, so it should be preferred.

## Expected Behavior

1. A new `reply-and-resolve-thread` subcommand should be added that accepts a thread node ID and reply body, calls reply then resolve in sequence.
2. The `replyToThread()` function should be refactored to use the REST API instead of the GraphQL mutation — it needs to look up the PR number and comment database ID from the thread node ID, then POST to the REST replies endpoint.
3. The `generateThreadMd()` function should include the combined command in generated thread files.
4. The agent skill documentation files (SKILL.md and workflow.md in `.agents/skills/pr-status-triage/`) should be updated to document the new command and the one-step workflow.

## Files to Look At

- `scripts/pr-status.js` — the main script; contains `replyToThread()`, `resolveThread()`, `generateThreadMd()`, and the subcommand dispatch in `main()`
- `.agents/skills/pr-status-triage/SKILL.md` — skill definition with workflow steps and quick-command reference
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow including "Resolving Review Threads" section
