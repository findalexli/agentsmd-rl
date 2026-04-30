# fix: document Sprite vs normal VM paths in SKILL.md

Source: [OpenRouterTeam/spawn#1196](https://github.com/OpenRouterTeam/spawn/pull/1196)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/SKILL.md`

## What to add / change

## Summary

- Add environment guide: Sprite VMs drop users in `/home/sprite/`, normal VMs in `/root/`
- Replace all hardcoded `/root/spawn` paths with `<REPO_ROOT>` placeholders
- Instruct agents to **ask the user** for the repo path instead of guessing
- Explicitly ban inventing directories like `/home/claude-runner/`
- Update systemd and wrapper script templates with environment-aware placeholders

## Context

The trigger server was previously configured to run from `/home/claude-runner/spawn` — a path that was invented by an agent. This caused 401 auth failures when the systemd service auto-restarted because it loaded different secrets than what GitHub Actions expected. The fix is to never guess paths and always ask.

## Test plan

- [x] Verify SKILL.md renders correctly
- [ ] Next `setup-agent-team` invocation should ask for repo path instead of assuming

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
