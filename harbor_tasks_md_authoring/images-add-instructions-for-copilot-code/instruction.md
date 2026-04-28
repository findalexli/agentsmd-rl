# Add instructions for Copilot Code Review

Source: [devcontainers/images#1607](https://github.com/devcontainers/images/pull/1607)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This should help us ensure we dont miss things during reviews. We will trial it here before adding it to other repos

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
