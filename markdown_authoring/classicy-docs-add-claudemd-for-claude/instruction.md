# docs: add CLAUDE.md for Claude Code guidance

Source: [robbiebyrd/classicy#116](https://github.com/robbiebyrd/classicy/pull/116)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Provides project overview, common commands, architecture documentation, and development notes for Claude Code when working in this repository.

https://claude.ai/code/session_01PhB1vsCMGSG4ruLYndYX97

## Summary by Sourcery

Documentation:
- Document project overview, architecture, and development workflows for contributors using Claude Code, including commands, path aliases, state management, theming, and build notes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
