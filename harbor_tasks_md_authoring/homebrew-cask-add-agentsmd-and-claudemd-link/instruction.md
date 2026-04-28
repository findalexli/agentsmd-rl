# Add AGENTS.md and CLAUDE.md (link to AGENTS.md)

Source: [Homebrew/homebrew-cask#247404](https://github.com/Homebrew/homebrew-cask/pull/247404)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Add AGENTS.md and CLAUDE.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
