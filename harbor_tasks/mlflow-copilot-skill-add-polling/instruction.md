# Add completion polling to the Copilot skill

## Problem

The `/copilot` skill (`.claude/skills/copilot/`) creates a GitHub Copilot agent task and prints session/PR URLs, but there is no way to detect when Copilot has finished its work. After handing off a task, the user must manually check GitHub to see if Copilot completed.

## Expected Behavior

The skill should include a polling mechanism that automatically detects when Copilot finishes working on a PR. Concretely:

1. **A shell script** at `.claude/skills/copilot/poll.sh` that:
   - Is executable and passes `bash -n` syntax validation
   - Takes two arguments: `{owner}/{repo}` (e.g., `mlflow/mlflow`) and a PR number
   - Exits non-zero when invoked without the required arguments
   - Polls the GitHub Issues **Timeline API** (the word `timeline` must appear in the script) to check for the `copilot_work_finished` event in the timeline response
   - Has a timeout of `1800` seconds (30 minutes); use a variable named `max_seconds` to hold this value

2. **The SKILL.md frontmatter** updated to:
   - Add `poll.sh` to the `allowed-tools` list so the skill can invoke it
   - The frontmatter must remain valid YAML with `name` and `allowed-tools` fields

3. **The SKILL.md body** updated to:
   - Add a section about polling (the word "polling" should appear in the content)
   - Reference `poll.sh` with usage instructions in this section

## Existing `.claude` directory structure

The repository already has a `.claude` directory with the following files. Your changes must not break any of these:

- `.claude/settings.json` — must remain valid JSON
- `.claude/statusline.sh` — must remain executable and pass `bash -n`
- `.claude/hooks/enforce-uv.sh` — must remain executable and pass `bash -n`
- `.claude/hooks/lint.py` — must have valid Python syntax
- `.claude/hooks/validate_pr_body.py` — must have valid Python syntax
- `.claude/skills/copilot/SKILL.md` — must retain valid YAML frontmatter with `name` and `allowed-tools` fields

## Files to Modify

- `.claude/skills/copilot/SKILL.md` — update frontmatter and add polling documentation
- `.claude/skills/copilot/poll.sh` — new script to create
