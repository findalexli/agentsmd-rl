# Add workflow approval script for Copilot PRs

## Problem

The GitHub `/approve` API (`POST /actions/runs/{id}/approve`) does not work for same-repo Copilot PRs — it returns a 403 error with "not a fork pull request." This means `action_required` workflow runs triggered by Copilot cannot be approved through the standard API.

However, the `/rerun` API (`POST /actions/runs/{id}/rerun`) works as a workaround — it re-triggers the workflow runs under the caller's permissions.

## What needs to be done

Create a shell script at `.claude/skills/copilot/approve.sh` that:

1. Takes a repository (`owner/repo`) and a PR number as arguments
2. Finds all `action_required` workflow runs for the PR's HEAD SHA that were triggered by the Copilot actor
3. Reruns each matching workflow using the GitHub API
4. Handles the case where no matching runs exist gracefully
5. Logs success or failure per run without aborting on individual failures

The script should use `gh` CLI for all GitHub API interactions and follow the same patterns as the existing `poll.sh` in the same directory.

After creating the script, update the copilot skill instructions (`.claude/skills/copilot/SKILL.md`) to:
- Add the new script to the skill's allowed tools
- Document how and when to use it

## Files to look at

- `.claude/skills/copilot/poll.sh` — existing script to follow as a pattern
- `.claude/skills/copilot/SKILL.md` — skill definition that needs updating
