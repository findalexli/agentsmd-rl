# Fix poll.sh to poll by session ID instead of timeline events

## Problem

`.claude/skills/copilot/poll.sh` currently checks for any `copilot_work_finished` event in the PR timeline to determine when Copilot has finished. This breaks when multiple Copilot sessions exist on the same PR — the script finds a stale `copilot_work_finished` event from a prior session and exits immediately, missing the current session.

## Expected Behavior

`poll.sh` should poll a specific Copilot session by its session ID rather than scanning timeline events. The script must:

1. Accept a session ID as its first argument (`$1`)
2. Use `gh agent-task view` to check the session's state
3. Loop while the state is `queued` or `in_progress`, exiting on any other state (e.g., `completed`, `failed`)
4. NOT call the timeline API (`repos/{owner}/{repo}/issues/{pr_number}/timeline`)

The session ID is obtained from `gh agent-task create` output — it appears in the returned URL after the last `/`.

After fixing the code, update the relevant skill documentation to reflect the new calling convention and any additional tool permissions needed.

## Files to Look At

- `.claude/skills/copilot/poll.sh` — the polling script that needs to be rewritten
- `.claude/skills/copilot/SKILL.md` — the skill instructions that document how to invoke `poll.sh`

## Code Quality Requirements

Both files must meet these standards (these are checked by tests):

- **poll.sh** must:
  - Have shebang `#!/usr/bin/env bash` as the first line
  - Be executable (has executable bit set)
  - Pass shellcheck linting
  - Have no trailing whitespace
  - Have no tab characters

- **SKILL.md** must:
  - Have valid YAML frontmatter (lines 1-3 must be `---`, key-value pairs, then `---`)
  - Contain required fields: `name:`, `description:`, `allowed-tools:`
  - Have no trailing whitespace
  - Have no tab characters

## SKILL.md Documentation Requirements

The SKILL.md must be updated to:

1. Add `gh agent-task view` to the `allowed-tools` list (e.g., `- Bash(gh agent-task view:*)`)
2. Document the new calling convention: `poll.sh <session_id> <owner>/<repo> <pr_number>`
3. Show how to extract the session ID from `gh agent-task create` output
