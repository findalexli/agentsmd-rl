# chore: update agents.md

Source: [atuinsh/atuin#3126](https://github.com/atuinsh/atuin/pull/3126)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- Thank you for making a PR! Bug fixes are always welcome, but if you're adding a new feature or changing an existing one, we'd really appreciate if you open an issue, post on the forum, or drop in on Discord -->

## Checks
- [ ] I am happy for maintainers to push small adjustments to this PR, to speed up the review cycle
- [ ] I have checked that there are no existing pull requests for the same thing

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
