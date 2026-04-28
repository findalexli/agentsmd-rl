# add agents.md to help LLMs

Source: [nushell/nushell#17148](https://github.com/nushell/nushell/pull/17148)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agents.md`

## What to add / change

This PR adds an Agents.md file to help with LLMs

## Release notes summary - What our users need to know
N/A

## Tasks after submitting
N/A

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
