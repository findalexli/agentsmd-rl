# Add CLAUDE.md

Source: [Homebrew/brew#21504](https://github.com/Homebrew/brew/pull/21504)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Add CLAUDE.md, linked to the existing AGENTS.md

- https://github.com/Homebrew/homebrew-core/pull/265525
- https://github.com/Homebrew/homebrew-cask/pull/247404

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
