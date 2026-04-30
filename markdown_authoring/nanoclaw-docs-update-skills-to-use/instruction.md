# docs: update skills to use Docker commands

Source: [qwibitai/nanoclaw#325](https://github.com/qwibitai/nanoclaw/pull/325)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-discord/modify/src/index.ts.intent.md`
- `.claude/skills/add-parallel/SKILL.md`
- `.claude/skills/add-telegram/modify/src/index.ts.intent.md`
- `.claude/skills/add-voice-transcription/SKILL.md`
- `.claude/skills/debug/SKILL.md`
- `.claude/skills/setup/SKILL.md`
- `.claude/skills/x-integration/SKILL.md`

## What to add / change

## Summary
- Updated 7 skill files to replace Apple Container CLI commands with Docker equivalents
- Setup skill now defaults to Docker, with optional `/convert-to-apple-container` for macOS users
- Debug skill commands use `docker ps/images/info` instead of `container ls/system status`
- Voice transcription and X integration skills use `docker` build/run commands
- Intent files for add-discord and add-telegram updated to say "Container runtime check" instead of "Apple Container check"

## Test plan
- [x] `npm run build` passes
- [x] Grep for remaining `Apple Container` references — only in `convert-to-docker/` (deleted in PR #324) and one intentional reference in setup skill

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
