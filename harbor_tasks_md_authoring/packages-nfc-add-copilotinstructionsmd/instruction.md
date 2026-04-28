# [NFC] Add copilot-instructions.md

Source: [getsolus/packages#6641](https://github.com/getsolus/packages/pull/6641)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

**Summary**
Add copilot-instructions file to disallow creation of issues that are AI generated

- [ ] Package was built and tested against unstable
- [ ] This change could gainfully be listed in the weekly sync notes once merged  <!-- Write an appropriate message in the Summary section, then add the "Topic: Sync Notes" label -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
