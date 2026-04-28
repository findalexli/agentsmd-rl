# Add Initial Cursor Rules

Source: [livekit/agents-js#701](https://github.com/livekit/agents-js/pull/701)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/agent-core.mdc`

## What to add / change

This is the initial draft for agent js cursor rule, will going to keep iterate on this

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
