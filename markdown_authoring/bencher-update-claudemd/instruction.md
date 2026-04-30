# Update `CLAUDE.md`

Source: [bencherdev/bencher#652](https://github.com/bencherdev/bencher/pull/652)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Claude tried to create a shell script, so I'm adding a section to `CLAUDE.md` to clarify how tasks should be handled in the codebase.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
