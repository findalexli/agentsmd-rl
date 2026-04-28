# Add claude skills for fakes and tests

Source: [stripe/stripe-android#12468](https://github.com/stripe/stripe-android/pull/12468)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/create-fake/SKILL.md`
- `.claude/skills/write-tests/SKILL.md`

## What to add / change

# Summary
<!-- Simple summary of what was changed. -->
Add claude skills for writing fakes and writing tests

# Motivation
<!-- Why are you making this change? If it's for fixing a bug, if possible, please include a code snippet or example project that demonstrates the issue. -->
Hopefully improve claude's ability to write tests in our preferred styles

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
