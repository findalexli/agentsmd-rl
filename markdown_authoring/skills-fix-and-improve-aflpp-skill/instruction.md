# fix and improve aflpp skill

Source: [trailofbits/skills#15](https://github.com/trailofbits/skills/pull/15)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/testing-handbook-skills/skills/aflpp/SKILL.md`

## What to add / change

The AFL++ skill has various bugs, outdated information and is missing improvements.
I am commenting the changes in the PR to explain why the changes should be done.

For further improvements, a section could be added to explain various good environment variables to add for fuzzing with afl-fuzz.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
