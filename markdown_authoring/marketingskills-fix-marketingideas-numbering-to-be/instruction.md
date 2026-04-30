# Fix marketing-ideas numbering to be sequential

Source: [coreyhaines31/marketingskills#18](https://github.com/coreyhaines31/marketingskills/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/marketing-ideas/SKILL.md`

## What to add / change

## Summary

The marketing ideas were reorganized from an ebook but kept their original numbers, resulting in out-of-order numbering (3, 7, 39, 40, 41, 56...).

## Changes

- Renumbered all 139 ideas sequentially (1, 2, 3, 4...)
- Updated description and header from 140 to 139 (actual count)
- Fixed Related Skills references to correct new numbers (#40→#4, #2→#11, #30→#15)

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
