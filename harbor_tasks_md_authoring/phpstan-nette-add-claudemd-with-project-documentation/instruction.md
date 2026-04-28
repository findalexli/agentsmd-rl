# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-nette#187](https://github.com/phpstan/phpstan-nette/pull/187)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a `CLAUDE.md` file to the repository root with comprehensive project documentation for AI assistants
- Covers project purpose (PHPStan extension for Nette Framework), PHP 7.4+ version support, Nette multi-version compatibility, repository structure, extension types (dynamic return types, class reflection, rules, stubs), build commands, testing patterns, CI pipeline, and development guidelines
- Created by examining README, composer.json, extension/rules neon configs, Makefile, CI workflow, source code structure, and test patterns

## Test plan
- [ ] Verify CLAUDE.md content is accurate and comprehensive
- [ ] Confirm no existing files were modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
