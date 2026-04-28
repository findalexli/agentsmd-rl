# [AI] Add AGENTS.md to provide extra context

Source: [Skyscanner/backpack#3954](https://github.com/Skyscanner/backpack/pull/3954)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds a comprehensive guide for AI agents contributing to the Backpack Design System. The new `AGENTS.md` file provides an overview of the project, codebase structure, development standards, and best practices to help maintain consistency and quality across contributions.

Documentation and onboarding:

* Added `AGENTS.md` with a detailed project overview, including repository structure, technology stack, and component organization to help new contributors understand the codebase.
* Documented key architecture patterns, file naming conventions, and development guidelines for TypeScript, SCSS, and React component implementation.
* Provided instructions for using design tokens, typography mixins, and SCSS best practices, including sample code snippets and component examples.
* Outlined common development workflows, accessibility standards, testing strategies, and troubleshooting tips for common issues.
* Included references for integration with external tools (e.g., Figma), package publishing, and links to further documentation and decision records.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
