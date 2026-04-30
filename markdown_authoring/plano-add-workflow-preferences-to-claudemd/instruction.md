# Add workflow preferences to CLAUDE.md

Source: [katanemo/plano#770](https://github.com/katanemo/plano/pull/770)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add workflow preferences section to CLAUDE.md: no co-author lines, concise commit messages, feature branch enforcement, branch naming convention, and issue-to-PR workflow.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
