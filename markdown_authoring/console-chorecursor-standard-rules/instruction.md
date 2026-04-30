# chore(cursor): standard rules

Source: [Qovery/console#2039](https://github.com/Qovery/console/pull/2039)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/development-commands.mdc`
- `.cursor/rules/naming-conventions.mdc`
- `.cursor/rules/pre-commit-workflow.mdc`
- `.cursor/rules/project-architecture.mdc`
- `.cursor/rules/react-typescript-standards.mdc`
- `.cursor/rules/styling-standards.mdc`
- `.cursor/rules/testing-standards.mdc`

## What to add / change

# What does this PR do?

This pull request introduces a comprehensive set of documentation files describing coding standards, workflows, and architecture for the Qovery Console project. These new `.cursor/rules/*.mdc` files provide clear guidelines for development practices, naming conventions, testing, styling, and project structure, supporting consistency and quality across the codebase.

**Project Architecture & Structure:**

* Added `project-architecture.mdc` outlining Nx monorepo structure, directory organization, and rules for using apps/libs, React, TailwindCSS, and more.

**Development Workflow & Quality:**

* Added `development-commands.mdc` with daily development commands, Nx usage, package management, git workflow, and environment setup instructions.
* Added `pre-commit-workflow.mdc` detailing required pre-commit checks, including formatting, tests, linting, and snapshot verification, plus a sample script and quality standards.

**Coding Standards:**

* Added `naming-conventions.mdc` specifying file, variable, and component naming rules, as well as commenting guidelines.
* Added `react-typescript-standards.mdc` describing import rules, React component patterns, state management, and performance tips for TypeScript projects.
* Added `styling-standards.mdc` with TailwindCSS usage, component styling, responsive design, and accessibility requirements.
* Added `testing-standards.mdc` covering test setup, structure, mocking, and coverage expectations fo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
