# llm: Add a mention of Testdrive version guards in the mz-test skill

Source: [MaterializeInc/materialize#36268](https://github.com/MaterializeInc/materialize/pull/36268)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/mz-test/SKILL.md`

## What to add / change

My agent kept forgetting about this. (I can't blame it, because I also often forget about this, lol.)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
