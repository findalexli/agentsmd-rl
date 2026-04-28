# feat: Add git worktree and commit marker conventions to SKILL.md

Source: [OpenRouterTeam/spawn#67](https://github.com/OpenRouterTeam/spawn/pull/67)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-trigger-service/SKILL.md`

## What to add / change

## Summary
- Adds a "Git Conventions for Agent Team Scripts" section to SKILL.md
- Documents the mandatory workflow: always `git pull origin main` before creating worktrees
- Documents worktree usage for parallel agent branch work
- Documents `Agent:` commit trailer requirement
- Documents worktree cleanup at end of cycle
- Ensures any new service scripts follow the same patterns as improve.sh and refactor.sh

## Test plan
- [x] SKILL.md renders correctly
- [x] Conventions match what's already in improve.sh and refactor.sh prompts

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
