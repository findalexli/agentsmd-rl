# Add combined reply-and-resolve command to pr-status script

## Problem

The `scripts/pr-status.js` script in this Next.js monorepo manages PR triage workflow. Currently, replying to a review thread and then resolving it requires two separate commands (`reply-thread` then `resolve-thread`). This is tedious — agents typically want to do both at once after addressing feedback.

The current `replyToThread()` function uses a GraphQL mutation (`addPullRequestReviewThreadReply`) that can attach replies to pending/draft reviews instead of publishing them immediately. The REST API endpoint for replies always publishes immediately, so it should be preferred. Note: the REST endpoint requires looking up both the PR number and a comment's `databaseId` from the thread node ID via a GraphQL query first.

## Expected Behavior

1. A new `reply-and-resolve-thread` subcommand should be added that accepts a thread node ID and reply body, calls `replyToThread()` then `resolveThread()` in sequence. When called with missing arguments it must print a non-zero exit code and a `Usage:` message that includes the subcommand name.
2. The `replyToThread()` function should be refactored to use the REST API (`/repos/{owner}/{repo}/pulls/{pr}/comments/{commentId}/replies`) instead of the GraphQL `addPullRequestReviewThreadReply` mutation. It needs to look up the PR number and `databaseId` of the first comment in the thread via a GraphQL query, then POST to the REST replies endpoint. The REST response contains an `html_url` field that should be logged.
3. The `generateThreadMd()` function should include a combined command option labeled "Reply and resolve in one step" that references the `reply-and-resolve-thread` subcommand.
4. The agent skill documentation files (SKILL.md and workflow.md in `.agents/skills/pr-status-triage/`) should be updated:
   - SKILL.md: add a "Thread interaction" section with commands including `reply-and-resolve-thread`, and update step 6 to mention doing both actions in one step.
   - workflow.md: describe the one-step `reply-and-resolve-thread` alternative.

## Files to Look At

- `scripts/pr-status.js` — the main script; contains `replyToThread()`, `resolveThread()`, `generateThreadMd()`, and the subcommand dispatch in `main()`
- `.agents/skills/pr-status-triage/SKILL.md` — skill definition with workflow steps and quick-command reference
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow including "Resolving Review Threads" section
