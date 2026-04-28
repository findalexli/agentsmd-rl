# chore: sync from agents-private

Source: [inkeep/agents#3197](https://github.com/inkeep/agents/pull/3197)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/emil-design-eng/SKILL.md`

## What to add / change

Automated sync from agents-private via Copybara mirror.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
