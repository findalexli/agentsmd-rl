# Fix formatting of description in SKILL.md

Source: [yizhiyanhua-ai/fireworks-tech-graph#4](https://github.com/yizhiyanhua-ai/fireworks-tech-graph/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

fix pi load skills failed:

[Skill conflicts]
  ~/.agents/skills/fireworks-tech-graph/SKILL.md
    Nested mappings are not allowed in compact mappings at line 2, column 14:

description: Use when the user wants to create any technical diagram — architec…

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
