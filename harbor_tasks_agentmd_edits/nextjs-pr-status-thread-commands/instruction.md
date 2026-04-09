# Add reply-thread and resolve-thread subcommands to pr-status script

## Problem

The `scripts/pr-status.js` script generates `thread-N.md` files that summarize PR review threads, but there is no way for an agent to reply to or resolve those threads from the pr-status workflow. After addressing review feedback, the agent has no built-in mechanism to close the loop — it would need to manually construct `gh api graphql` calls with the correct mutation and node IDs.

## Expected Behavior

The pr-status script should support two new subcommands:

- `reply-thread <threadNodeId> <body>` — posts a reply to a PR review thread
- `resolve-thread <threadNodeId>` — marks a review thread as resolved

Both subcommands should validate their arguments and print a usage message if required arguments are missing. They should use `execFileSync` with argument arrays (not shell strings) to safely pass the body to `gh api graphql` without shell escaping issues.

The generated `thread-N.md` files should include a `## Commands` section at the bottom with ready-to-use commands pre-populated with the correct GraphQL node IDs (for reply and, if unresolved, resolve). This requires fetching the thread `id` from the GraphQL API.

After making the code changes, update the pr-status-triage skill documentation to reflect the new workflow. The skill's rules and workflow docs should guide agents to reply to threads with a description of actions taken before resolving them.

## Files to Look At

- `scripts/pr-status.js` — the main script to add subcommands and Commands section generation
- `.agents/skills/pr-status-triage/SKILL.md` — skill rules (add thread resolution guidance)
- `.agents/skills/pr-status-triage/workflow.md` — detailed workflow docs (add resolving threads section)
