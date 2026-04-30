# feat: add Amazon platform to requesthunt skill

Source: [ReScienceLab/opc-skills#77](https://github.com/ReScienceLab/opc-skills/pull/77)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/requesthunt/SKILL.md`

## What to add / change

## Summary
- Add Amazon as a new platform throughout the requesthunt skill (SKILL.md)
- Update platform strengths table, recommended platforms by category, quick selection rules
- Add Consumer Electronics as a new category recommendation
- Update all example commands to include `amazon` in platform lists
- Note Amazon depth cap (max 5) in cost section

Corresponds to requesthunt v1.14.0 release.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
