# Add architecture section to CLAUDE.md

Source: [manzaltu/claude-code-ide.el#39](https://github.com/manzaltu/claude-code-ide.el/pull/39)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Provides a brief overview of the package structure and what each .el file contains, helping Claude Code quickly understand the codebase organization.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
