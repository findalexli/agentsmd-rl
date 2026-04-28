# Revert "Split the root Agent.md files into subdirectories."

Source: [opf/openproject#22398](https://github.com/opf/openproject/pull/22398)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `app/AGENTS.md`
- `app/CLAUDE.md`
- `config/AGENTS.md`
- `config/CLAUDE.md`
- `db/AGENTS.md`
- `db/CLAUDE.md`
- `docker/dev/AGENTS.md`
- `docker/dev/CLAUDE.md`
- `frontend/AGENTS.md`
- `frontend/CLAUDE.md`
- `spec/AGENTS.md`
- `spec/CLAUDE.md`

## What to add / change

Reverts opf/openproject#22240

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
