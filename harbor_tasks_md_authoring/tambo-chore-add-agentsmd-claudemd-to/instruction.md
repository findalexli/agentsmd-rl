# chore: add agents.md & claude.md to monorepo.

Source: [tambo-ai/tambo#1116](https://github.com/tambo-ai/tambo/pull/1116)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `cli/AGENTS.md`
- `cli/CLAUDE.md`
- `create-tambo-app/AGENTS.md`
- `create-tambo-app/CLAUDE.md`
- `docs/AGENTS.md`
- `docs/CLAUDE.md`
- `react-sdk/AGENTS.md`
- `react-sdk/CLAUDE.md`
- `showcase/AGENTS.md`
- `showcase/CLAUDE.md`

## What to add / change

- Added AGENTS.md
- Added CLAUDE.md pointers

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
