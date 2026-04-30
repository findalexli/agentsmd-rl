# Add combined reply-and-resolve command to pr-status script

## Problem

The `scripts/pr-status.js` script in this Next.js monorepo manages PR triage workflow. Currently, replying to a review thread and then resolving it requires two separate commands (`reply-thread` then `resolve-thread`). This is tedious — agents typically want to do both at once after addressing feedback.

The current reply-to-thread implementation uses a GraphQL mutation that can attach replies to pending/draft reviews instead of publishing them immediately. When the reply is not published immediately, reviewers may not see it right away.

## Expected Behavior

1. A new `reply-and-resolve-thread` subcommand should be added to `scripts/pr-status.js` that accepts a thread node ID and reply body, and performs both operations. When called with missing arguments it must exit with a non-zero code and print a `Usage:` message to stderr that includes the subcommand name.

2. The reply-to-thread function should be refactored to use a REST API endpoint instead of the old GraphQL mutation. The REST endpoint URL path contains `/comments/` and `/replies`. The implementation needs to look up a field called `databaseId` via a GraphQL query to construct the REST call. After posting, the response includes an `html_url` field that should be logged.

3. The `generateThreadMd()` function output should include a command option labeled exactly "Reply and resolve in one step" that references the `reply-and-resolve-thread` subcommand.

4. The skill documentation files (SKILL.md and workflow.md in `.agents/skills/pr-status-triage/`) should be updated to document the combined command:
   - SKILL.md: add a section with the heading "Thread interaction" (case-sensitive) that includes the `reply-and-resolve-thread` command, and update the workflow step about handling review comments to mention doing both actions in "one step".
   - workflow.md: describe the one-step alternative using the `reply-and-resolve-thread` subcommand and mention "one step".

## Files to Look At

- `scripts/pr-status.js` — the main script; contains `replyToThread()`, `resolveThread()`, `generateThreadMd()`, and the subcommand dispatch in `main()`
- `.agents/skills/pr-status-triage/SKILL.md` — skill definition with workflow steps and quick-command reference
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow including "Resolving Review Threads" section

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
