# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-deprecation-rules#175](https://github.com/phpstan/phpstan-deprecation-rules/pull/175)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Adds a comprehensive `CLAUDE.md` file documenting the project for AI-assisted development
- Covers project overview, repository structure, PHP 7.4+ compatibility requirements, development commands (Makefile targets), testing patterns, architecture (rules, restricted usage extensions, deprecated scope resolution), CI pipeline, branch strategy, and code style conventions

## Test plan
- [x] Verified the file accurately reflects the repository structure, configuration, and conventions
- [x] No code changes — documentation only

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
