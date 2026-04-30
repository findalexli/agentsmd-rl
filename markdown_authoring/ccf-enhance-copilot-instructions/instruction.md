# Enhance copilot instructions

Source: [microsoft/CCF#7678](https://github.com/microsoft/CCF/pull/7678)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

A second attempt at #7677, with a lot more human input. Some sections taken from the robot's attempt, some additional constraints suggested by me.

Further comments and discussion welcome.

Hopefully brief enough to avoid blowing out any context windows, while still covering the critical bases to get repo-specific work from agents.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
