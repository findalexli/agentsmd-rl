# Add AGENTS.md

Source: [google/oss-fuzz#14888](https://github.com/google/oss-fuzz/pull/14888)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Provide basic instructions on using helper.py for working with projects/ and how to work with code in infra/

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
