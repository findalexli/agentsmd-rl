# docs(AGENTS): add guidance for running single test files

Source: [sanity-io/sanity#12332](https://github.com/sanity-io/sanity/pull/12332)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Claude _always_ get the "run a single test" wrong.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
