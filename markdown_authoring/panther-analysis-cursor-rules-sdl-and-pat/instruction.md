# Cursor Rules: SDL and Pat Testing

Source: [panther-labs/panther-analysis#1731](https://github.com/panther-labs/panther-analysis/pull/1731)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/simple-detections.mdc`
- `.cursor/rules/testing.mdc`

## What to add / change

Adds two new cursor rules for writing SDL and for Pat testing. 


https://github.com/user-attachments/assets/34e497da-63f2-42cf-a1f4-4bccb610a1f9

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
