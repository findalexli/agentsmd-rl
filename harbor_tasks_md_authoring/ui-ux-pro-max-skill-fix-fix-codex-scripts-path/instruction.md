# fix: fix codex scripts path

Source: [nextlevelbuilder/ui-ux-pro-max-skill#80](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/pull/80)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codex/skills/ui-ux-pro-max/SKILL.md`

## What to add / change

Summary:

  - Update all search.py command examples to use the correct path under .codex/skills/ui-ux-pro-max/scripts

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
