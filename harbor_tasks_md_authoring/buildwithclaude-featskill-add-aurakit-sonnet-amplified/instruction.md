# feat(skill): add AuraKit — Sonnet Amplified fullstack engine

Source: [davepoon/buildwithclaude#88](https://github.com/davepoon/buildwithclaude/pull/88)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/aurakit/SKILL.md`

## What to add / change

## New Skill: AuraKit

Adds `plugins/all-skills/skills/aurakit/SKILL.md`

**npm**: `npx @smorky85/aurakit`
**GitHub**: https://github.com/smorky850612/Aurakit

### What it does

AuraKit is a Sonnet Amplified fullstack engine. Single `/aura` command activates 34 modes with:

- **Sonnet Amplifier** — 5-step forced reasoning for Opus-level code quality
- **SEC-01~15** — OWASP Top 10 complete inline security (15 rules + 13 runtime hooks)
- **Tiered Model** — ECO/PRO/MAX with automatic model selection
- **75% Token Reduction** — Verified measurement
- **10 Language Reviewers** + **5 Framework Patterns**
- **Instinct Learning Engine** — Project patterns auto-saved across sessions
- **8-Language UI** — KO, EN, JA, ZH, ES, FR, DE, IT

### Checklist
- [x] Single SKILL.md file in `plugins/all-skills/skills/aurakit/`
- [x] Follows existing directory convention
- [x] Includes install instructions
- [x] Clear description and usage examples

Resolves #85

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
