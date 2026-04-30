# Add and update AI coding skills

Source: [wix/react-native-navigation#8246](https://github.com/wix/react-native-navigation/pull/8246)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/rn-version-upgrade.md`

## What to add / change

## Summary

- Add RNN codebase navigation skill (`.claude/skills/rnn-codebase/SKILL.md` + copies for Cursor/GitHub)
- Add RN version upgrade skill (`.claude/skills/rn-version-upgrade.md`)
- Update upgrade skill with lessons from RN 0.84:
  - Prefer `__has_include` for conditional imports (forward-compatible)
  - Use `#ifndef RCT_REMOVE_LEGACY_ARCH` for legacy code blocks (RN 0.84+)
  - Added "Research Before Fixing" phase: investigate better approaches from the target RN version before pattern-matching on existing code
  - New pitfall: don't blindly follow existing codebase patterns when better alternatives exist

## Test plan

- [ ] Verify skill files are well-formed markdown
- [ ] Verify no non-skill files are included in this PR

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
