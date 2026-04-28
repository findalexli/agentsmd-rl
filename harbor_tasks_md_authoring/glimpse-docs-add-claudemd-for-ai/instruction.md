# docs: add CLAUDE.md for AI assistant guidance

Source: [seatedro/glimpse#25](https://github.com/seatedro/glimpse/pull/25)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add comprehensive documentation for AI assistants including:
- Project overview and architecture
- Codebase structure and key files
- Development commands and workflows
- Code style guidelines (terse, docstrings only)
- Jujutsu version control instructions
- CI/CD pipeline details

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
