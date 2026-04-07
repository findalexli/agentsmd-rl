# Add completion polling to the Copilot skill

## Problem

The `/copilot` skill (`.claude/skills/copilot/`) creates a GitHub Copilot agent task and prints session/PR URLs, but there is no way to detect when Copilot has finished its work. After handing off a task, the user must manually check GitHub to see if Copilot completed.

## Expected Behavior

The skill should include a polling mechanism that automatically detects when Copilot finishes working on a PR. This requires:

1. A shell script that polls the GitHub Issues Timeline API for the completion event, with a reasonable timeout
2. The skill definition updated to allow running the polling script and to document how to use it

After implementing the polling script, update the skill's configuration and documentation to reflect the new capability.

## Files to Look At

- `.claude/skills/copilot/SKILL.md` — the skill definition file (frontmatter + usage docs)
- `.claude/skills/copilot/` — directory where skill assets live
