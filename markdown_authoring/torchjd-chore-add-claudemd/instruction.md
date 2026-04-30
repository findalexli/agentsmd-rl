# chore: Add CLAUDE.md

Source: [SimplexLab/TorchJD#567](https://github.com/SimplexLab/TorchJD/pull/567)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

At the time of writing, claude code does not support the standard AGENTS.md.

See the status of https://github.com/anthropics/claude-code/issues/6235.

This is a kinda shitty workaround that some people advise.

IMO this is an argument against using claude code. It seems that they want to lock us in. But for now it's fine, we're just one renaming away from being able to change agent, and claude is just too good to change now.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
