# Add refactor skill

Source: [unkeyed/unkey#5912](https://github.com/unkeyed/unkey/pull/5912)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/refactor/SKILL.md`

## What to add / change

## What does this PR do?

Adds a refactor skill which helps with removing dead code and tightening up your branch before pushing for review.


<!-- Please mark the relevant points by using [x] -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] Chore (refactoring code, technical debt, workflow improvements)
- [ ] Enhancement (small improvements)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] This change requires a documentation update

## How should this be tested?

<!-- Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration -->

- Run it against a branch you want to commit, see if it helps clean it up!

## Checklist

<!-- We're starting to get more and more contributions. Please help us making this efficient for all of us and go through this checklist. Please tick off what you did  -->

### Required

- [ ] Filled out the "How to test" section in this PR
- [ ] Read [Contributing Guide](./CONTRIBUTING.md)
- [ ] Self-reviewed my own code
- [ ] Commented on my code in hard-to-understand areas
- [ ] Ran `pnpm build`
- [ ] Ran `pnpm fmt`
- [ ] Ran `make fmt` on `/go` directory
- [ ] Checked for warnings, there are none
- [ ] Removed all `console.logs`
- [ ] Merged the latest changes from main

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
