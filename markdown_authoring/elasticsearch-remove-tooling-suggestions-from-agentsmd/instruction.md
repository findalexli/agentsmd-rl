# Remove tooling suggestions from AGENTS.md

Source: [elastic/elasticsearch#146413](https://github.com/elastic/elasticsearch/pull/146413)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

These tools are environment specific, and in flux. This commit removes the guidance for agents, leaving AGENTS.md focused on the project structure and best practices.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
