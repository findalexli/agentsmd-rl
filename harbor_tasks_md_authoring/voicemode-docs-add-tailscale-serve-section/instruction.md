# docs: add Tailscale serve section to VoiceMode skill

Source: [mbailey/voicemode#280](https://github.com/mbailey/voicemode/pull/280)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/voicemode/SKILL.md`

## What to add / change

## Summary
- Added "Sharing Voice Services Over Tailscale" section to VoiceMode skill
- Documents `tailscale serve --set-path` setup for Kokoro TTS and Whisper STT
- Includes important notes about path mapping, same-machine testing, and CORS
- Based on working configuration documented in VMD-40

## Test plan
- [x] Verified Tailscale serve with ms2 works for VoiceMode Connect calls
- [x] Skill content matches VMD-40 documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
