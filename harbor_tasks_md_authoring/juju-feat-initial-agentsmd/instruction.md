# feat: initial AGENTS.md

Source: [juju/juju#21300](https://github.com/juju/juju/pull/21300)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This is the initial germ of a file for use by coding agents.

It is expected that we will refine this over time.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
