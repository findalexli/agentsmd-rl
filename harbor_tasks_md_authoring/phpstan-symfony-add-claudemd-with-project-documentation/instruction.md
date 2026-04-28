# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-symfony#471](https://github.com/phpstan/phpstan-symfony/pull/471)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Adds a comprehensive `CLAUDE.md` file documenting the phpstan-symfony project for AI-assisted development
- Covers project overview, repository structure, PHP 7.4+ version requirements, Symfony version compatibility, development commands, testing patterns, CI pipeline, and key architectural concepts

## Contents

The documentation includes:
- **Project overview** and feature summary
- **Repository structure** with explanation of each directory's purpose
- **PHP version support** (7.4+) and Symfony version compatibility notes
- **Development commands** (`make check`, `make tests`, `make phpstan`, etc.)
- **Testing patterns** (RuleTestCase, TypeInferenceTestCase, conditional skipping)
- **CI pipeline** details (lint, CS, tests, PHPStan across PHP 7.4-8.5)
- **Key concepts** (ServiceMap, ParameterMap, ConsoleApplicationResolver, type extensions vs rules, stubs)

## Test plan

- [x] Verified the file accurately reflects the repository structure, configuration, and conventions
- [x] No code changes — documentation only

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
