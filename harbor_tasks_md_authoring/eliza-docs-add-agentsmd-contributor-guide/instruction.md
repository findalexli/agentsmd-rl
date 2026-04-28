# docs: add AGENTS.md contributor guide

Source: [elizaOS/eliza#5898](https://github.com/elizaOS/eliza/pull/5898)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This pull request adds comprehensive repository guidelines to the documentation, outlining project structure, development workflows, coding standards, testing practices, and security protocols. These guidelines are intended to help contributors navigate the monorepo, maintain code quality, and follow best practices.

Documentation improvements:

* Added a new section to `AGENTS.md` detailing the monorepo structure, including package organization and folder conventions.
* Provided step-by-step instructions for build, test, and development commands using Bun, Turbo, and Lerna, clarifying usage for each package and the overall repo.
* Defined coding style, naming conventions, and formatting/linting requirements, including Prettier and ESLint usage.
* Outlined testing guidelines for both backend and frontend, specifying test runners and coverage requirements.
* Added commit and pull request standards, including conventional commit messages, PR requirements, and documentation update expectations.Adds a concise, repo-specific contributor guide covering structure, build/test, style, testing, PR standards, and security/config. Resolves missing contributor guidance.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
