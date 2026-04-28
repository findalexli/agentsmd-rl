# AGENTS.md: add agent instructions to the repo

Source: [irbis-sh/zen-desktop#655](https://github.com/irbis-sh/zen-desktop/pull/655)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

### What does this PR do?

Self-explanatory. See https://agents.md for more details.

### How did you verify your code works?

<!--
**Please describe your testing strategy**:

- If you performed manual testing, list the steps to verify correct functionality, including edge cases if applicable.
- If new or existing automated tests cover the functionality, explicitly mention them.
-->

### What are the relevant issues?

<!--
**Please link any relevant issues**, for example:

Closes #123
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
