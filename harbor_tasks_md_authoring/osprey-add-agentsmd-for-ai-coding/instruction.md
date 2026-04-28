# add AGENTS.md for AI coding agents

Source: [roostorg/osprey#234](https://github.com/roostorg/osprey/pull/234)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description

Adds AGENTS.md at the repo root following the ROOST agents.md template, customized for Osprey.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
