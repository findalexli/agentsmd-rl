# Symlink CLAUDE.md instead of pointing to it

Source: [microsoft/vscode-copilot-chat#3321](https://github.com/microsoft/vscode-copilot-chat/pull/3321)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`
- `.claude/CLAUDE.md`

## What to add / change

Seems to work on macOS and from what I read, will be ok for our Windows devs:

> Windows compatibility: On Windows, symlinks require Developer Mode enabled or admin privileges. Without these, git clone will create a regular file containing the symlink path as text.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
