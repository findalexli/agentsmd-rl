# chore: add CLAUDE.md

Source: [whoami-wiki/whoami#41](https://github.com/whoami-wiki/whoami/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
Added a new `CLAUDE.md` file documenting the commit message guidelines for this project, establishing standards for conventional commits across the codebase.

## Changes
- Created `CLAUDE.md` with comprehensive commit message guidelines
- Documented the Conventional Commits format used by the project
- Defined four commit types: `feat`, `fix`, `chore`, and `release`
- Established six formatting rules including lowercase, imperative mood, and character limits
- Provided examples of properly formatted commit messages for reference
- Included special formatting rules for release commits with product name and semver version

## Details
This document serves as a reference for contributors to maintain consistent commit message formatting across the project. It follows the [Conventional Commits](https://www.conventionalcommits.org/) specification and includes practical examples to guide developers in writing clear, standardized commit messages.

https://claude.ai/code/session_015rEfz3oXvAbNZy7cSx1Rzf

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
