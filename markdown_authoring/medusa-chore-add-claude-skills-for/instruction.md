# chore: add claude skills for docs

Source: [medusajs/medusa#14533](https://github.com/medusajs/medusa/pull/14533)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/api-ref-doc/SKILL.md`
- `.claude/skills/book-doc/SKILL.md`
- `.claude/skills/how-to/SKILL.md`
- `.claude/skills/recipe/SKILL.md`
- `.claude/skills/resources-doc/SKILL.md`
- `.claude/skills/tutorial/SKILL.md`
- `.claude/skills/ui-component-doc/SKILL.md`

## What to add / change

Add skill files to assist in writing docs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
