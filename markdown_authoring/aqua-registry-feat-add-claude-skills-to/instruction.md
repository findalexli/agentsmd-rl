# feat: add claude skills to .agents/

Source: [aquaproj/aqua-registry#52709](https://github.com/aquaproj/aqua-registry/pull/52709)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/fetch-doc/SKILL.md`
- `.agents/skills/review-change/SKILL.md`

## What to add / change

## Summary
- copy Claude skills into .agents/skills

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
