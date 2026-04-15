# Simplify poll.sh to auto-resolve session ID

## Problem

The Copilot polling script (`.claude/skills/copilot/poll.sh`) currently requires callers to manually extract the session ID from the `gh agent-task create` output URL and pass it as the first argument. This makes the interface clunky — callers need to parse the URL, extract the trailing UUID, and pass three arguments (`session_id`, `repo`, `pr_number`).

## Expected Behavior

`poll.sh` should accept just two arguments — `repo` (in `owner/repo` format) and `pr_number` — and internally resolve the most recent agent session for that repo and PR. The script must use `gh agent-task list --json` to retrieve session data, filter by `repository` and `pullRequestNumber` fields using jq, sort by `createdAt`, and extract the `id` of the most recent session.

Specifically:
- The script must call `gh agent-task list` with `--json` output containing at least the fields `id`, `repository`, `pullRequestNumber`, and `createdAt`
- The jq filter must select sessions matching the given `repository` and `pullRequestNumber`, sort by `createdAt`, and take the last (most recent)
- The `id` field of the selected session becomes the session ID for polling

The existing polling loop (`while true`) and mark-ready-for-review logic (`gh pr ready`) should remain unchanged.

## Files to Modify

### `.claude/skills/copilot/poll.sh`
- Change the argument interface: the first argument (`$1`) should be assigned to a variable `repo=` and the second argument (`$2`) to a variable `pr_number=` (not `session_id`)
- Remove any `session_id="$1"` assignment
- Add a session resolution block that calls `gh agent-task list`, filters by `repository` and `pullRequestNumber` using jq, sorts by `createdAt`, and extracts the session `id`
- Retain the existing `while true` polling loop and `gh pr ready` calls

### `.claude/skills/copilot/SKILL.md`
- Add `gh agent-task list:*` to the `allowed-tools` list
- Update the polling section to show the simplified 2-argument usage (`poll.sh "<owner>/<repo>" <pr_number>`) without any `session_url` extraction
- The polling section should describe the session resolution as automatic (using words like "automatic" or "auto")
- Remove any `session_url=` or `session_id="${session_url` patterns from the polling documentation
