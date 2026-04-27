# docs(packages): add CLAUDE.md and AGENTS.md to internal and terminal packages

Source: [ryoppippi/ccusage#649](https://github.com/ryoppippi/ccusage/pull/649)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/internal/AGENTS.md`
- `packages/terminal/AGENTS.md`
- `packages/terminal/CLAUDE.md`

## What to add / change

## Summary

- Added comprehensive CLAUDE.md documentation files to `packages/internal` and `packages/terminal`
- Added AGENTS.md as symlinks to CLAUDE.md following the established pattern from apps/ directories
- Ensures consistency across all packages in the monorepo with standardized documentation structure

## What Changed

- **packages/internal/CLAUDE.md**: Complete documentation for the internal utilities package including:
  - Package overview with name, description, and type
  - Development commands for testing, linting, and building
  - Architecture details covering key modules (pricing.ts, pricing-fetch-utils.ts)
  - Dependencies documentation (runtime and dev dependencies)
  - Testing guidelines with in-source testing patterns
  - Code style guidelines following project conventions
  
- **packages/terminal/CLAUDE.md**: Complete documentation for the terminal utilities package including:
  - Package overview for terminal utilities
  - Development commands and workflow
  - Architecture details covering key modules (table.ts, utils.ts)
  - Dependencies for terminal functionality (cli-table3, picocolors, etc.)
  - Testing and code style guidelines

- **AGENTS.md symlinks**: Added in both packages pointing to CLAUDE.md following the monorepo pattern

## Why

This change ensures documentation consistency across the entire monorepo. Previously, only the apps/ directories had CLAUDE.md files, but the packages/ also needed comprehensive documentation for:

1. **Developer Exp

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
