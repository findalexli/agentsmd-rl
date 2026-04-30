# AGENTS.md: restructure root and client AGENTS.md

Source: [Automattic/wp-calypso#108874](https://github.com/Automattic/wp-calypso/pull/108874)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `client/AGENTS.md`
- `packages/image-studio/AGENTS.md`
- `packages/image-studio/CLAUDE.md`

## What to add / change

## Proposed Changes

Restructure contents of `AGENTS.md` at root and `client/`, so that it's easier for devs to add more stuff to it in the future.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
