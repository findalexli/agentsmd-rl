# chore: improve CLAUDE.md and add Claude Code skills

Source: [devoxx/DevoxxGenieIDEAPlugin#851](https://github.com/devoxx/DevoxxGenieIDEAPlugin/pull/851)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr/SKILL.md`
- `.claude/skills/release/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Reformatted CLAUDE.md with consistent line wrapping and blank lines between markdown sections for better readability
- Added "Best Practices" section covering EDT constraints, workflow rules, git workflow, testing, and release process guidelines
- Added GitHub issue investigation workflow instructions
- Added Claude Code skill definitions:
  - **PR skill** (`.claude/skills/pr/SKILL.md`) - automated PR creation workflow
  - **Release skill** (`.claude/skills/release/SKILL.md`) - version bump and release workflow

## Test plan
- [x] Build passes (`./gradlew build`)
- [x] All tests pass
- [ ] Verify CLAUDE.md renders correctly on GitHub

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
