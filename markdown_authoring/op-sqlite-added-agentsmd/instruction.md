# added AGENTS.md

Source: [OP-Engineering/op-sqlite#323](https://github.com/OP-Engineering/op-sqlite/pull/323)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This pull request adds a new `AGENTS.md` documentation file that outlines repository guidelines for project structure, build and test commands, coding style, testing practices, commit conventions, and architecture notes. This will help contributors quickly understand how to work with the codebase and maintain consistency.

Documentation improvements:

* Added `AGENTS.md` with detailed guidelines on project structure, module organization, and file layout to clarify where code and assets should reside.
* Documented build, test, and development commands, including prerequisites and steps for running the example app on iOS and Android.
* Specified coding style and naming conventions for TypeScript, C/C++, Kotlin, and Objective‑C(++), including formatting requirements and enforcement tools.
* Provided testing guidelines, emphasizing validation through the example app and type checking, and noted the absence of Jest tests.
* Outlined commit and pull request standards, including message formatting, hygiene requirements, and PR content expectations.
* Included architecture notes explaining the JSI TurboModule structure and feature flag configuration for the demo app.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
