# Add root SKILL.md for directory compatibility

Source: [talkstream/ru-text#6](https://github.com/talkstream/ru-text/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

Root-level SKILL.md with adjusted paths enables discovery by skills directories (skillsdirectory.com, skills.sh, skillhub.club, etc.).

The canonical skill remains at `skills/ru-text/SKILL.md` — this is a copy with paths adjusted for root context.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
