# docs: Added CLAUDE.md

Source: [IJHack/QtPass#1089](https://github.com/IJHack/QtPass/pull/1089)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

<!-- kody-pr-summary:start -->
docs: Add `CLAUDE.md`

This pull request introduces a new documentation file, `CLAUDE.md`, to the repository. This file is designed to provide comprehensive guidance to AI models, specifically Claude Code, when working with the QtPass codebase.

The `CLAUDE.md` file includes:
- An overview of QtPass and its purpose.
- Detailed instructions for building the project, running tests, and generating code coverage.
- Information on the Qt Test framework, including how to execute specific tests and functions.
- Guidelines for linting and formatting C++ and Markdown/YAML files.
- An explanation of the project's architecture, including its two-mode design (RealPass/ImitatePass), core classes, and signal/slot flow.
- Key coding conventions and best practices.
- Details on the localization process and translation files.
- A list of specialized skills for common development workflows within the project.
<!-- kody-pr-summary:end -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added a new repository-root developer guide with project overview and supported platforms; concrete build, test and coverage commands; test execution options; local formatting and lint workflows; architecture overview of the two-mode design and command queue flow; Doxygen and localization guidance; coding conventions and quick-reference developer workflows.
<!-- end of auto-generated comment: release notes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
