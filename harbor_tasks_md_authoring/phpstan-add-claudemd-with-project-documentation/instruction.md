# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan#14162](https://github.com/phpstan/phpstan/pull/14162)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Add `CLAUDE.md` to the repository root with comprehensive documentation about the project structure, development workflow, and conventions
- Covers the distribution model (this repo vs phpstan-src), PHP version support, e2e testing, CI/CD pipelines, website, playground, Docker images, and related repositories
- Notes that phpstan-src is on PHP 8.1+ (downgraded for PHAR) while extension repositories still support PHP 7.4+

## Test plan

- [x] Verify the file contains accurate information about the repository structure
- [x] Verify PHP version requirements are correctly documented
- [x] Verify references to related repositories and workflows are accurate

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
