# Setup GitHub Copilot instructions for ioBroker.repositories

Source: [ioBroker/ioBroker.repositories#5075](https://github.com/ioBroker/ioBroker.repositories/pull/5075)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This PR adds comprehensive GitHub Copilot instructions to help developers and contributors understand and work with the ioBroker.repositories project more effectively.

## What was added

Created `.github/copilot-instructions.md` with detailed documentation covering:

- **Repository overview**: Explains the purpose of managing ioBroker adapter repositories (latest and stable)
- **Project structure**: Complete breakdown of directories, key files, and their functions
- **Development setup**: Prerequisites, installation steps, and available npm scripts
- **Code style and patterns**: ESLint configuration, coding conventions, and architectural patterns
- **Testing framework**: How to run tests, validation processes, and environment variables
- **GitHub Actions workflows**: Documentation of automated PR checking, validation, and deployment
- **Adapter requirements**: Detailed requirements for adding adapters to latest and stable repositories
- **Common tasks**: Examples of frequently performed operations with command-line examples
- **Troubleshooting**: Common issues and debugging tips for developers

## Key benefits

This will help GitHub Copilot provide more accurate and contextual assistance when:
- Adding new adapters to repositories
- Debugging validation failures
- Understanding the repository automation workflows
- Following established code patterns and conventions
- Navigating the complex project structure

The instructions follow GitHub's best practices for Copilot config

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
