# docs: correct architecture docs to match alacritty_terminal PTY stack

Source: [peters/horizon#24](https://github.com/peters/horizon/pull/24)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Replace stale `vt100` and `portable-pty` references in AGENTS.md with the actual `alacritty_terminal` stack
- Update stack summary, horizon-core module description, threading model, data flow diagram, and panel lifecycle

Closes #17

## Test plan

- [x] No code changes, docs only
- [x] `cargo fmt` and maintainability checks pass

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
