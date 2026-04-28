# docs(AI): let Claude read `AGENTS.md`

Source: [oxc-project/oxc#13603](https://github.com/oxc-project/oxc/pull/13603)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

References: 
https://github.com/anthropics/claude-code/issues/6235#issuecomment-3217884068
https://github.com/rolldown/rolldown/pull/6039

I've confirmed that it works.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
