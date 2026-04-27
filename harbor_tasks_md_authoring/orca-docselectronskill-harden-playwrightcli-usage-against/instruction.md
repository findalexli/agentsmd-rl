# docs(electron-skill): harden playwright-cli usage against alias and port collisions

Source: [stablyai/orca#996](https://github.com/stablyai/orca/pull/996)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/electron/SKILL.md`

## What to add / change

## Summary
- Prefer `command playwright-cli` in all examples to bypass user shell aliases that leak flags like `--persistent` into subcommands.
- Add CDP port probing guidance (loop 9333–9340) so agents don't attach to a stale dev server left by another worktree.
- Add a post-attach verification snippet that confirms the connected app is the intended worktree before proceeding.

## Test plan
- [ ] Skim rendered SKILL.md on GitHub to confirm formatting

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
