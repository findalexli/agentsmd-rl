# task(fxa): Add CLAUDE.md instructions

Source: [mozilla/fxa#19787](https://github.com/mozilla/fxa/pull/19787)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Because

* We want to add guardrails for Claude

## This pull request

* Adds a CLAUDE.md file incl. file ignore instructions

## Issue that this pull request solves

Closes: (issue number)

## Checklist

_Put an `x` in the boxes that apply_

- [x] My commit is GPG signed.
- [ ] If applicable, I have modified or added tests which pass locally.
- [ ] I have added necessary documentation (if appropriate).
- [ ] I have verified that my changes render correctly in RTL (if appropriate).

## Screenshots (Optional)

Please attach the screenshots of the changes made in case of change in user interface.

## Other information (Optional)

Any other information that is important to this pull request.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
