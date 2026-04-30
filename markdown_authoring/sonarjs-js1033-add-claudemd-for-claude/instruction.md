# JS-1033 Add CLAUDE.md for Claude Code guidance

Source: [SonarSource/SonarJS#6161](https://github.com/SonarSource/SonarJS/pull/6161)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md to provide project-specific context for Claude Code
- Document project structure, build commands, rule implementation patterns
- Include testing patterns with the three RuleTesters (DefaultParserRuleTester, NoTypeCheckingRuleTester, RuleTester)
- Add code style guidelines and important notes

## Test plan
- [x] File follows project formatting (verified by pre-commit hook)
- [ ] Review content accuracy with team

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
