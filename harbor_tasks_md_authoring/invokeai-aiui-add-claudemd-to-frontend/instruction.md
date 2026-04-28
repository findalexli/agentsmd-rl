# ai(ui): add CLAUDE.md to frontend

Source: [invoke-ai/InvokeAI#8556](https://github.com/invoke-ai/InvokeAI/pull/8556)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `invokeai/frontend/web/CLAUDE.md`

## What to add / change

## Summary

add CLAUDE.md to frontend

## Related Issues / Discussions

n/a

## QA Instructions

n/a

## Merge Plan

n/a

## Checklist

- [x] _The PR has a short but descriptive title, suitable for a changelog_
- [ ] _Tests added / updated (if applicable)_
- [ ] _❗Changes to a redux slice have a corresponding migration_
- [ ] _Documentation added / updated (if applicable)_
- [ ] _Updated `What's New` copy (if doing a release after this PR)_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
