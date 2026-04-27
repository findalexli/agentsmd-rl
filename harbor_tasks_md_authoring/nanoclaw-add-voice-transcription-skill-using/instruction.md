# Add voice transcription skill using OpenAI Whisper API

Source: [qwibitai/nanoclaw#77](https://github.com/qwibitai/nanoclaw/pull/77)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-voice-transcription/SKILL.md`

## What to add / change

## Summary

New skill `/add-voice-transcription` that guides users through adding automatic voice message transcription to NanoClaw using OpenAI's Whisper API.

## Features

- **OpenAI Whisper integration** - Transcribes WhatsApp voice notes (~$0.006/min of audio)
- **Provider-agnostic architecture** - Switch statement design supports future providers (Groq, Deepgram, local Whisper)
- **Secure API key storage** - Config file automatically added to `.gitignore`
- **Graceful degradation** - Fallback message when transcription unavailable
- **Database integration** - Voice messages stored as `[Voice: <transcript>]`

## Skill Contents

| Section | Description |
|---------|-------------|
| Prerequisites | OpenAI API key setup with cost estimate |
| Implementation | 8-step guide: dependency, config, module, db, handler, build, restart, test |
| Configuration | Enable/disable, fallback message, provider switching |
| Troubleshooting | Common errors, ES module fixes, dependency conflicts |
| Security Notes | API key handling, data privacy considerations |
| Cost Management | Usage monitoring, spending limits, typical costs |
| Removal | Complete uninstall instructions |

## UX Consistency

- Includes `AskUserQuestion` tool guidance (consistent with updated `/setup` skill)
- Documents trigger word behavior for voice messages

## Test plan

- [ ] Run `/add-voice-transcription` skill
- [ ] Verify step-by-step guidance is clear
- [ ] Verify `AskUserQuestion` prompts appear at prerequisit

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
