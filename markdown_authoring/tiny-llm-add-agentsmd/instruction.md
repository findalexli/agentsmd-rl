# add AGENTS.md

Source: [skyzh/tiny-llm#85](https://github.com/skyzh/tiny-llm/pull/85)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR adds a repository-level `AGENTS.md` to standardize how coding agents run and validate tests in this project.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
