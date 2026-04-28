# add AGENTS.md

Source: [cubicdaiya/nginx-build#232](https://github.com/cubicdaiya/nginx-build/pull/232)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds a comprehensive set of repository guidelines to the `AGENTS.md` documentation. The new section provides clear instructions on project structure, build and test commands, coding style, testing practices, commit standards, and CI/security considerations, making it easier for contributors to follow best practices.

Documentation improvements:

* Added a new "Repository Guidelines" section to `AGENTS.md`, detailing project structure, module organization, and directory usage for CLI entrypoints, helpers, integrations, configs, tests, and assets.
* Included instructions for build, test, and development commands, covering compilation, validation, formatting, and cleaning workflows.
* Specified coding style and naming conventions for Go code, CLI flags, and module paths to ensure consistency and maintainability.
* Outlined testing guidelines, including preferred test structure, naming, and documentation of edge cases.
* Provided commit and pull request standards, CI triggers, and security notes to support reliable and secure contributions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
