# Expansion of `agents.md` with detailed documentation for all available agents, usage guides, and best practices.

Source: [aliasrobotics/cai#299](https://github.com/aliasrobotics/cai/pull/299)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/agents.md`

## What to add / change

## 📋 Description

Comprehensive expansion of `agents.md` with detailed documentation for all available agents, usage guides, and best practices.

## ✨ Changes

- Add complete table of 12 of main available agents with descriptions, use cases, and key tools
- Add agent capabilities matrix with visual star ratings
- Add 3 multi-agent workflow scenarios (Web Pentest, IoT Assessment, Incident Response)
- Add agent-specific configuration guides (Red Team, Bug Bounty, DFIR)
- Add best practices section with 5 practical examples
- Improve document structure and formatting

## 📊 Stats

- **Lines added**: +206
- **Lines removed**: -13
- **Total lines**: ~340 (from ~150)

## ✅ Checklist

- [x] Documentation is clear and comprehensive
- [x] Code examples are tested and working
- [x] Formatting is consistent
- [x] No linting errors
- [x] Links are valid

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
