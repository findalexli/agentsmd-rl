# SKILL.md: Make quota error handling explicit

Source: [koreal6803/finlab-ai#5](https://github.com/koreal6803/finlab-ai/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `finlab-plugin/skills/finlab/SKILL.md`

## What to add / change

## The Problem

The docs were passive. They said "告知" (inform) but:
- Didn't tell the AI WHEN to trigger (no error string)
- Didn't say to be PROACTIVE

Result: AI just dumps the error and waits for user to ask "what now?"

## The Fix

Three changes:
1. Added exact error string: `Usage exceed 500 MB/day`
2. Changed "告知" to "**主動**告知" (proactively inform)
3. Numbered the steps (easier to follow)

That's it. No over-engineering.

## Feedback Reference
- ID: 9419cac6-d5a3-4a39-ac8b-070b92ef3467
- Type: improvement
- Context: User hit 500MB limit, AI didn't proactively suggest upgrade

---

Note: The other feedback (a929c427) wants 80% warnings and "new user protection periods". Those require **package code changes**, not docs. Out of scope for this repo.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
