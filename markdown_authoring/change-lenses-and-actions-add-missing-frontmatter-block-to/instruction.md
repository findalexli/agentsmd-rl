# Add missing frontmatter block to SKILL.md

Source: [johnpcutler/change-lenses-and-actions#1](https://github.com/johnpcutler/change-lenses-and-actions/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

SKILL.md lacked the required YAML frontmatter that Claude Code uses to register a file as a skill. Without it, the skill name and description were undefined, preventing Claude Code from identifying when to activate the diagnostic or exposing it as a slash command.

Added frontmatter with name (com-b-diagnostic) and a description that includes the activation conditions already documented in the file body.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
