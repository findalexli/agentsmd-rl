# AGENTS.md: rename from .github/copilot-instructions.md.

Source: [Homebrew/brew#20759](https://github.com/Homebrew/brew/pull/20759)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This will provide instructions for all agents as this is both supported by Copilot now and become a bit of a standard.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
