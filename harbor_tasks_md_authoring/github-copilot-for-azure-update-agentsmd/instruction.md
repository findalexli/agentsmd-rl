# Update AGENTS.md

Source: [microsoft/GitHub-Copilot-for-Azure#651](https://github.com/microsoft/GitHub-Copilot-for-Azure/pull/651)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `tests/AGENTS.md`

## What to add / change

Update the AGENTS.md to make it clear that when Copilot scaffolds tests for new skills, it shouldn't add or change files outside of the new test directory. Copilot Coding Agent was making changes to unrelated files.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
