# docs(agents): add CLAUDE.md similar to cursorrules

Source: [alex-ilgayev/MCPSpy#41](https://github.com/alex-ilgayev/MCPSpy/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`
- `CLAUDE.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
