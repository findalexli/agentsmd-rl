# Add Figma skills to curated catalog

Source: [openai/skills#9](https://github.com/openai/skills/pull/9)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/.curated/figma-code-connect-components/SKILL.md`
- `skills/.curated/figma-create-design-system-rules/SKILL.md`
- `skills/.curated/figma-implement-design/SKILL.md`

## What to add / change

Adding partner skills provided by Figma into the curated section

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
