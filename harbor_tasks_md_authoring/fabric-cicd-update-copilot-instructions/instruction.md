# Update copilot instructions

Source: [microsoft/fabric-cicd#886](https://github.com/microsoft/fabric-cicd/pull/886)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

This pull request significantly restructures and expands the `.github/copilot-instructions.md` documentation to provide a clearer, more actionable guide for developers working with the `fabric-cicd` Python library. The changes focus on improving quick-start usability, clarifying authentication requirements, introducing configuration-based deployment, and outlining development/testing best practices.

Key documentation improvements:

**Quick Start & Validation:**
- Replaces the verbose setup and validation sections with a concise "Quick Command Reference" table, listing essential commands, timeouts, and mandatory validation steps for development and CI.

**Authentication Guidance:**
- Clearly explains authentication requirements, emphasizing explicit use of the `token_credential` parameter, and provides concrete examples for local development, CI/CD, and testing scenarios.

**Deployment Methods & Project Structure:**
- Adds a new section on config-based deployment using `deploy_with_config()`, including references to implementation files and tests.
- Restores and updates the project structure diagram for easier navigation.

**Development & Testing Guidelines:**
- Details core development patterns, publisher class structure, serial publishing, parameterization, and best practices for adding features or tests.
- Outlines testing strategies, types of tests, and use of mocks for external dependencies.

**Pull Request & Troubleshooting Standards:**
- Specifies st

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
