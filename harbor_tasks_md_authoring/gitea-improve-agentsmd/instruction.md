# Improve AGENTS.md

Source: [go-gitea/gitea#37382](https://github.com/go-gitea/gitea/pull/37382)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Adds points to `AGENTS.md` how to run single tests because AIs get these wrong too often (either they trigger the whole suite or run into other errors).

---
This PR was written with the help of Claude Opus 4.7

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
