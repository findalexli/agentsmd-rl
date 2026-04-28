# docs: improve code comment guidelines in CLAUDE.md

Source: [datahub-project/datahub#14620](https://github.com/datahub-project/datahub/pull/14620)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds guidelines for when to add valuable code comments vs when to avoid obvious ones.

## Changes

- New "Code Comments" section in CLAUDE.md
- Focus on WHY rather than WHAT
- Include examples of good vs bad comments
- Reduce low-value comment noise

This helps AI assistants and developers write better, more meaningful comments.

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
