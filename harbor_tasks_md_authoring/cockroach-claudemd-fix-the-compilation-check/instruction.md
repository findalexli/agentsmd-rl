# CLAUDE.md: fix the compilation check filter

Source: [cockroachdb/cockroach#163512](https://github.com/cockroachdb/cockroach/pull/163512)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

`-f -` doesn't actually skip all tests -- `-f -.` is what we want.

Epic: None
Release note: None

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
