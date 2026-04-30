# Delete .cursorrules

Source: [OWASP-BLT/BLT#6071](https://github.com/OWASP-BLT/BLT/pull/6071)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Chores**
  * Removed internal development configuration file. No impact on application functionality or user experience.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
