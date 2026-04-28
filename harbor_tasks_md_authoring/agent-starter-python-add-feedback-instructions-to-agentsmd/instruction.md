# Add feedback instructions to AGENTS.md

Source: [livekit-examples/agent-starter-python#30](https://github.com/livekit-examples/agent-starter-python/pull/30)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This ensures coding agents can help us improve the docs (see https://github.com/livekit/web/pull/2239)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
