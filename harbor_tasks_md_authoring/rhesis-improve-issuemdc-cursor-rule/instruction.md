# Improve issue.mdc cursor rule

Source: [rhesis-ai/rhesis#346](https://github.com/rhesis-ai/rhesis/pull/346)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/issue.mdc`

## What to add / change

This PR improves the issue.mdc cursor rule with better formatting and clearer instructions for creating GitHub issues.

Changes:
- Updated issue type descriptions to use proper capitalization ("Bug", "Feature", "Task")
- Added clarification about not adding issue type labels
- Improved formatting and readability of the rule instructions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
