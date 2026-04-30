# [DOC] Improve AGENTS.md based on best practices research

Source: [OpenMS/OpenMS#8563](https://github.com/OpenMS/OpenMS/pull/8563)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Enhance AGENTS.md following the AGENTS.md standard best practices while preserving all original content:

Added:
- Critical Constraints section upfront (explicit "NEVER do" list)
- Quick Commands section with copy-paste ready bash commands
- Visual directory tree for repo layout
- Code examples for naming conventions, file structure, and tests
- Commit message example
- Debugging command examples

Preserved:
- All original build/install instructions
- All testing guidelines and details
- All coding conventions
- All pyOpenMS wrapping details
- All external documentation links
- All CI/packaging information

Based on research from GitHub's analysis of 2,500+ repositories and the official AGENTS.md specification.

## Description

<!-- Please include a summary of the change and which issue is fixed here. -->

## Checklist
- [ ] Make sure that you are listed in the AUTHORS file
- [ ] Add relevant changes and new features to the CHANGELOG file
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] New and existing unit tests pass locally with my changes
- [ ] Updated or added python bindings for changed or new classes (Tick if no updates were necessary.)

### How can I get additional information on failed tests during CI
<details>
  <summary>Click to expand</summary>
If your PR is failing you can check out

- The details of the action statuses at the end of the PR or the "Checks" tab.
- http://cdash.seqan.de/index.php?pr

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
