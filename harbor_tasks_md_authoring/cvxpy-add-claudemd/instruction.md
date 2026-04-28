# Add CLAUDE.md

Source: [cvxpy/cvxpy#3098](https://github.com/cvxpy/cvxpy/pull/3098)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Description
Since we have more people making commits with claude code we should have a shared CLAUDE.md. This is a first attempt but can definitely be improved.

## Type of change
- [ ] New feature (backwards compatible)
- [ ] New feature (breaking API changes)
- [ ] Bug fix
- [x] Other (Documentation, CI, ...)

## [Contribution checklist](https://www.cvxpy.org/contributing/index.html#contribution-checklist)
- [ ] Add our license to new files.
- [ ] Check that your code adheres to our coding style.
- [ ] Write unittests.
- [ ] Run the unittests and check that they’re passing.
- [ ] Run the benchmarks to make sure your change doesn’t introduce a regression.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
