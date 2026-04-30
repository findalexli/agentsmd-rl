# update agents md

Source: [nextcloud/android#16871](https://github.com/nextcloud/android/pull/16871)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!--
TESTING

Writing tests is very important. Please try to write some tests for your PR. 
If you need help, please do not hesitate to ask in this PR for help.

Unit tests: https://github.com/nextcloud/android/blob/master/CONTRIBUTING.md#unit-tests
Instrumented tests: https://github.com/nextcloud/android/blob/master/CONTRIBUTING.md#instrumented-tests
UI tests: https://github.com/nextcloud/android/blob/master/CONTRIBUTING.md#ui-tests
 -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
