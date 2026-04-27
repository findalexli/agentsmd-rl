# Update push skill CI gating for missing checks

Source: [saffron-health/libretto#45](https://github.com/saffron-health/libretto/pull/45)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/push/SKILL.md`

## What to add / change

## Summary
- add fallback guidance when `gh pr checks` reports no checks after retries
- instruct merging `main` and using `fix-merge-conflicts` if conflicts are detected
- require re-running the full check-wait loop after every follow-up push in the same session

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
