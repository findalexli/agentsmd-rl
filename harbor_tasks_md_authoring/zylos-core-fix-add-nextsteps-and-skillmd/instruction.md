# fix: add nextSteps and SKILL.md guidance to C4 install flow

Source: [zylos-ai/zylos-core#95](https://github.com/zylos-ai/zylos-core/pull/95)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/component-management/references/install.md`

## What to add / change

## Summary
- Add `skill.nextSteps` display to C4 mode post-install actions (was only in Session mode)
- Add instruction to read component SKILL.md for additional setup documentation

## Context
When installing lark via C4 mode (Lark/Telegram), Claude skipped showing webhook URL and verification token guidance because the C4 post-install actions didn't include `nextSteps`. Session mode Step 6 already had this, but C4 mode was missing it.

## Test plan
- [ ] Install a component with `nextSteps` via C4 mode — verify Claude shows the guidance
- [ ] Install a component without `nextSteps` — verify no change in behavior

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
