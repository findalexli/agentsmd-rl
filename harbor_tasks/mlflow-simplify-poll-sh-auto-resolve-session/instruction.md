# Simplify poll.sh to auto-resolve session ID

## Problem

The Copilot polling script (`.claude/skills/copilot/poll.sh`) currently requires callers to manually extract the session ID from the `gh agent-task create` output URL and pass it as the first argument. This makes the interface clunky — callers need to parse the URL, extract the trailing UUID, and pass three arguments (`session_id`, `repo`, `pr_number`).

## Expected Behavior

`poll.sh` should accept just two arguments — `repo` (in `owner/repo` format) and `pr_number` — and internally resolve the most recent agent session for that repo and PR. The `gh agent-task list` command can be used to query sessions and filter by repository and PR number client-side (since `--repo` isn't supported). Take the most recent session by `createdAt`.

The existing polling loop and mark-ready-for-review logic should remain unchanged.

## Files to Look At

- `.claude/skills/copilot/poll.sh` — the polling script that needs its interface simplified
- `.claude/skills/copilot/SKILL.md` — the skill documentation that describes how to use poll.sh; update it to reflect the new simpler interface and ensure the `allowed-tools` list covers any new CLI commands used
