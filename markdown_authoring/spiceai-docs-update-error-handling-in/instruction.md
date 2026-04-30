# docs: Update error handling in copilot instructions

Source: [spiceai/spiceai#7652](https://github.com/spiceai/spiceai/pull/7652)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## 📝 Summary

<!-- What does this PR change? Why is it necessary? Keep it concise. -->

* Clarify error handling guidelines for test and non-test code.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
