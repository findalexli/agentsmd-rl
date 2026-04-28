# Compress CLAUDE.md and reorder sections by priority

Source: [Mng-dev-ai/agentrove#545](https://github.com/Mng-dev-ai/agentrove/pull/545)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Tightened language and removed redundant examples across CLAUDE.md (~13% byte reduction).
- Reordered top-level sections by priority: universal rules (Project Context, Minimalism, Completion Quality Gate, Verification) first, then code style, naming/organization, backend data conventions, frontend, and finally code review guidance.
- No rules dropped — content preserved verbatim where present.

## Test plan
- [ ] Skim the file and confirm all previously-listed rules are still present.
- [ ] Verify section ordering reads top-down from most universal to most task-specific.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
