# Simplify poll.sh to auto-resolve session ID

## Problem

The Copilot polling script (`.claude/skills/copilot/poll.sh`) currently requires three arguments: a session ID, a repository identifier, and a PR number. Callers must manually extract the session ID from the URL returned by `gh agent-task create`, making the interface unnecessarily complex.

## Expected Behavior

Simplify `poll.sh` to accept only two arguments — the repository (in `owner/repo` format) and the PR number — and have the script automatically resolve the correct session ID internally.

To resolve the session, the script should query available sessions using `gh agent-task list` with JSON output. The `gh agent-task list` API returns objects with fields including `id`, `repository`, `pullRequestNumber`, and `createdAt`. The script should filter sessions for the matching repository and PR number, then select the most recently created session for polling.

The existing polling loop (`while true`, `gh agent-task view`, `gh pr ready`) must be preserved.

## Skill Configuration Update

The skill definition file (`.claude/skills/copilot/SKILL.md`) also needs to be updated:

- The `allowed-tools` list must permit `gh agent-task list` commands so the script can query sessions
- The polling documentation section should be simplified to reflect the new 2-argument interface, removing any `session_url` extraction boilerplate
- The documentation should describe the session resolution as automatic
