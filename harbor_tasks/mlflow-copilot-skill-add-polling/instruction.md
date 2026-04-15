# Add completion polling to the Copilot skill

## Problem

The `/copilot` skill (`.claude/skills/copilot/`) creates a GitHub Copilot agent task and prints session/PR URLs, but there is no way to detect when Copilot has finished its work. After handing off a task, the user must manually check GitHub to see if Copilot completed.

## Expected Behavior

The skill should include a polling mechanism that automatically detects when Copilot finishes working on a PR. Concretely:

1. **A shell script** at `.claude/skills/copilot/poll.sh` that:
   - Is executable
   - Takes two arguments: `{owner}/{repo}` (e.g., `mlflow/mlflow`) and a PR number
   - Polls the GitHub Issues **Timeline API** endpoint (`repos/{owner}/{repo}/issues/{pr_number}/timeline`)
   - Looks for the **copilot_work_finished** event in the timeline response
   - Has a timeout mechanism (e.g., a variable or value representing approximately 30 minutes / 1800 seconds)
   - Exits non-zero when invoked without arguments

2. **The SKILL.md frontmatter** updated to:
   - Add `poll.sh` to the `allowed-tools` list
   - Document how to run the polling script

## Files to Look At

- `.claude/skills/copilot/SKILL.md` — the skill definition file (frontmatter + usage docs)
- `.claude/skills/copilot/` — directory where skill assets live
