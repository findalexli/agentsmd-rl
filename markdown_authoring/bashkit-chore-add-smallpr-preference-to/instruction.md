# chore: add small-PR preference to AGENTS.md

Source: [everruns/bashkit#217](https://github.com/everruns/bashkit/pull/217)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Add guidance to PRs section in AGENTS.md: prefer small, shippable PRs and follow instructions when asked to split into separate PRs.

## Test plan
- [ ] Verify AGENTS.md renders correctly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
