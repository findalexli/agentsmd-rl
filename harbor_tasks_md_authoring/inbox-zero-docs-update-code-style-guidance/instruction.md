# docs: Update code style guidance

Source: [elie222/inbox-zero#2382](https://github.com/elie222/inbox-zero/pull/2382)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Updates contributor guidance around when to inline logic versus extracting helpers.

The wording keeps co-location as the default while allowing helpers for clearer call sites, meaningful domain concepts, or shared behavior that should stay consistent across flows.

Validation: docs-only change.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
