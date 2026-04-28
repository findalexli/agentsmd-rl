# docs: add CLAUDE.md pointing to AGENTS.md

Source: [unkeyed/unkey#5913](https://github.com/unkeyed/unkey/pull/5913)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add a root `CLAUDE.md` that points Claude Code to the existing `AGENTS.md`, so agent instructions load automatically without duplicating content.

## Test plan
- [ ] Confirm `CLAUDE.md` is picked up by Claude Code and `AGENTS.md` is loaded via the `@AGENTS.md` reference.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
