# Fix orphan container cleanup and update installation steps

Source: [qwibitai/nanoclaw#149](https://github.com/qwibitai/nanoclaw/pull/149)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-voice-transcription/SKILL.md`

## What to add / change

For the transcription skill - updated instructions for handling orphaned containers and Zod version conflicts. Added critical cleanup steps for the NanoClaw service.

## Type of Change

- [ ] **Skill** - adds a new skill in `.claude/skills/`
- [x] **Fix** - bug fix or security fix to source code
- [ ] **Simplification** - reduces or simplifies source code

## Description


## For Skills

- [x] I have not made any changes to source code
- [x] My skill contains instructions for Claude to follow (not pre-built code)
- [x] I tested this skill on a fresh clone

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
