# fix(plan): remove deprecated /technical_review references

Source: [EveryInc/compound-engineering-plugin#258](https://github.com/EveryInc/compound-engineering-plugin/pull/258)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-plan/SKILL.md`
- `plugins/compound-engineering/skills/deepen-plan/SKILL.md`

## What to add / change

## Summary

- Remove all references to the deprecated `/technical_review` command from `ce:plan` and `deepen-plan` skill files
- Renumber menu options after removal to keep numbering sequential
- The `/technical_review` command was removed in v2.32.0 but 6 references remained in the post-generation menus and selection handlers

## Why removal instead of replacement

The closed PR #247 took the wrong approach by replacing `/technical_review` with `/ce:review`. That's incorrect because `/ce:review` is a **code review** tool (for reviewing PRs/diffs), not a **plan review** tool. The plan menu already has the correct tool for plan review - "Review and refine" (option 4, now option 3), which loads the `document-review` skill. There's nothing to replace these references with - they just need to be removed.

Supersedes #247.
Fixes #244

## Changes

**`plugins/compound-engineering/skills/ce-plan/SKILL.md`** (4 removals):
- Removed option 3 (`/technical_review`) from post-generation menu, renumbered remaining options
- Removed `/technical_review` selection handler
- Updated loop-back text to remove `/technical_review` mention
- Removed `/technical_review` from issue creation follow-up prompt

**`plugins/compound-engineering/skills/deepen-plan/SKILL.md`** (2 removals):
- Removed option 2 (`/technical_review`) from post-enhancement menu, renumbered remaining options
- Removed `/technical_review` selection handler

## Test plan

- [ ] Run `/ce:plan` and verify the post-generation menu sh

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
