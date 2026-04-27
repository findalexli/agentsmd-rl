# Add researchclaw skill metadata

Source: [aiming-lab/AutoResearchClaw#207](https://github.com/aiming-lab/AutoResearchClaw/pull/207)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/researchclaw/SKILL.md`

## What to add / change

Skill metadata was missing in `.claude/skills/researchclaw/SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
