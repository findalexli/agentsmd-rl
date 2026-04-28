# [ci] Updating Copilot Instructions

Source: [nanvix/nanvix#1139](https://github.com/nanvix/nanvix/pull/1139)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This pull request significantly expands and clarifies the project's contributor documentation in `.github/copilot-instructions.md`. It introduces detailed sections on the repository structure, build and test workflows, coding standards, and review guidelines, with language-specific best practices for Rust, C/C++, Python, and shell scripts. The changes are aimed at improving onboarding, code quality, and consistency for all contributors.

Key documentation and standards updates:

**Repository structure and build/test workflow:**
- Expanded descriptions of the repository and source code structure, including detailed breakdowns of directories and their purposes. Added explicit lists of supported runtimes, development tools, and libraries.
- Introduced comprehensive instructions for building, formatting, linting, spell checking, and testing using the `z` utility script, with examples for Docker and local toolchains. Added sections on benchmarking and running the CI/CD pipeline locally.

**Coding standards and style guides:**
- Greatly enhanced coding standards, adding language-specific style and formatting rules for Rust, C/C++, Python, and shell scripts. Included requirements for error handling, log formatting, module organization, and copyright headers. [[1]](diffhunk://#diff-227c2c26cb2ee0ce0f46a320fc48fbcbdf21801a57f59161b1d0861e8aad55f5L17-R229) [[2]](diffhunk://#diff-227c2c26cb2ee0ce0f46a320fc48fbcbdf21801a57f59161b1d0861e8aad55f5R238-R278)
- Expanded documentatio

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
