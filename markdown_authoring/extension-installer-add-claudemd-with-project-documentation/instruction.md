# Add CLAUDE.md with project documentation

Source: [phpstan/extension-installer#100](https://github.com/phpstan/extension-installer/pull/100)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds `CLAUDE.md` with comprehensive documentation about the phpstan/extension-installer project
- Covers project purpose (automatic PHPStan extension registration via Composer plugin), architecture (`Plugin.php` event subscriber + `GeneratedConfig.php` generation), PHP 7.4+ version requirements, development commands (`make check/lint/cs/phpstan`), CI pipeline details, and contribution guidelines

## Context
Created in response to a request to add CLAUDE.md documentation for AI-assisted development context.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
