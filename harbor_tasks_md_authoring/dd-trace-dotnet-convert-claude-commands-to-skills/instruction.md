# Convert Claude commands to skills format

Source: [DataDog/dd-trace-dotnet#8158](https://github.com/DataDog/dd-trace-dotnet/pull/8158)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/analyze-crash/SKILL.md`
- `.claude/skills/analyze-error/SKILL.md`
- `.claude/skills/review-pr/SKILL.md`

## What to add / change

## Summary of changes

Migrated Claude Code commands from the legacy `.claude/commands/*.md` format to the new `.claude/skills/*/SKILL.md` structure:

- `analyze-crash`: Stack trace crash analysis tool
- `analyze-error`: Error stack trace analysis with actionability assessment
- `review-pr`: GitHub PR review automation

## Reason for change

Claude Code has introduced a new skills format that provides enhanced capabilities. The old command format still works but is deprecated in favor of skills.

## Implementation details

For each command:
1. Created `.claude/skills/{skill-name}/SKILL.md` with YAML frontmatter
2. Added appropriate frontmatter fields:
   - `disable-model-invocation: true` - These are manual workflows
   - `context: fork` + `agent: general-purpose` - Run in isolated subagent
   - `allowed-tools` (review-pr only) - Restrict to specific gh commands
3. Deleted original `.claude/commands/*.md` files

The skill content remains identical to the original commands.

## Test coverage

They show up as slash commands in Claude Code, and are listed under `/skills`, so :shipit: 

## Other details

These are developer productivity tools for the `dd-trace-dotnet` maintainers and do not affect the tracer runtime or customer-facing functionality.

References:
- https://code.claude.com/docs/en/skills
- https://agentskills.io/specification

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
