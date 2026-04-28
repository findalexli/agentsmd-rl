# docs(skill): Encourage proactive committing in SKILL.md

Source: [gitbutlerapp/gitbutler#12159](https://github.com/gitbutlerapp/gitbutler/pull/12159)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `crates/but/skill/SKILL.md`

## What to add / change

Emphasize that models should commit early and often since GitButler
makes editing history trivial with absorb, squash, and reword commands.
Small atomic commits that get refined later are better than accumulating
large uncommitted changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
