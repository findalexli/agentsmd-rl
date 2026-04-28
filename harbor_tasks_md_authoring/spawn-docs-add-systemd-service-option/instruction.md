# docs: add systemd service option to SKILL.md

Source: [OpenRouterTeam/spawn#840](https://github.com/OpenRouterTeam/spawn/pull/840)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/SKILL.md`

## What to add / change

## Summary
- Add systemd as Option A for running the trigger server on standard Linux VMs
- Keep sprite-env as Option B for Sprite environments
- Add systemd troubleshooting entries (EADDRINUSE, restart loops)
- Update deployed services table with security service on sandbox VM

## Test plan
- [x] systemd service running and healthy on sandbox VM
- [x] `curl http://localhost:8080/health` returns ok

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
