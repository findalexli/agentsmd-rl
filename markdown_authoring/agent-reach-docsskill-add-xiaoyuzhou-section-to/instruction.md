# docs(skill): add 小宇宙播客 (Xiaoyuzhou) section to SKILL.md

Source: [Panniantong/Agent-Reach#158](https://github.com/Panniantong/Agent-Reach/pull/158)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

## Problem

Fixes #156. XiaoyuzhouChannel (groq-whisper + ffmpeg podcast transcription) was implemented in the codebase (`agent_reach/channels/xiaoyuzhou.py`) but completely absent from `SKILL.md`. Agents had no way to know this channel existed.

## Changes

- **Description**: platform count 15 → 16, add Xiaoyuzhou to platform list
- **Triggers**: add `小宇宙`, `xiaoyuzhou`, `播客`, `podcast`, `转录`, `transcribe` as trigger keywords
- **New section**: `## 小宇宙播客 / Xiaoyuzhou Podcast` with:
  - Correct `transcribe.sh` invocation
  - Prerequisites (ffmpeg + Groq API Key)
  - Setup instructions (`agent-reach configure groq-key`, `agent-reach install --env=auto`)

## Verification

- Confirmed `agent_reach/channels/xiaoyuzhou.py` exists and is Tier 1 (groq-whisper + ffmpeg)
- Confirmed `agent-reach read` CLI command does NOT exist (avoiding doc/reality mismatch)
- Used `transcribe.sh` path which is what `check()` validates
- `agent-reach doctor` correctly reports channel status

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
