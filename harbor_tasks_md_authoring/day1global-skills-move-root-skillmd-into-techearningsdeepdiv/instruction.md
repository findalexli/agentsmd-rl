# Move root SKILL.md into tech-earnings-deepdive/ folder

Source: [star23/Day1Global-Skills#8](https://github.com/star23/Day1Global-Skills/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `tech-earnings-deepdive/SKILL.md`

## What to add / change

This makes the repo a proper multi-skill repo so that `npx skills add --all` can discover all 5 skills.

https://claude.ai/code/session_01SjBQfRh6amw1qofqP4VfNX

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
