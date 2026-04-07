# Fix poll.sh to poll by session ID instead of timeline events

## Problem

`.claude/skills/copilot/poll.sh` checks for any `copilot_work_finished` event in the PR timeline to determine when Copilot has finished. This breaks when multiple Copilot sessions exist on the same PR — the script finds a stale `copilot_work_finished` event from a prior session and exits immediately, missing the current session.

## Expected Behavior

`poll.sh` should poll a specific Copilot session by its session ID (obtained from `gh agent-task create` output) rather than scanning all timeline events. The script should use `gh agent-task view` to check the session's state and loop while it is still active (`queued` or `in_progress`), exiting on any terminal state.

After fixing the code, update the relevant skill documentation to reflect the new calling convention and any additional tool permissions needed.

## Files to Look At

- `.claude/skills/copilot/poll.sh` — the polling script that needs to be rewritten to accept and use a session ID
- `.claude/skills/copilot/SKILL.md` — the skill instructions that document how to invoke `poll.sh`; must be updated to reflect the new calling convention and any new tool permissions needed
