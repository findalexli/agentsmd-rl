# Improve setup UX with AskUserQuestion tool and security education

Source: [qwibitai/nanoclaw#60](https://github.com/qwibitai/nanoclaw/pull/60)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup/SKILL.md`

## What to add / change

## Summary

- Add UX note instructing Claude to use `AskUserQuestion` tool for better interactive experience during setup
- Add new Section 7 explaining the main channel's elevated privileges (admin control portal) before registration
- Include interactive security acknowledgment with follow-up confirmation for users choosing shared groups
- Renumber subsequent sections (7→8, 8→9, 9→10)

## Changes

| Change | Description |
|--------|-------------|
| Line 10 | Added UX note about using `AskUserQuestion` tool |
| Section 7 | New section with security model education and interactive questions |
| Sections 8-10 | Renumbered from previous 7-9 |

## Test plan

- [ ] Run `/setup` on a fresh NanoClaw install
- [ ] Verify Claude uses the AskUserQuestion tool when asking questions
- [ ] Verify the security explanation appears before main channel registration
- [ ] Verify Claude asks follow-up if user selects "group with other people"
- [ ] Verify section numbers are correct throughout

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
