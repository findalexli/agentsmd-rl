# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-webmozart-assert#200](https://github.com/phpstan/phpstan-webmozart-assert/pull/200)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a `CLAUDE.md` file documenting the project goal, structure, and development workflows
- Covers PHP 7.4+ compatibility requirement and webmozart/assert version support
- Documents all Makefile commands, the extension architecture, testing approach, coding style, and CI setup

## Test plan
- [x] Verify the file accurately reflects the repository structure and configuration
- [x] Confirm PHP version requirements match `composer.json` (PHP 7.4+)
- [x] Confirm library version support matches `composer.json` (webmozart/assert ^1.11.0 || ^2.0)
- [x] Confirm CI matrix matches `.github/workflows/build.yml`
- [x] Confirm development commands match `Makefile`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
