# Migrate GitHub Copilot instructions to AGENTS.md

Source: [vscode-reborn-ai/vscode-reborn-ai#172](https://github.com/vscode-reborn-ai/vscode-reborn-ai/pull/172)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Copilot coding agent now supports AGENTS.md custom instructions, as more coding agents support it. Migrating from GitHub Copilot's custom instructions file to AGENTS.md will help developers leverage more and different coding agents than just GitHub Copilot.

Reference:
- https://agents.md/
- https://github.blog/changelog/2025-08-28-copilot-coding-agent-now-supports-agents-md-custom-instructions/

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
