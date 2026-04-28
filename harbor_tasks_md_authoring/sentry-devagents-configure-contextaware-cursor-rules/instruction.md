# dev(agents): Configure context-aware Cursor rules with file matching

Source: [getsentry/sentry#105426](https://github.com/getsentry/sentry/pull/105426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/README.md`
- `.cursor/rules/backend.mdc`
- `.cursor/rules/frontend.mdc`
- `.cursor/rules/general.mdc`
- `.cursor/rules/tests.mdc`
- `AGENTS.md`

## What to add / change

Adds .cursor/rules/*.mdc files to automatically load domain-specific AGENTS.md files based on the file being edited:
* Backend Python files → loads src/AGENTS.md
* Test files → loads tests/AGENTS.md
* Frontend files → loads static/AGENTS.md
* All files → always loads root AGENTS.md

Benefits:
* Token efficient: Only loads relevant context for current task
* Better AI responses: Gets targeted guidance (backend vs frontend vs testing patterns)
* Prevents context overload: No need to load all guides simultaneously

Also includes documentation in root AGENTS.md and .cursor/rules/README.md explaining the setup.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
