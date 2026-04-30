# Rename AGENT.md ==> AGENTS.md

Source: [pyodide/pyodide#6035](https://github.com/pyodide/pyodide/pull/6035)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `AGENTS.md`

## What to add / change

Looks like this is a more common name in convention

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
