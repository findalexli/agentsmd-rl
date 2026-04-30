# Add CLAUDE.md with project documentation

Source: [phpstan/phpstan-mockery#87](https://github.com/phpstan/phpstan-mockery/pull/87)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add `CLAUDE.md` file with comprehensive project documentation
- Covers project goal (PHPStan extension for Mockery mock type inference), repository structure, PHP 7.4+ version support, development commands, coding standard, testing approach, PHPStan extension architecture, and CI setup

## Test plan
- [ ] Verify CLAUDE.md content is accurate and complete
- [ ] Verify no other files were modified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
