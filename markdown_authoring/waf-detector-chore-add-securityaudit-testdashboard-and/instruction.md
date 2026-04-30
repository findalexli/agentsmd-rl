# chore: add security-audit, test-dashboard, and validate-build skills

Source: [ammarion/waf-detector#36](https://github.com/ammarion/waf-detector/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/security-audit.md`
- `.claude/skills/test-dashboard.md`
- `.claude/skills/validate-build.md`

## What to add / change

## Summary
- Adds 3 Claude Code agent skills: `security-audit`, `test-dashboard`, `validate-build`
- These complement the existing `waf-assess` skill for project automation

## Test plan
- [x] Skills are valid markdown with correct frontmatter
- [ ] Verify skills load in Claude Code session

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
