# chore: update CLAUDE.md files to reference AGENTS.md properly

Source: [tambo-ai/tambo#1214](https://github.com/tambo-ai/tambo/pull/1214)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `cli/CLAUDE.md`
- `create-tambo-app/CLAUDE.md`
- `docs/CLAUDE.md`
- `react-sdk/CLAUDE.md`
- `showcase/CLAUDE.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
