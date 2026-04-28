# feat(skills): add skill-creator builtin skill

Source: [qhkm/zeptoclaw#45](https://github.com/qhkm/zeptoclaw/pull/45)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/skill-creator/SKILL.md`

## What to add / change

## Summary
- Adds a 6-step agent-guided skill authoring workflow adapted from OpenClaw's skill-creator
- Covers use-case gathering, content analysis, structure selection, scaffolding, writing with progressive disclosure, and validation
- Documents structural patterns (workflow, task-based, reference, capabilities) and freedom levels

## Test plan
- [ ] Verify SKILL.md loads correctly via `zeptoclaw skills list`
- [ ] Test skill-creator workflow end-to-end with `zeptoclaw skills create`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
