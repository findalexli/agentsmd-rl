# Add copilot instructions

Source: [openvinotoolkit/model_server#3992](https://github.com/openvinotoolkit/model_server/pull/3992)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

### 🛠 Summary

JIRA/Issue if applicable.
Describe the changes.

### 🧪 Checklist

- [ ] Unit tests added.
- [ ] The documentation updated.
- [ ] Change follows security best practices.
``

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
