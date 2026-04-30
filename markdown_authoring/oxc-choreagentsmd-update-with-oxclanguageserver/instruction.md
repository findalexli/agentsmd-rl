# chore(AGENTS.md): update with `oxc_language_server`

Source: [oxc-project/oxc#14910](https://github.com/oxc-project/oxc/pull/14910)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Also updates currently used rust toolchain version.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
