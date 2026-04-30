# feat: review and optimize Claude configuration, agents, and skills

Source: [AztecProtocol/aztec-packages#20270](https://github.com/AztecProtocol/aztec-packages/pull/20270)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/analyze-logs.md`
- `.claude/agents/identify-ci-failures.md`
- `.claude/skills/ci-logs/SKILL.md`
- `.claude/skills/noir-sync-update/SKILL.md`
- `.claude/skills/updating-changelog/SKILL.md`
- `yarn-project/.claude/skills/debug-e2e/SKILL.md`
- `yarn-project/.claude/skills/fix-pr/SKILL.md`
- `yarn-project/.claude/skills/rebase-pr/SKILL.md`
- `yarn-project/.claude/skills/worktree-spawn/SKILL.md`
- `yarn-project/CLAUDE.md`

## What to add / change

- Have claude opus 4.6 go through and apply 'best practices'
- Add nuance around when to squash/amend

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
