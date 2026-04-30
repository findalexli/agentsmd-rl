# Enhance copilot code review custom instructions

Source: [intel/intel-xpu-backend-for-triton#6148](https://github.com/intel/intel-xpu-backend-for-triton/pull/6148)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Provide maximum effectiveness for GitHub Copilot by:
- Being concise enough for Copilot to process efficiently
- Having clear priority signals (Critical vs Preferred)
- Providing abundant pattern examples for learning
- Focusing purely on code generation guidance
- Eliminating noise and redundancy

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
