# Add writing-unit-tests and api-reviewer skills, update AGENTS.md

Source: [mitchdenny/hex1b#108](https://github.com/mitchdenny/hex1b/pull/108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/api-reviewer/SKILL.md`
- `.github/skills/writing-unit-tests/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

This PR adds two new skills and updates AGENTS.md to be more concise by pointing to skills for detailed guidance.

### New Skills

**writing-unit-tests** - Guidelines for writing unit tests:
- Prefer full `Hex1bTerminal.CreateBuilder()` stack
- Use `.WithHex1bApp()` for TUI functionality
- Input sequencing and visual assertion patterns
- Widget test dimensions (terminal size, containers, theming)
- Anti-patterns including partial render timing issues

**api-reviewer** - API design preferences:
- Public vs internal decision framework
- Builder pattern (`With...()`) vs widget pattern (minimal constructor + fluent extensions)
- Task vs ValueTask guidance
- Documentation standards (complete runnable examples)
- Code organization (one type per file, avoid statics)

### AGENTS.md Updates

- Added "Available Skills" section listing all 8 skills
- Simplified Aspire section (was ~65 lines, now ~15 with pointer to aspire skill)
- Added skill pointers for widget creation and testing
- Reduced from 272 to 243 lines while adding useful content

### Skills Now Available

| Skill | Purpose |
|-------|---------|
| widget-creator | Creating new widgets |
| writing-unit-tests | Writing unit tests |
| test-fixer | Diagnosing flaky tests |
| api-reviewer | Reviewing API design |
| doc-writer | Writing documentation |
| doc-tester | Validating documentation |
| surface-benchmarker | Performance benchmarks |
| aspire | .NET Aspire workflows |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
