# Remove Figma skills

Source: [openai/skills#18](https://github.com/openai/skills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/.curated/figma-code-connect-components/SKILL.md`
- `skills/.curated/figma-create-design-system-rules/SKILL.md`
- `skills/.curated/figma-implement-design/SKILL.md`

## What to add / change

- Until we have licenses for them.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
