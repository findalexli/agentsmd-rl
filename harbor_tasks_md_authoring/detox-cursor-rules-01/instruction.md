# Cursor rules 0.1

Source: [wix/Detox#4873](https://github.com/wix/Detox/pull/4873)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/detox-idomatic.mdc`
- `.cursor/rules/detox-unittests.mdc`

## What to add / change

## Description

<!--
Thank you for contributing!

Step 1: Before submitting a pull request that introduces a new functionality or fixes a bug,
please open an issue where we could discuss the suggestion, problem - and potential ways to fix.
-->

- This pull request addresses the issue described here: #<?>

<!--
Step 2: Provide an overview of how your fix / enhancement works.
If possible, provide screenshots of the before and after states (even for simple command line options - show the terminal).
-->

In this pull request, I have …

<!--
Step 3: Please review the checklist below.
-->

---


> _For features/enhancements:_
 - [ ] I have added/updated the relevant references in the [documentation](https://github.com/wix/Detox/tree/master/docs) files.

> _For API changes:_
 - [ ] I have made the necessary changes in the [types index](https://github.com/wix/Detox/blob/master/detox/index.d.ts) file.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
