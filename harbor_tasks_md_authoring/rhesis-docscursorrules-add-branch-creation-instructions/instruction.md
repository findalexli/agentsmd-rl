# docs(cursor-rules): add branch creation instructions to PR rules

Source: [rhesis-ai/rhesis#1239](https://github.com/rhesis-ai/rhesis/pull/1239)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/pull-requests.mdc`

## What to add / change

## Purpose
Improve the pull request cursor rules by adding detailed branch creation instructions with proper command formatting.

## What Changed
- Added "Branch Creation" section with git commands to create branches from latest main
- Included proper bash code block formatting for the commands
- Added comments explaining each step

## Additional Context
This ensures team members follow a consistent workflow when starting new feature branches.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
