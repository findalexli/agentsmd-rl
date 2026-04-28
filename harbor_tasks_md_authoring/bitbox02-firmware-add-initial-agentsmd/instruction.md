# add initial AGENTS.md

Source: [BitBoxSwiss/bitbox02-firmware#1708](https://github.com/BitBoxSwiss/bitbox02-firmware/pull/1708)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

To support agentic reviews and coding workflows.

It was generated using the codex init command, with some manual modifications and extensions by myself.

Unsure if the docker instructions will work or are helpful, but we can iterate this later.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
