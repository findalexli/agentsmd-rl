# Merge CLAUDE.md into AGENTS.md

Source: [databricks/cli#3506](https://github.com/databricks/cli/pull/3506)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

## Changes
This merges `CLAUDE.md` into `AGENTS.md`. The former will now be a symlink, just like `.cursurrules`.

## Review
* This PR was AI-generated. As a human reviewer, I confirmed it just merges the files and then re-orders the sections in a sensible way. Only minimal phrasing rewrites were included.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
