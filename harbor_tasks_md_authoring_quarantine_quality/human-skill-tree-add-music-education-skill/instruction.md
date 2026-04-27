# Add music education skill

Source: [24kchengYe/human-skill-tree#8](https://github.com/24kchengYe/human-skill-tree/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/02-music-arts/SKILL.md`

## What to add / change

Closes #5 

Added a new skill for music education covering music theory, instrument practice, ear training, performance skills, and music history appreciation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
