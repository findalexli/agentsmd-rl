# Expand copilot instructions

Source: [equinor/ert#12922](https://github.com/equinor/ert/pull/12922)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- [x] PR title captures the intent of the changes, and is fitting for release notes.
- [x] Added appropriate release note label
- [x] Commit history is consistent and clean, in line with the [contribution guidelines](https://github.com/equinor/ert/blob/main/CONTRIBUTING.md).
- [x] Make sure unit tests pass locally after every commit (`git rebase -i main
      --exec 'just rapid-tests'`)

## When applicable
- [ ] **When there are user facing changes**: Updated documentation
- [ ] **New behavior or changes to existing untested code**: Ensured that unit tests are added (See [Ground Rules](https://github.com/equinor/ert/blob/main/CONTRIBUTING.md#ground-rules)).
- [ ] **Large PR**: Prepare changes in small commits for more convenient review
- [ ] **Bug fix**: Add regression test for the bug
- [ ] **Bug fix**: Add backport label to latest release (format: 'backport release-branch-name')

<!--
Adding labels helps the maintainers when writing release notes. This is the [list of release note labels](https://github.com/equinor/ert/labels?q=release-notes).
-->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
