# docs: Clean up AGENTS.md structure

Source: [Eventual-Inc/Daft#5321](https://github.com/Eventual-Inc/Daft/pull/5321)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Changes Made

Cleaned up AGENTS.md structure for better readability and AI performance:
- Removed redundant file name header (`# AGENTS.md`)
- Promoted all section headers from `##` to `#` for cleaner structure
- Simplified PR conventions line by removing example text (`e.g., feat: ...`)

Reducing unnecessary text improves context efficiency and AI comprehension.

Follows up on #5124 which introduced this file.

## Internal

Closes https://linear.app/eventual/issue/EVE-959/docs-clean-up-agentsmd-structure

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
