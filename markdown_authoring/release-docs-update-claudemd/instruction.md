# docs: update CLAUDE.md

Source: [openshift/release#70141](https://github.com/openshift/release/pull/70141)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Update CLAUDE.md with improved guidance on Claude usage in this repo: setup steps, prompt conventions, known limitations, and updated examples. Clarifies scope and best practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
