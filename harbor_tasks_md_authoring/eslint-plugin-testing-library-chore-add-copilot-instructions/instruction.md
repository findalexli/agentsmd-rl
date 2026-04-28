# chore: add copilot instructions

Source: [testing-library/eslint-plugin-testing-library#1135](https://github.com/testing-library/eslint-plugin-testing-library/pull/1135)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Checks

- [x] I have read the [contributing guidelines](https://github.com/testing-library/eslint-plugin-testing-library/blob/main/CONTRIBUTING.md).

## Changes

- Added `.github/copilot-instructions.md` with comprehensive repository onboarding documentation

## Context

Provides GitHub Copilot coding agents with essential information to work efficiently on the repository. Covers:

- **Tech Stack**: TypeScript, pnpm (via corepack), Vitest, tsdown, ESLint v9 flat config
- **Prerequisites**: Node.js versions referenced from `.nvmrc` and `package.json`, pnpm setup via corepack instead of global install
- **Build Workflow**: Tested command sequences with timing (build ~2s, tests ~40s, full validation ~10s)
- **Project Structure**: 30 rules in `src/rules/`, 7 configs, custom `createTestingLibraryRule` usage
- **CI/CD**: Test matrix (Node 18-23 × ESLint 8-9), 90% coverage threshold, 3min timeout
- **Git Hooks**: Pre-commit lint-staged, commit-msg Conventional Commits validation
- **Troubleshooting**: Common failures (pnpm missing via corepack, validation errors, type check issues)
- **Command Reference**: Quick-lookup table of all scripts with timing and notes

File length: ~2 pages (287 lines). All commands verified. Version numbers reference `package.json` fields for maintainability (pnpm version from `packageManager` field, Node.js versions from `engines.node`). Uses `corepack enable pnpm` instead of global npm install to automatically use the correct pnpm version.

Key for a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
