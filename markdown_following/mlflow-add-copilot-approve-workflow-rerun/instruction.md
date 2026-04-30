# Add workflow approval script for Copilot PRs

## Problem

The GitHub `/approve` API (`POST /actions/runs/{id}/approve`) does not work for same-repo Copilot PRs — it returns a 403 error with "not a fork pull request." This means `action_required` workflow runs triggered by Copilot cannot be approved through the standard API.

However, the `/rerun` API (`POST /actions/runs/{id}/rerun`) works as a workaround — it re-triggers the workflow runs under the caller's permissions.

## What needs to be done

Create a shell script at `.claude/skills/copilot/approve.sh` that:

1. Takes a repository (`owner/repo`) and a PR number as arguments
2. Finds all `action_required` workflow runs for the PR's HEAD SHA that were triggered by the Copilot actor
3. Reruns each matching workflow using the GitHub API
4. Handles the case where no matching runs exist gracefully (the script must detect when no matching runs were found and exit with code 0, not an error)
5. Logs success or failure per run without aborting on individual failures

The script should use `gh` CLI for all GitHub API interactions and follow the same patterns as the existing `poll.sh` in the same directory.

**Empty-results handling**: When no matching `action_required` runs exist for the PR's HEAD SHA, the script must exit cleanly with code 0. Implement this by checking whether any matching run IDs were collected (e.g., using a shell empty-string test on the collected IDs) and printing an informational message such as "No action_required" or similar before exiting.

After creating the script, update the copilot skill instructions (`.claude/skills/copilot/SKILL.md`) to:
- Add the new script to the skill's `allowed-tools` frontmatter section
- Document how and when to use it

## Files to look at

- `.claude/skills/copilot/poll.sh` — existing script to follow as a pattern
- `.claude/skills/copilot/SKILL.md` — skill definition that needs updating

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff` (lint and format check)
- `typos (spell-check)`
