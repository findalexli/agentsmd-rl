# Add AI coding guidelines for GitHub Copilot and Cursor

Source: [SRombauts/SQLiteCpp#529](https://github.com/SRombauts/SQLiteCpp/pull/529)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/load-github-copilot-instructions.mdc`
- `.github/copilot-instructions.md`

## What to add / change

- Add .github/copilot-instructions.md with project-specific coding guidelines for AI assistants (GitHub Copilot, Cursor, etc.)
- Add Cursor rule (.cursor/rules/load-github-copilot-instructions.mdc) to ensure the guidelines are loaded before any coding task
- Update .editorconfig charset to latin1 for compatibility with existing source files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
