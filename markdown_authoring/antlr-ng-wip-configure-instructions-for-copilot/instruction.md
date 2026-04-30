# [WIP] Configure instructions for Copilot in repository

Source: [antlr-ng/antlr-ng#82](https://github.com/antlr-ng/antlr-ng/pull/82)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

- [x] Create `.github/copilot-instructions.md` file with comprehensive repository-specific guidance
- [x] Include project overview and architecture details
- [x] Document code style requirements from ESLint config
- [x] Specify TypeScript configuration and patterns
- [x] Provide testing guidelines using Vitest
- [x] Document build and development workflow
- [x] Add target language generation information
- [x] Include naming conventions and best practices

## Summary

Created a comprehensive `.github/copilot-instructions.md` file that provides GitHub Copilot coding agents with essential information about the antlr-ng repository:

### Key sections included:
- **Project Overview**: Description of antlr-ng as a TypeScript-based parser generator supporting 10 target languages
- **Architecture**: Detailed directory structure and organization
- **Code Style and Standards**: Complete ESLint rules, TypeScript configuration, and naming conventions
- **Testing Guidelines**: Vitest framework usage and test patterns
- **Build and Development Workflow**: Commands for building, testing, and generating parsers
- **Common Tasks and Patterns**: Grammar handling, error reporting, code generation, ATN operations
- **Common Pitfalls**: Module imports, arrow functions, generated files, null checks
- **Target Language Support**: List of supported languages and extension guidelines
- **Unicode Support**: Information about Unicode 16 implementation
- **Documentation Standards**: JSDoc requirements fo

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
