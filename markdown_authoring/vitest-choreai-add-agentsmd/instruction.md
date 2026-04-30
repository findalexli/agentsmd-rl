# chore(ai): add AGENTS.md

Source: [vitest-dev/vitest#8555](https://github.com/vitest-dev/vitest/pull/8555)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

### Description

Generated with Claude Code and is more accurate than #8543

Closes #8543

<!-- Please insert your description here and provide especially info about the "what" this PR is solving -->

<!-- You can also add additional context here -->

### Please don't delete this checklist! Before submitting the PR, please make sure you do the following:
- [ ] It's really useful if your PR references an issue where it is discussed ahead of time. If the feature is substantial or introduces breaking changes without a discussion, PR might be closed.
- [ ] Ideally, include a test that fails without this PR but passes with it.
- [ ] Please, don't make changes to `pnpm-lock.yaml` unless you introduce a new test example.
- [ ] Please check [Allow edits by maintainers](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/allowing-changes-to-a-pull-request-branch-created-from-a-fork) to make review process faster. Note that this option is not available for repositories that are owned by Github organizations.

### Tests
- [ ] Run the tests with `pnpm test:ci`.

### Documentation
- [ ] If you introduce new functionality, document it. You can run documentation with `pnpm run docs` command.

### Changesets
- [ ] Changes in changelog are generated from PR name. Please, make sure that it explains your changes in an understandable manner. Please, prefix changeset messages with `feat:`, `fix:`, `perf:`, `docs:`, or `chore:`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
