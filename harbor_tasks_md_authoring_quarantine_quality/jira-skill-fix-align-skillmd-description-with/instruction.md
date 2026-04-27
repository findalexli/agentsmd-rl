# fix: align SKILL.md description with quality standard

Source: [netresearch/jira-skill#17](https://github.com/netresearch/jira-skill/pull/17)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/jira-communication/SKILL.md`
- `skills/jira-syntax/SKILL.md`

## What to add / change

## Summary
- Fix SKILL.md description to use "Use when..." trigger format
- Remove "Agent Skill:" prefix and "By Netresearch." suffix
- Remove workflow summaries from description

Addresses netresearch/claude-code-marketplace#32

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
