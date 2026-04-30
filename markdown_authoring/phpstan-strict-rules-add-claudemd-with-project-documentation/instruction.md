# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-strict-rules#299](https://github.com/phpstan/phpstan-strict-rules/pull/299)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a `CLAUDE.md` file documenting the project for AI-assisted development
- Covers project overview, PHP 7.4+ version constraints, repository structure, rule architecture, configuration system, development commands, testing patterns, CI pipeline, and coding standards
- Created by examining the full repository structure, README, composer.json, rules.neon, Makefile, CI workflows, source code patterns, and test patterns

## Test plan
- [ ] Verify the file renders correctly on GitHub
- [ ] Confirm all documented commands and paths are accurate

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
