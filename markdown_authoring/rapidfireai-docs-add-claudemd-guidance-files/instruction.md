# Docs: Add CLAUDE.md guidance files for all modules

Source: [RapidFireAI/rapidfireai#55](https://github.com/RapidFireAI/rapidfireai/pull/55)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `rapidfireai/automl/CLAUDE.md`
- `rapidfireai/backend/CLAUDE.md`
- `rapidfireai/db/CLAUDE.md`
- `rapidfireai/dispatcher/CLAUDE.md`
- `rapidfireai/ml/CLAUDE.md`
- `rapidfireai/utils/CLAUDE.md`

## What to add / change

Add comprehensive CLAUDE.md documentation files to guide AI-assisted development across all RapidFire modules. These files provide:

- Module overviews and architecture
- File-by-file documentation with purposes and key functions
- Usage examples and common patterns
- Integration points and dependencies
- Best practices and testing guidance

Files added:
- CLAUDE.md (repository root)
- rapidfireai/automl/CLAUDE.md
- rapidfireai/backend/CLAUDE.md
- rapidfireai/db/CLAUDE.md
- rapidfireai/dispatcher/CLAUDE.md
- rapidfireai/ml/CLAUDE.md
- rapidfireai/utils/CLAUDE.md (includes Colab support documentation)

These guidance files help Claude Code (and human developers) understand the codebase structure and make consistent, informed changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
