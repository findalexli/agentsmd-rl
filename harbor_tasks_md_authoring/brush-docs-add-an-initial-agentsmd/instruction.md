# docs: add an initial AGENTS.md file

Source: [reubeno/brush#714](https://github.com/reubeno/brush/pull/714)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This aims to better aid AI-assisted analysis and work in this repo. Of course, any AI-assisted contributions must comply with the new policy specified in #694.

I expect that this file will be a living document, and continually iterated based on our learnings.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
