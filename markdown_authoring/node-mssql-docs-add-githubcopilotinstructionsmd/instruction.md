# docs: add .github/copilot-instructions.md

Source: [tediousjs/node-mssql#1844](https://github.com/tediousjs/node-mssql/pull/1844)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds a `.github/copilot-instructions.md` file to help Copilot sessions work effectively in this repository.

## What's included

- **Build, test, and lint commands** — including how to run a single test
- **Architecture overview** — the base-class/driver-implementation pattern, entry points, and key modules
- **Coding conventions** — private method naming, dual Promise/callback API, StandardJS, streaming patterns
- **Commit message rules** — detailed Conventional Commits breakdown with release triggers
- **Merge strategy** — merge commits, rebase to update, all changes via PRs
- **Test patterns** — Mocha + assert, factory pattern for integration tests, three execution styles

Conventions were aligned with the sibling `tediousjs/setup-sqlserver` repository.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
