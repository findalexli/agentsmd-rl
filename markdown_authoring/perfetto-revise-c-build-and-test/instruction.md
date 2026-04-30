# Revise C++ build and test instructions in AGENTS.md

Source: [google/perfetto#3462](https://github.com/google/perfetto/pull/3462)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Updated instructions for building and running C++ tests,
including environment variable usage and command examples.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
