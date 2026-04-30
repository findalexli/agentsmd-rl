# Tighten make-pr skill workflow

Source: [remix-run/remix#11167](https://github.com/remix-run/remix/pull/11167)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/make-pr/SKILL.md`

## What to add / change

This tightens the `make-pr` skill around the fastest path to a credible PR, especially when working from a detached `HEAD` or a small, focused change.

- add fast-path checks for branch state before deeper prep
- encourage using the smallest useful context and getting to a clean commit quickly
- add a change-file decision point instead of assuming every PR needs release notes
- clean up the body template wording and markdown fencing so the example renders clearly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
