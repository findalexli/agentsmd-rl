# Add reply-thread and resolve-thread subcommands to pr-status.js

## Problem

The `scripts/pr-status.js` tool helps agents check PR status and review feedback, but it lacks the ability to interact with review threads. When an agent addresses review feedback, there's no programmatic way to:
1. Reply to a review thread describing what actions were taken
2. Mark a review thread as resolved

Currently, agents would need to manually construct `gh api graphql` calls, which is error-prone and requires knowledge of GraphQL mutations.

## Expected Behavior

Add two new subcommands to `scripts/pr-status.js`:

1. `reply-thread <threadNodeId> <body>` - Posts a reply to a PR review thread using the `addPullRequestReviewThreadReply` GraphQL mutation with `pullRequestReviewThreadId` parameter

2. `resolve-thread <threadNodeId>` - Marks a review thread as resolved using the `resolveReviewThread` GraphQL mutation with `threadId` parameter (note: NOT `pullRequestReviewThreadId` - this was fixed in a follow-up commit)

Key requirements:
- Use `execFileSync` (not `execSync`) to safely pass arguments without shell escaping issues
- The subcommands should be dispatched before the existing PR-number behavior in `main()`
- Thread markdown files (`thread-N.md`) should include a `## Commands` section with ready-to-use commands populated with the correct GraphQL node IDs
- The resolve command should only be shown for threads that are not yet resolved

Also update the agent documentation:
- `.agents/skills/pr-status-triage/SKILL.md` - Add guidance about resolving review threads
- `.agents/skills/pr-status-triage/workflow.md` - Add a "Resolving Review Threads" section with detailed steps

## Files to Look At

- `scripts/pr-status.js` - Main file to modify (add subcommand dispatch, `replyToThread()` and `resolveThread()` functions)
- `.agents/skills/pr-status-triage/SKILL.md` - Update with review thread workflow guidance
- `.agents/skills/pr-status-triage/workflow.md` - Add Resolving Review Threads section

## Base Commit

Start from commit `c300a63cc9e0b9eeea6632f0b2150114de8c5d23` on the canary branch.
