# AGENTS.md: consolidate PR guidelines

Source: [Automattic/wp-calypso#108822](https://github.com/Automattic/wp-calypso/pull/108822)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/pr.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Proposed Changes

Pull the PR guidelines from Claude rule to AGENTS.md itself.

## Why are these changes being made?

So that other agents can use it.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
