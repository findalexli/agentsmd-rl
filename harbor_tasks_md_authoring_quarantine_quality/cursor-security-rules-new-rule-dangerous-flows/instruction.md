# New Rule - Dangerous Flows

Source: [matank001/cursor-security-rules#1](https://github.com/matank001/cursor-security-rules/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `dangerous-flows.mdc`

## What to add / change

This rule helps your Cursor to look for and identify dangerous flows, starting from user input all the way to the actual dangerous function.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
