# [mob][photos] symlink for agents.md

Source: [ente-io/ente#7128](https://github.com/ente-io/ente/pull/7128)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `mobile/apps/photos/AGENTS.md`
- `mobile/apps/photos/CLAUDE.md`

## What to add / change

## Description

symlink for [agents.md](https://agents.md)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
